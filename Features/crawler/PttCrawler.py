import datetime
import logging
import random
import time

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='[PTT_CRAWLER] %(message)s')
PAGE_LOADING_TIME_MIN = 0.5  # minimum seconds to wait
PAGE_LOADING_TIME_MAX = 1  # maximum seconds to wait


class PttCrawler:
    def __init__(self):
        self.base_url = 'https://www.ptt.cc'
        self.board_list_url = f'{self.base_url}/cls/3732'
        self.session = requests.Session()
        self.session.cookies.set('over18', '1')

    def _get_soup(self):
        try:
            response = self.session.get(self.board_list_url)
            response.raise_for_status()  # 檢查 HTTP 狀態碼是否為 200
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup
        except requests.exceptions.RequestException as req_err:
            logging.error(f"Request error getting soup: {req_err}")
        except Exception as e:
            logging.error(f"Unexpected error getting soup: {e}")
        return None

    @staticmethod
    def _extract_board_info(soup):
        boards = soup.find_all('a', class_='board')
        board_info = [(idx + 1, board.find('div', class_='board-title').text.strip(),
                       board.find('div', class_='board-name').text.strip())
                      for idx, board in enumerate(boards)]
        return board_info

    def get_board_categories(self):
        """
        Get board categories' info
        """
        soup = self._get_soup()
        if soup:
            return self._extract_board_info(soup)
        else:
            logging.info("No soup obtained.")
            return None

    @staticmethod
    def _extract_titles(soup):
        """
        從代表文章頁面的 BeautifulSoup 物件中提取標題、日期和連結。
        """
        entries = soup.find_all('div', class_='r-ent')
        titles = []
        for entry in entries:
            title_element = entry.find('div', class_='title').find('a')
            # 可能爬到的垃圾, "[建議]", "[LIVE]", "[BGD]"
            if title_element and not any(
                    kw in title_element.text for kw in ["[公告]", "[版務]", "[檢舉]", "[申訴]", "Fw"]):
                title = title_element.text.strip()
                date = entry.find('div', class_='date').text.strip()
                link = title_element['href']
                titles.append((title, date, link))
        return titles

    def get_titles(self, board_name: str, pages_amount: int):
        titles = []
        board_url = f"{self.base_url}/bbs/{board_name}/index.html"

        try:
            for _ in range(pages_amount):
                response = self.session.get(board_url)
                soup = BeautifulSoup(response.text, 'html.parser')

                if soup.select('div.over18-button-container'):
                    self.session.post(f'{self.base_url}/ask/over18', data={'yes': 'yes'})
                    response = self.session.get(board_url)
                    soup = BeautifulSoup(response.text, 'html.parser')

                titles.extend(self._extract_titles(soup))
                next_page_link = soup.find('a', string='‹ 上頁')
                if next_page_link:
                    board_url = f"{self.base_url}{next_page_link['href']}"
                else:
                    break
                time.sleep(random.uniform(PAGE_LOADING_TIME_MIN, PAGE_LOADING_TIME_MAX))
        except Exception as e:
            print(f"發生錯誤：{e}")
        print(titles)
        return titles

    def get_article(self, article_link):
        """
        按連結檢索特定文章的詳細資料訊息。
        """
        try:
            response = self.session.get(f'{self.base_url}{article_link}')
            soup = BeautifulSoup(response.text, 'html.parser')

            if soup.select('div.over18-button-container'):
                self.session.post(f'{self.base_url}/ask/over18', data={'yes': 'yes'})
                response = self.session.get(f'{self.base_url}{article_link}')
                soup = BeautifulSoup(response.text, 'html.parser')

            author = self.get_author(soup)
            board = self.get_board(soup)
            title = self.get_title(soup)
            post_time = self.get_release_time(soup)
            content = self.get_content(soup)

            return author, board, title, post_time, content
        except Exception as e:
            print(f"發生錯誤：{e}")
            return None

    @staticmethod
    def get_author(soup):
        """
        從 BeautifulSoup 物件中提取文章作者。
        """
        try:
            author = soup.select_one('#main-content > div:nth-child(1) > span:nth-child(2)').text.strip()
            return author
        except AttributeError:
            return None

    @staticmethod
    def get_board(soup):
        """
        從 BeautifulSoup 物件中提取看板名稱。
        """
        try:
            board = soup.select_one('#main-content > div:nth-child(2) > span:nth-child(2)').text.strip()
            return board
        except AttributeError:
            return None

    @staticmethod
    def get_title(soup):
        """
        從 BeautifulSoup 物件中提取文章標題。
        """
        try:
            title = soup.select_one('#main-content > div:nth-child(3) > span:nth-child(2)').text.strip()
            return title
        except AttributeError:
            return None

    @staticmethod
    def get_release_time(soup):
        """
        從 BeautifulSoup 物件中提取文章發佈時間。
        """
        try:
            post_time = soup.select_one('#main-content > div:nth-child(4) > span:nth-child(2)').text.strip()
            return post_time
        except AttributeError:
            return None

    @staticmethod
    def get_content(soup):
        """
        從 BeautifulSoup 物件中提取文章內容。
        """
        try:
            main_content = soup.find('div', id='main-content')
            content_texts = main_content.find_all(string=True, recursive=False)
            content = ''.join(content_texts).strip()
            return content
        except AttributeError:
            return None

    def get_article_data(self, board_name, pages_amount):
        """
        從多個頁面中檢索文章並返回文章詳細信息。
        """
        titles = self.get_titles(board_name, pages_amount)
        articles_data = []

        for idx, (title, date, link) in enumerate(titles):
            article_info = self.get_article(link)
            if article_info:
                author, board, title, post_time, content = article_info
                generated_time = datetime.datetime.now().isoformat()

                article_data = {
                    "id": idx,
                    "title": title,
                    "content": content,
                    "author": author,
                    "link": f'{self.base_url}{link}',
                    "post_time": post_time,
                    "generated_time": generated_time
                }
                articles_data.append(article_data)
                time.sleep(random.uniform(PAGE_LOADING_TIME_MIN, PAGE_LOADING_TIME_MAX))

        return articles_data
