import time
import pymongo
import requests
import random
import os
from bs4 import BeautifulSoup
from pymongo import MongoClient, errors
from datetime import datetime, timezone
from dotenv import load_dotenv  # 引入 dotenv 來加載 .env 文件
import coze_API  # 引入 coze_API.py 作為模組

load_dotenv()  # 呼叫載入 .env 檔

PAGE_LOAD_WAIT_TIME_MIN = 0.5  # minimum seconds to wait
PAGE_LOAD_WAIT_TIME_MAX = 1  # maximum seconds to wait


class PttCrawler:
    """
    PttCrawler 類別，用於從 PTT 網站爬取數據。
    """

    def __init__(self):
        self.base_url = 'https://www.ptt.cc'
        self.board_list_url = f'{self.base_url}/cls/3732'
        self.session = requests.Session()
        self.session.cookies.set('over18', '1')  # 設置 over18 cookie

    @staticmethod
    def _extract_board_info(soup):
        """
        從傳遞的 BeautifulSoup 物件中提取有關不同看板的訊息。
        """
        boards = soup.find_all('a', class_='board')
        board_info = [(idx + 1, board.find('div', class_='board-title').text.strip(),
                       board.find('div', class_='board-name').text.strip())
                      for idx, board in enumerate(boards)]
        return board_info

    def _get_board_categories(self):
        """
        檢索並返回 PTT 網站上各個看板的訊息。
        """
        try:
            response = self.session.get(self.board_list_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            return self._extract_board_info(soup)
        except Exception as e:
            print(f"發生錯誤：{e}")
            return []

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

    def get_titles(self, board_name, num_pages):
        """
        檢索特定看板的帖子標題，並指定要檢索的頁數。
        """
        titles = []
        board_url = f"{self.base_url}/bbs/{board_name}/index.html"

        try:
            for _ in range(num_pages):
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
                time.sleep(random.uniform(PAGE_LOAD_WAIT_TIME_MIN, PAGE_LOAD_WAIT_TIME_MAX))
        except Exception as e:
            print(f"發生錯誤：{e}")

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

            author = soup.select_one('#main-content > div:nth-child(1) > span:nth-child(2)').text.strip()
            board = soup.select_one('#main-content > div:nth-child(2) > span:nth-child(2)').text.strip()
            title = soup.select_one('#main-content > div:nth-child(3) > span:nth-child(2)').text.strip()
            post_time = soup.select_one('#main-content > div:nth-child(4) > span:nth-child(2)').text.strip()

            main_content = soup.find('div', id='main-content')
            content_texts = main_content.find_all(string=True, recursive=False)
            content = ''.join(content_texts).strip()

            return author, board, title, post_time, content
        except Exception as e:
            print(f"發生錯誤：{e}")
            return "", "", "", "", ""


def convert_time_to_iso_date(post_time):
    """
    將從 PTT 網站獲取的日期和時間字符串轉換為 ISO 格式。
    """
    try:
        post_date = datetime.strptime(post_time, "%a %b %d %H:%M:%S %Y").astimezone(timezone.utc)
    except ValueError as e:
        print(f"日期轉換錯誤：{e}")
        return datetime(1970, 1, 1, tzinfo=timezone.utc)
    return post_date


class MongoDBManager:
    """
    提取與 MongoDB 相關的功能類別。
    """

    def __init__(self, connection_string):
        self.client = MongoClient(connection_string, serverSelectionTimeoutMS=50000)
        self.db = self.client['ptt_database']
        self.collection = self.db['articles']

    def close_connection(self):
        """
        關閉與 MongoDB 伺服器的連接。
        """
        self.client.close()

    def create_index(self):
        """
        在 MongoDB 集合中建立索引，以便進行有效的查詢和數據管理。
        """
        try:
            self.collection.create_index([('generated_date', pymongo.DESCENDING)], name='generated_date_idx')
            self.collection.create_index([('generated_date', 1)], expireAfterSeconds=86400)
        except errors.PyMongoError as err:
            print(f"索引創建時發生錯誤：{err}")

    def insert_article(self, article_data):
        """
        將文章數據插入到 MongoDB 集合中。
        """
        try:
            self.collection.insert_one(article_data)
        except errors.PyMongoError as err:
            print(f"插入文檔時發生錯誤：{err}")


def crawl_and_store_articles(crawler, num_pages, board_info, mongo_manager):
    """
    從多個看板中檢索文章並將其存儲到 MongoDB 中。
    """
    all_articles_data = []
    inserted_count = 0
    duplicate_count = 0
    global_idx = 0

    for board_idx, description, board_name in board_info:

        # 排除 HatePolitics、HateP_Picket、HatePicket 看板
        if board_name == 'HatePolitics' or board_name == 'HateP_Picket' or board_name == 'HatePicket':
            print(f"跳過爬取看板：{board_name} ({description})")
            continue

        print("=", f"\n正在爬取看板：{board_name} ({description})")
        titles = crawler.get_titles(board_name, num_pages)

        for (title, date, link) in titles:
            print("-" * 100)
            print(f"第{global_idx}篇：")
            author, board, title, post_time, content = crawler.get_article(link)

            post_date = convert_time_to_iso_date(post_time)
            generated_date = datetime.now(timezone.utc).isoformat()

            if mongo_manager.collection.find_one({"title": title}):
                print(f"重複的文章：{title}")
                duplicate_count += 1
                continue  # 跳過重複的文章

            try:
                # 以 coze_API 回傳的字元數判斷，當 Token 用盡時，停止爬蟲。
                content_emo = coze_API.chat_with_bot(content)
                if len(content_emo) > 20:
                    print(content_emo)
                    print(f"已插入{inserted_count}篇文章，跳過{duplicate_count}篇重複的文章。")
                    return all_articles_data, inserted_count, duplicate_count
            except Exception as e:
                print(f"發生其他錯誤：{e}")
                continue

            article_data = {
                'index': global_idx,
                'link': link,
                'board': board,
                'author': author,
                'title': title,
                'post_date': post_date,
                'content': content,
                'emotion': content_emo,
                'generated_date': generated_date
            }
            mongo_manager.insert_article(article_data)
            inserted_count += 1
            print(f"插入文章：{title}")
            all_articles_data.append(article_data)

            global_idx += 1
            time.sleep(random.uniform(PAGE_LOAD_WAIT_TIME_MIN, PAGE_LOAD_WAIT_TIME_MAX))

    print(f"已插入{inserted_count}篇文章，跳過{duplicate_count}篇重複的文章。")
    return all_articles_data, inserted_count, duplicate_count


def insert_to_mongodb(crawler, num_pages, board_info):
    """
    通過與其他函數協調，管理將文章存儲到 MongoDB 中的過程。
    """
    connection_string = os.getenv("MONGODB_CONNECTION_STRING")
    mongo_manager = MongoDBManager(connection_string)

    try:
        mongo_manager.create_index()
        all_articles_data, inserted_count, duplicate_count = crawl_and_store_articles(crawler, num_pages, board_info,
                                                                                      mongo_manager)
    finally:
        mongo_manager.close_connection()


def main():
    """
    程式的主要入口點。協調執行其他功能。
    """
    crawler = PttCrawler()
    num_pages = int(input("請輸入想搜尋的頁數："))

    board_info = crawler._get_board_categories()
    insert_to_mongodb(crawler, num_pages, board_info)


if __name__ == "__main__":
    main()
