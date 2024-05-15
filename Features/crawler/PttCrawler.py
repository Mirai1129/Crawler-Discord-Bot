import time
import requests
from bs4 import BeautifulSoup

PAGE_LOAD_WAIT_TIME = 2  # seconds


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
            if title_element and not any(kw in title_element.text for kw in ["[公告]", "[版務]", "[建議]"]):
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
                time.sleep(PAGE_LOAD_WAIT_TIME)
        except Exception as e:
            print(f"發生錯誤：{e}")

        return titles

    def get_article_content(self, article_link):
        """
        獲取指定文章的內容。
        """
        try:
            response = requests.get(f'{self.base_url}{article_link}')
            soup = BeautifulSoup(response.text, 'html.parser')
            content = soup.find(id='main-content').text.strip()
            return content
        except Exception as e:
            print(f"發生錯誤：{e}")
            return ""


def main():
    crawler = PttCrawler()
    board_info = crawler.list_board_info()

    print("看板列表：")
    for idx, description, title in board_info:
        print(f"{{{idx}}} {title}\n{description}\n")

    board_choice = input("請輸入想搜尋的「看板編號」或名稱：")
    num_pages = int(input("請輸入想搜尋的頁數："))

    if board_choice.isdigit():
        board_choice = int(board_choice)
        if 1 <= board_choice <= len(board_info):
            board_name = board_info[board_choice - 1][2]
        else:
            print("無效的看板編號。")
            return
    else:
        board_name = board_choice

    titles_with_date = crawler.get_titles(board_name, num_pages)
    for idx, (title, date, link) in enumerate(titles_with_date, start=1):
        print("****************************************************************************************************")
        print(f"第{idx}篇： {title} - {date}")
        content = crawler.get_article_content(link)
        print(f"內文：{content}\n")
    print("****************************************************************************************************")
    print(f"共爬取了{len(titles_with_date)}篇文章。")


if __name__ == "__main__":
    main()