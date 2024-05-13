import time
import requests
from bs4 import BeautifulSoup

PAGE_LOAD_WAIT_TIME = 2  # seconds


class PttCrawler(object):
    def __init__(self):
        self.url = 'https://www.ptt.cc/cls/3732'

    @staticmethod
    def _extract_board_info(soup):
        """
        從 BeautifulSoup 物件中提取看板標題和描述。
        """
        sections = soup.find_all('a', class_='board')
        board_info = []
        for idx, section in enumerate(sections, start=1):
            title = section.find('div', class_='board-name').text.strip()
            description = section.find('div', class_='board-title').text.strip()
            board_info.append((idx, description, title))  # 將編號、描述和標題添加到看板信息中
        return board_info

    def list_board_info(self):
        """
        列出給定 URL 中的所有看板標題和描述。
        """
        try:
            response = requests.get(self.url)
            soup = BeautifulSoup(response.text, 'html.parser')
            board_info = self._extract_board_info(soup)
            return board_info
        except Exception as e:
            print(f"發生錯誤：{str(e)}")

    @staticmethod
    def _extract_titles(soup):
        """
        從 BeautifulSoup 物件中提取標題、日期和連結。
        """
        sections = soup.find_all('div', class_='r-ent')
        titles_with_date = []
        for section in sections:
            title_element = section.find('div', class_='title').find('a')
            if title_element:
                title = title_element.text.strip()
                if not any(keyword in title for keyword in ["[公告]", "[版務]", "[建議]"]):  # 檢查標題中是否包含指定的字串
                    date_element = section.find('div', class_='date')
                    date = date_element.text.strip() if date_element else ""
                    link = title_element.get('href')
                    titles_with_date.append((title, date, link))
        return titles_with_date

    def get_title(self, board_choice: str, num_pages: int) -> list[str]:
        """
        從指定的看板 URL 中獲取標題。
        """
        titles_with_date = []  # 初始化標題列表為空
        board_info = self.list_board_info()

        try:
            # 檢查用戶輸入是否為數字
            if board_choice.isdigit():
                idx = int(board_choice)
                if 1 <= idx <= len(board_info):
                    selected_board_title = board_info[idx - 1][2]  # 從所選索引中獲取看板標題
                else:
                    print("無效的看板編號。程式已終止。")
                    return titles_with_date
            else:
                selected_board_title = board_choice

            board_url = f"https://www.ptt.cc/bbs/{selected_board_title}/index.html"
            print("所選擇的看板連結：", board_url)
            print(f">>> 已選取 {selected_board_title} 看板<<<")

            if num_pages > 0:
                for _ in range(num_pages):
                    response = requests.get(board_url)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    titles_with_date.extend(self._extract_titles(soup))  # 將新標題擴展到標題列表中
                    next_link = soup.find('a', string='‹ 上頁')  # 找到下一頁的連結
                    if next_link:
                        board_url = 'https://www.ptt.cc' + next_link['href']  # 更新下一頁的 URL
                    else:
                        break  # 如果沒有下一頁，則退出循環
                    time.sleep(PAGE_LOAD_WAIT_TIME)
            else:
                print("無效的頁數輸入。程式已終止。")

        except Exception as e:
            print(f"發生錯誤：{str(e)}")

        return titles_with_date

    def get_article_content(self, article_link: str) -> str:
        """
        從指定文章連結中獲取內文。
        """
        try:
            response = requests.get('https://www.ptt.cc' + article_link)
            soup = BeautifulSoup(response.text, 'html.parser')
            content = soup.select_one('div#main-content').text.strip()
            return content
        except Exception as e:
            print(f"發生錯誤：{str(e)}")
            return ""


def main() -> None:
    crawler = PttCrawler()
    board_info = crawler.list_board_info()
    print("看板列表：")
    for idx, description, title in board_info:
        print(f"{{{idx}}} {title}\n{description}\n")  # 調整輸出格式

    board_choice = input("請輸入想搜尋的「看板編號」：")
    num_pages = int(input("請輸入想搜尋的頁數："))

    # 開始爬取所選擇的看板
    titles_with_date = crawler.get_title(board_choice, num_pages)
    for idx, (title, date, link) in enumerate(titles_with_date, start=1):
        print("****************************************************************************************************")
        print(f"第{idx}篇： {title} - {date}")  # 編號
        content = crawler.get_article_content(link)
        print(f"內文：{content}")
        print("\n")
    print("****************************************************************************************************")
    print(f"共爬取了{len(titles_with_date)}篇文章。")


if __name__ == "__main__":
    main()
