import http.client
import json
import websockets
import StockFighter.Utilities as Utils

class StockFighterApi:
    """Wrapper to use assorted Stock Fighter APIs over HTTP"""
    def __init__(self, apiKey, account, venue = "TESTEX", isDebug = False):
        self.apiKey = apiKey
        self.connection = None
        self.account = account
        self.venue = venue
        self.isDebug = isDebug

    def __del__(self):
        if self.connection != None:
            self.connection.close()

    def connect(self):
        host = "api.stockfighter.io"
        
        try:
            if self.connection != None:
                self.connection.close()
            self.connection = http.client.HTTPSConnection(host)
        except Exception:
            print("ERROR: Could not establish a connection to the server.")
    

    def isApiUp(self):
        resource = "/ob/api/heartbeat"
        result = Utils.Utilities.sendGet(self.connection, resource, self.isDebug)
        if result["ok"] == True:
            return True
        else:
            return False


    def isVenueUp(self):
        resource = "/ob/api/venues/{0}/heartbeat".format(self.venue)
        result = Utils.Utilities.sendGet(self.connection, resource, self.isDebug)
        if result["ok"] == True:
            return True
        else:
            return False


    def getStockList(self):
        if not self.isVenueUp():
            raise ConnectionError

        resource = "/ob/api/venues/{0}/stocks".format(self.venue)
        result = Utils.Utilities.sendGet(self.connection, resource, self.isDebug)

        if result["ok"] == True:
            return result["symbols"]
        else:
            return []


    def getOrderbook(self, stock):
        if not self.isVenueUp():
            raise ConnectionError

        resource = "/ob/api/venues/{0}/stocks/{1}".format(self.venue, stock)
        return Utils.Utilities.sendGet(self.connection, resource, self.isDebug)


    def getQuote(self, stock):
        if not self.isVenueUp():
            raise ConnectionError

        resource = "/ob/api/venues/{0}/stocks/{1}/quote".format(self.venue, stock)
        return Utils.Utilities.sendGet(self.connection, resource, self.isDebug)


    def getOrderIdStatus(self, stock, id):
        if not self.isVenueUp():
            raise ConnectionError

        resource = "/ob/api/venues/{0}/stocks/{1}/orders/{2}".format(self.venue, stock, id)
        result = Utils.Utilities.sendGet(self.connection, resource, self.isDebug)

        if result["ok"] == True:
            return result
        else:
            return None

    """
    Deletes an order matching the given stock and order ID if it exists and hasn't been filled or cancelled.
    """
    def deleteOrder(self, stock, id):
        if not self.isVenueUp():
            raise ConnectionError

        resource = "/ob/api/venues/{0}/stocks/{1}/orders/{2}/cancel".format(self.venue, stock, id)
        return Utils.Utilities.sendGet(self.connection, resource, self.isDebug)

    """
    Retrieves a list of orders that have been submitted by the connected account 
    for all stocks or for a specified one.
    """
    def getOrderStatus(self, stock = ""): #All stock orders are obtained if stock is not sent
        if not self.isVenueUp():
            raise ConnectionError

        resource = "/ob/api/venues/{0}/accounts/{1}".format(self.venue, self.account)

        if len(stock) > 0:
            resource += "/stocks/{0}/orders".format(stock)
        else:
            resource += "/orders"

        result = Utils.Utilities.sendGet(self.connection, resource, self.isDebug)

        if result["ok"] == True:
            return result["orders"]
        else:
            return []

    """
    Input: Takes in an order which is a dictionary consisting of:
        account
        venue
        stock
        price
        qty
        direction ("buy" or "sell")
        orderType ("limit", "market", "fill-or-kill", "immediate-or-cancel")

    Output: The result returned by the order request
    """
    def placeOrder(self, stock, qty, price, direction, orderType):
        if not self.isVenueUp():
            raise ConnectionError

        resource = "/ob/api/venues/{0}/stocks/{1}/orders".format(self.venue, stock)
        body = json.dumps({"account": self.account, "venue": self.venue, "stock": stock, \
                        "qty": qty, "price": price, "direction": direction.value, \
                        "orderType": orderType.value})
        
        try:
            header = {"X-Starfighter-Authorization": self.apiKey}
            result = Utils.Utilities.sendPost(self.connection, self.apiKey, resource, header, body, self.isDebug)

            if not (result["ok"] == True and result["account"] == self.account and \
            result["venue"] == self.venue and result["symbol"] == stock):
                print("ERROR: Unexpected order result ({0})".format(result))
                raise Exception()
            #might need to confirm order number uniqueness and/or verify uniqueness of timestamp
        except Exception:
            print("ERROR: Exception encountered or result invalid.")
            return {"ok": False}

        return result
