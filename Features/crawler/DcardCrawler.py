import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class DcardCrawler(object):
    def __init__(self):
        self.options = Options()
        self.url = "https://www.dcard.tw/f/relationship?tab=latest"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/124.0.0.0 Safari/537.36',
            'Referer': 'https://www.dcard.tw/'}

    @staticmethod
    def _extract_titles(soup):
        """
        Extract titles from the BeautifulSoup object.
        """
        titles = []
        sections = soup.select('div[data-key]>div>article>h2>a>span')
        for section in sections:
            titles.append(section.text)
        return titles

    def get_title(self, amounts: int) -> list[str]:
        """
        Get titles from Dcard.
        """
        chrome_options = self.options
        titles = []  # Initialize titles as an empty list
        driver = None

        chrome_options.add_argument("--headless")  # 選擇無頭模式，不顯示瀏覽器
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        try:
            # Initialize WebDriver
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(self.url)

            # 使用隱式等待，等待元素加載完成
            driver.implicitly_wait(10)

            # 捲動到頁面底部
            for _ in range(amounts // 10):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                # 使用顯式等待，等待新的元素出現
                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-key]')))
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                titles.extend(self._extract_titles(soup))  # Extend titles with new titles

        except Exception as e:
            print(f"An error occurred: {str(e)}")
        finally:
            if driver is not None:
                driver.quit()

        return titles


if __name__ == '__main__':
    crawler = DcardCrawler()
    title = crawler.get_title(3)
    print(title)
