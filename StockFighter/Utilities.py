from StockFighter import StockFighterApi
import threading
from time import sleep
import statistics
import math
import json
from enum import Enum

class OrderDirection(Enum):
    BUY = "buy"
    SELL = "sell"

class OrderType(Enum):
    LIMIT = "limit"
    MARKET = "market"
    FILL_OR_KILL = "fill-or-kill"
    IMMEDIATE_OR_CANCEL = "immediate-or-cancel"

class Utilities:
    @staticmethod
    def sendPost(connection, apikey, resource, header, body, isDebug):
        if isDebug:
            print("POST {0} ({1})- ".format(resource, body))

        try: #"/ob/api/{0}".format(resource)
            connection.request("POST", resource, body, header)
            response = connection.getresponse()
        except Exception:
            print("Error sending POST.")
            raise Exception

        if isDebug:
            if response.status == 200:
                print("OK!")
            else:
                print("ERROR: {0} -> {1}".format(response.status, response.reason))

        return json.loads(response.read().decode("utf-8")) 

    @staticmethod
    def sendGet(connection, resource, isDebug):
        if isDebug:
            print("GET {0}".format(resource))

        #"/ob/api/{0}".format(resource)
        connection.request("GET", resource)
        response = connection.getresponse()

        if isDebug:
            if response.status == 200:
                print("OK!")
            else:
                print("ERROR: {0} -> {1}".format(response.status, response.reason))

        return json.loads(response.read().decode("utf-8")) #JSON data decoded to a dictionary

    def __init__(self):
        self.isRunning = False
        self.result = {}
        self.averageAsk = -1
        self.averageAskSize = -1
        self.averageBid = -1
        self.averageBidSize = -1
        self.targetPrice = -1
        self.maxTransactionQty = -1
        self.algorithmEnabled = True

    def getNumericalInput(self, fieldName, var):
        return int(input("Enter a {0}(Current: {1}): ".format(fieldName, var)))

    def controlPanel(self):
        commands = ["Target price", "Maximum transaction quantity", "Stop/Start algorithm"]
        #display averages? holdings?
        while self.isRunning:
            print("Control Panel")
            print("================================")
            for i in range(0, len(commands)):
                print("{0}. {1}".format(i, commands[i]))
            
            print("================================")
            id = int(input("Please enter a value: "))

            if commands[id] == "Target price":
                self.targetPrice = self.getNumericalInput(commands[id], self.targetPrice)
                print("Target price updated to {0}".format(self.targetPrice))
            elif commands[id] == "Maximum transaction quantity":
                self.maxTransactionQty = self.getNumericalInput(commands[id], self.maxTransactionQty)
            elif commands[id] == "Stop/Start algorithm":
                self.algorithmEnabled = not self.algorithmEnabled
                if self.algorithmEnabled:
                    print("Algorithm enabled.")
                else:
                    print("Algorithm disabled.")
            else:
                print("Unrecognized command.")

            print("\n")

    def getAverages(self, api, stock):        
        while self.isRunning:
            try:
                quote = api.getQuote(stock)

                if quote["ok"] == True:
                    if len(self.result) > 0:
                        if len(self.result["averageAsk"]) > 30:
                            self.result["averageAsk"].remove(0)
                        if len(self.result["averageBid"]) > 30:
                            self.result["averageBid"].remove(0)
                    elif len(self.result) == 0:
                        self.result["averageAsk"] = []
                        self.result["averageAskSize"] = []
                        self.result["averageBid"] = []
                        self.result["averageBidSize"] = []

                    if quote["ask"]:
                        self.result["averageAsk"].append(quote["ask"])
                        self.result["averageAskSize"].append(quote["askSize"])

                    if quote["bid"]:
                        self.result["averageBid"].append(quote["bid"])
                        self.result["averageBidSize"].append(quote["bidSize"])
                    #print("Current ask: {0}, Current ask size: {1}".format(quote["ask"], quote["askSize"]))
                    sleep(5)
                else:
                    print("ERROR: {0}".format(quote["error"]))
                    raise Exception()
    
                self.averageAsk = math.floor(statistics.mean(self.result["averageAsk"]))
                self.averageAskSize = math.floor(statistics.mean(self.result["averageAskSize"]))
                self.averageBid = math.floor(statistics.mean(self.result["averageBid"]))
                self.averageBidSize = math.floor(statistics.mean(self.result["averageBidSize"]))
                print("Average ask: {0}, Average ask size: {1}".format(averageAsk, averageAskSize))
                print("Average bid: {0}, Average bid size: {1}".format(averageBid, averageBidSize))
            except Exception:
                #print("Error: Unable to obtain quote. Last quote: {0}".format(quote))
                blah = 1
