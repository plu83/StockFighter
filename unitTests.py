import unittest
import StockFighter.StockFighterApi as SfApi
import StockFighter.Utilities as Utils

apiKey = "48948ef62b622c5b2be0791e52285007375d9eb0"
account = "1234"

class StockFighterApiFix(unittest.TestCase):
    def setUp(self):
        global apiKey
        global account

        self.apiKey = apiKey
        self.account = account
        return super().setUp()

    def test_construct(self):
        sfapi = SfApi.StockFighterApi(self.apiKey, self.account)
        self.assertIsNotNone(sfapi)

    def test_connect(self):
        sfapi = SfApi.StockFighterApi(self.apiKey, self.account)
        sfapi.connect()

    def test_api_up(self):
        sfapi = SfApi.StockFighterApi(self.apiKey, self.account)
        sfapi.connect()
        sfapi.isApiUp()

    def test_venue(self):
        sfapi = SfApi.StockFighterApi(self.apiKey, self.account)
        sfapi.connect()
        sfapi.isVenueUp()

    def test_stock_list(self):
        sfapi = SfApi.StockFighterApi(self.apiKey, self.account)
        sfapi.connect()
        stocks = sfapi.getStockList()

        for stock in stocks:
            sfapi.getOrderbook(stock['symbol'])

        for stock in stocks:
            sfapi.getQuote(stock['symbol'])

    def test_order(self):
        sfapi = SfApi.StockFighterApi(self.apiKey, self.account)
        sfapi.connect()
        stocks = sfapi.getStockList()

        sfapi.placeOrder(stocks[0], 1, 1, Utils.OrderDirection.BUY, Utils.OrderType.FILL_OR_KILL)
        sfapi.placeOrder(stocks[0], 1, 1, Utils.OrderDirection.SELL, Utils.OrderType.FILL_OR_KILL)

if __name__ == '__main__':
    unittest.main()
