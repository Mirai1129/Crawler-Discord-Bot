import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

PAGE_LOAD_WAIT_TIME = 2  # seconds


class PttCrawler(object):
    def __init__(self):
        self.options = Options()
        self.url = 'https://www.ptt.cc/bbs/Sad/index.html'

    @staticmethod
    def _extract_titles(soup):
        """
        Extract titles from the BeautifulSoup object.
        """
        sections = soup.find_all('div', class_='r-ent')
        titles = []
        for section in sections:
            title_element = section.find('div', class_='title').find('a')
            if title_element:
                titles.append(title_element.text)
        return titles

    def get_title(self, amounts: int) -> list[str]:
        """
        Get titles from PTT.
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

            # Wait for page to load
            time.sleep(PAGE_LOAD_WAIT_TIME)

            if amounts == 1:
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                titles = self._extract_titles(soup)
            elif amounts > 1:
                for _ in range(amounts):
                    driver.find_element(By.XPATH, '/html/body/div[2]/div[1]/div/div[2]/a[2]').click()
                    time.sleep(PAGE_LOAD_WAIT_TIME)
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    titles.extend(self._extract_titles(soup))  # Extend titles with new titles
            else:
                print("Invalid input. Program terminated.")

        except Exception as e:
            print(f"An error occurred: {str(e)}")
        finally:
            if 'driver' in locals():
                driver.quit()

        return titles


def main() -> None:
    crawler = PttCrawler()
    print(crawler.get_title(amounts=3))


if __name__ == "__main__":
    main()
