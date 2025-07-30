import os
from unittest import TestCase, skip

from .. import KoreaInvestment, API_RETURN_CODE


class TestKoreaInvestment(TestCase):
    @classmethod
    def setUpClass(cls):
        api_key = os.getenv('KOREA_INVESTMENT_API_KEY')
        api_secret = os.getenv('KOREA_INVESTMENT_API_SECRET')
        acc_no = os.getenv('KOREA_INVESTMENT_ACCOUNT_NO')

        cls.kis = KoreaInvestment(
            api_key=api_key,
            api_secret=api_secret,
            acc_no=acc_no,
        )

    def test_stock_info(self):
        stock_market_list = [
            ("005930", "KR"),
            ("017670", "KR"),
            ("AAPL", "US"),
        ]

        results = self.kis.fetch_stock_info_list(stock_market_list)
        self.assertEqual(len(results), len(stock_market_list))

        for result in results:
            print(result)
            self.assertEqual(result['rt_cd'], API_RETURN_CODE["SUCCESS"])

    def test_fetch_search_stock_info(self):
        stock_market_list = [
            ("005930", "KR"),
            ("294400", "KR")
        #     국내 주식만 조회가 가능하다
        ]

        results = self.kis.fetch_search_stock_info_list(stock_market_list)

        self.assertEqual(len(results), len(stock_market_list))
        for result in results:
            print(result)
            self.assertEqual(result['rt_cd'], API_RETURN_CODE["SUCCESS"])
            self.assertIn('output', result)
            self.assertIn('frbd_mket_lstg_dt', result['output'])

    def test_fetch_price(self):
        stock_market_list = [
            ("005930", "KR"),
            ("294400", "KR"), # ETF
            ("AAPL", "US"),
            ("QQQM", "US"), # ETF

        ]

        results = self.kis.fetch_price_list(stock_market_list)
        self.assertEqual(len(results), len(stock_market_list))
        for result in results:
            print(result)
            self.assertEqual(result['rt_cd'], API_RETURN_CODE["SUCCESS"])

    @skip("Skipping test_fetch_kospi_symbols")
    def test_fetch_kospi_symbols(self):
        resp = self.kis.fetch_kospi_symbols()
        print(resp)
        self.assertEqual(resp['rt_cd'], API_RETURN_CODE["SUCCESS"])

    # todo: 이 unit test는 정리가 필요하다
    def test_fetch_price_detail_oversea(self):
        stock_market_list = [
            # ("AAPL", "US"),
            ("QQQM", "US"), # ETF
        ]

        results = self.kis.fetch_price_detail_oversea_list(stock_market_list)
        self.assertEqual(len(results), len(stock_market_list))

        for result in results:
            print(result)
            self.assertEqual(result['rt_cd'], API_RETURN_CODE["SUCCESS"])
            self.assertNotEqual(result['output']['rsym'], None)
