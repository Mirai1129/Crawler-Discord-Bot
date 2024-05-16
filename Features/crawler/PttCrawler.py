import time
import requests
import random
from bs4 import BeautifulSoup

PAGE_LOAD_WAIT_TIME_MIN = 1  # minimum seconds to wait
PAGE_LOAD_WAIT_TIME_MAX = 3  # maximum seconds to wait


class PttCrawler:
    def __init__(self):
        self.base_url = 'https://www.ptt.cc'
        self.board_list_url = f'{self.base_url}/cls/3732'

    @staticmethod
    def extract_board_info(soup):
        """
        從 BeautifulSoup 物件中提取看板標題和描述。
        """
        boards = soup.find_all('a', class_='board')
        board_info = [(idx + 1, board.find('div', class_='board-title').text.strip(),
                       board.find('div', class_='board-name').text.strip())
                      for idx, board in enumerate(boards)]
        return board_info

    def list_board_info(self):
        """
        列出所有看板標題和描述。
        """
        try:
            response = requests.get(self.board_list_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            return self.extract_board_info(soup)
        except Exception as e:
            print(f"發生錯誤：{e}")
            return []

    @staticmethod
    def extract_titles(soup):
        """
        從 BeautifulSoup 物件中提取標題、日期和連結。
        """
        entries = soup.find_all('div', class_='r-ent')
        titles = []
        for entry in entries:
            title_element = entry.find('div', class_='title').find('a')
            if title_element and not any(
                    kw in title_element.text for kw in ["[公告]", "[版務]", "[建議]", "Fw", "[檢舉]"]):
                title = title_element.text.strip()
                date = entry.find('div', class_='date').text.strip()
                link = title_element['href']
                titles.append((title, date, link))
        return titles

    def get_titles(self, board_name, num_pages):
        """
        獲取指定看板的標題。
        """
        titles = []
        board_url = f"{self.base_url}/bbs/{board_name}/index.html"

        try:
            for _ in range(num_pages):
                response = requests.get(board_url)
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
        """
        獲取指定文章的基本資料。
        """
        try:
            response = requests.get(f'{self.base_url}{article_link}')
            soup = BeautifulSoup(response.text, 'html.parser')

            author = soup.select_one('#main-content > div:nth-child(1) > span:nth-child(2)').text.strip()
            board = soup.select_one('#main-content > div:nth-child(2) > span:nth-child(2)').text.strip()
            title = soup.select_one('#main-content > div:nth-child(3) > span:nth-child(2)').text.strip()
            post_time = soup.select_one('#main-content > div:nth-child(4) > span:nth-child(2)').text.strip()

            # 使用CSS選擇器獲取内文部分
            main_content = soup.find('div', id='main-content')
            content_texts = main_content.find_all(text=True, recursive=False)
            content = ''.join(content_texts).strip()

            return author, board, title, post_time, content
        except Exception as e:
            print(f"發生錯誤：{e}")
            return "", "", "", "", ""


def main():
    crawler = PttCrawler()
    num_pages = int(input("請輸入想搜尋的頁數："))
    board_info = crawler.list_board_info()

    all_articles_data = []

    for idx, description, board_name in board_info:
        print(
            f"====================================================================================================\n正在爬取看板：{board_name} ({description})")
        titles_with_date = crawler.get_titles(board_name, num_pages)

        for idx, (title, date, link) in enumerate(titles_with_date, start=1):
            print(
                "****************************************************************************************************")
            print(f"第{idx}篇：")
            author, board, title, post_time, content = crawler.get_article(link)

            article_data = {
                'index': idx,
                'author': author,
                'board': board,
                'title': title,
                'time': post_time,
                'content': content
            }
            all_articles_data.append(article_data)
            print(article_data)

            # 隨機延遲，避免爬蟲行為過於明顯
            time.sleep(random.uniform(PAGE_LOAD_WAIT_TIME_MIN, PAGE_LOAD_WAIT_TIME_MAX))

    print("****************************************************************************************************")
    print(f"共爬取了{len(all_articles_data)}篇文章。")
    return all_articles_data


if __name__ == "__main__":
    articles_data = main()
    # Here you can process the articles_data as needed, e.g., inserting into a database
