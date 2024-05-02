import requests
import cloudscraper
import pandas as pd

from bs4 import BeautifulSoup


class DcardCrawler(object):
    def __init__(self):
        self.url = "https://www.dcard.tw/f/relationship"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/124.0.0.0 Safari/537.36',
            'Referer': 'https://www.dcard.tw/'}
        self.resp = requests.get(self.url, headers=self.headers)

    def get_top_three_data(self):
        # Dcard is preventing crawler seriously...
        cloudscraper_body = cloudscraper.create_scraper().get(self.url).text

        soup = BeautifulSoup(self.resp.text, 'html.parser')
        article_title = soup.select_one('div[data-key="2"] span')


if __name__ == '__main__':
    crawler = DcardCrawler()
    crawler.get_top_three_data()
