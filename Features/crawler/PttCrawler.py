import time
import requests
import random
from bs4 import BeautifulSoup
from pymongo import MongoClient, errors
from datetime import datetime

PAGE_LOAD_WAIT_TIME_MIN = 1  # minimum seconds to wait
PAGE_LOAD_WAIT_TIME_MAX = 1.5  # maximum seconds to wait


class PttCrawler:
    def __init__(self):
        self.base_url = 'https://www.ptt.cc'
        self.board_list_url = f'{self.base_url}/cls/3732'
        self.session = requests.Session()
        self.session.cookies.set('over18', '1')  # 設置 over18 cookie

    @staticmethod
    def extract_board_info(soup):
        boards = soup.find_all('a', class_='board')
        board_info = [(idx + 1, board.find('div', class_='board-title').text.strip(),
                       board.find('div', class_='board-name').text.strip())
                      for idx, board in enumerate(boards)]
        return board_info

    def list_board_info(self):
        try:
            response = self.session.get(self.board_list_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            return self.extract_board_info(soup)
        except Exception as e:
            print(f"發生錯誤：{e}")
            return []

    @staticmethod
    def extract_titles(soup):
        entries = soup.find_all('div', class_='r-ent')
        titles = []
        for entry in entries:
            title_element = entry.find('div', class_='title').find('a')
            # 可能爬到的垃圾, [建議]", "[LIVE]","[BGD]"
            if title_element and not any(
                    kw in title_element.text for kw in ["[公告]", "[版務]", "[檢舉]", "[申訴]", "Fw"]):
                title = title_element.text.strip()
                date = entry.find('div', class_='date').text.strip()
                link = title_element['href']
                titles.append((title, date, link))
        return titles

    def get_titles(self, board_name, num_pages):
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

                titles.extend(self.extract_titles(soup))
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


def get_board_info(crawler):
    return crawler.list_board_info()


def tran_time_to_date(post_time):
    # 將 post_time 轉換為 YYYY/MM/DD 格式的字符串
    try:
        post_date = datetime.strptime(post_time, "%a %b %d %H:%M:%S %Y").strftime("%Y/%m/%d")
    except ValueError as e:
        print(f"日期轉換錯誤：{e}")
        return "0000/00/00"
    return post_date


def get_articles(crawler, num_pages, board_info, collection):
    all_articles_data = []
    inserted_count = 0
    duplicate_count = 0
    global_idx = 1  # 全局計數器

    for board_idx, description, board_name in board_info:
        print("=", f"\n正在爬取看板：{board_name} ({description})")
        titles_with_date = crawler.get_titles(board_name, num_pages)

        for (title, date, link) in titles_with_date:
            print("-" * 100)
            print(f"第{global_idx}篇：")
            author, board, title, post_time, content = crawler.get_article(link)

            post_date = tran_time_to_date(post_time)

            # 檢查資料庫中是否已存在該標題的文章
            if collection.find_one({"title": title}):
                print(f"重複的文章：{title}")
                duplicate_count += 1
            else:
                article_data = {
                    'index': global_idx,
                    'author': author,
                    'board': board,
                    'title': title,
                    'date': post_date,
                    'content': content
                }
                collection.insert_one(article_data)
                inserted_count += 1
                print(f"插入文章：{title}")
                all_articles_data.append(article_data)

            global_idx += 1  # 增加全局計數器
            time.sleep(random.uniform(PAGE_LOAD_WAIT_TIME_MIN, PAGE_LOAD_WAIT_TIME_MAX))

    return all_articles_data, inserted_count, duplicate_count


def store_to_mongodb(crawler, num_pages, board_info):
    connection_string = 'mongodb+srv://{}:{}@pttcrawler.ewbsmua.mongodb.net/?retryWrites=true&w=majority&appName=PttCrawler'

    client = MongoClient(connection_string, serverSelectionTimeoutMS=50000)
    db = client['ptt_database']
    collection = db['articles']

    try:
        all_articles_data, inserted_count, duplicate_count = get_articles(crawler, num_pages, board_info, collection)
        print(f"已插入{inserted_count}篇文章，跳過{duplicate_count}篇重複的文章。")
    except errors.ServerSelectionTimeoutError as err:
        print(f"連接到 MongoDB 伺服器愈時：{err}")
    except errors.PyMongoError as err:
        print(f"插入文檔時發生錯誤：{err}")
    finally:
        client.close()  # 確保 MongoDB 連接在完成後關閉


def main():
    crawler = PttCrawler()
    num_pages = int(input("請輸入想搜尋的頁數："))

    board_info = get_board_info(crawler)
    store_to_mongodb(crawler, num_pages, board_info)


if __name__ == "__main__":
    main()
