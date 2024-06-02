import datetime
import logging
import random
import time

import requests
from bs4 import BeautifulSoup

PAGE_LOADING_TIME_MIN = 0.5  # minimum seconds to wait
PAGE_LOADING_TIME_MAX = 1  # maximum seconds to wait


class PttCrawler:
    def __init__(self):
        """
        Initialize the PttCrawler with base URL and board list URL.
        Set up a session with cookies to bypass the age restriction.
        """
        self.base_url = 'https://www.ptt.cc'
        self.board_list_url = f'{self.base_url}/cls/3732'
        self.session = requests.Session()
        self.session.cookies.set('over18', '1')
        logging.basicConfig(level=logging.INFO, format='[PTT_CRAWLER] %(message)s')

    def _get_soup(self) -> BeautifulSoup | None:
        """
        Retrieve and parse HTML content from the board list URL.

        Returns:
            BeautifulSoup | None: Parsed HTML content as a BeautifulSoup object if successful, None otherwise.
        """
        try:
            response = self.session.get(self.board_list_url)
            response.raise_for_status()  # Check if HTTP status code is 200 (OK)
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup
        except requests.exceptions.RequestException as req_err:
            logging.error(f"Request error getting soup: {req_err}")
        except Exception as e:
            logging.error(f"Unexpected error getting soup: {e}")
        return None

    @staticmethod
    def _extract_board_info(soup: BeautifulSoup):
        """
        Extract board information from the provided BeautifulSoup object.

        Args:
            soup (BeautifulSoup): Parsed HTML content.

        Returns:
            list of tuple: List of tuples, each containing board index, title, and name.
        """
        boards = soup.find_all('a', class_='board')
        board_info = [(board_index + 1,
                       board.find('div', class_='board-title').text.strip(),
                       board.find('div', class_='board-name').text.strip())
                      for board_index, board in enumerate(boards)]
        return board_info

    def get_board_categories(self):
        """
        Get board categories' information.

        This function retrieves the HTML content from the board list URL, parses it,
        and extracts the board information such as index, title, and board name.

        Returns:
            list of tuple | None: List of tuples containing board information if successful, None otherwise.
                Each tuple contains:
                    - int: Board index
                    - str: Board title
                    - str: Board name
        """
        soup = self._get_soup()
        if soup:
            return self._extract_board_info(soup)
        else:
            logging.error("No soup obtained.")
            return None

    @staticmethod
    def _extract_titles(soup: BeautifulSoup):
        """
        Extract titles, dates, and links from the provided BeautifulSoup object representing a page of articles.

        Args:
            soup (BeautifulSoup): Parsed HTML content.

        Returns:
            list of tuple: List of tuples, each containing the title, date, and link of an article.
        """
        entries = soup.find_all('div', class_='r-ent')
        titles = []
        for entry in entries:
            title_element = entry.find('div', class_='title').find('a')
            # Filter out unwanted posts
            if title_element and not any(
                    kw in title_element.text for kw in ["[公告]", "[版務]", "[檢舉]", "[申訴]", "Fw"]):
                title = title_element.text.strip()
                date = entry.find('div', class_='date').text.strip()
                link = title_element['href']
                titles.append((title, date, link))
        return titles

    def get_titles(self, board_name: str, pages_amount: int):
        """
        Retrieve titles from multiple pages of a specified board.

        Args:
            board_name (str): The name of the board to scrape.
            pages_amount (int): The number of pages to scrape.

        Returns:
            list of tuple: List of tuples, each containing the title, date, and link of an article.
        """
        titles = []
        board_url = f"{self.base_url}/bbs/{board_name}/index.html"

        try:
            for _ in range(pages_amount):
                response = self.session.get(board_url)
                soup = BeautifulSoup(response.text, 'html.parser')

                # Handle age restriction
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
            logging.error(f"Error occurred: {e}")
        return titles

    def get_article(self, article_link: str):
        """
        Retrieve details of a specific article by its link.

        Args:
            article_link (str): The relative link to the article.

        Returns:
            tuple | None: Tuple containing author, board, title, post time, and content if successful, None otherwise.
        """
        try:
            response = self.session.get(f'{self.base_url}{article_link}')
            soup = BeautifulSoup(response.text, 'html.parser')

            # Handle age restriction
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
            logging.error(f"Error occurred: {e}")
            return None

    @staticmethod
    def get_author(soup: BeautifulSoup) -> str | None:
        """
        Extract the author of an article from the provided BeautifulSoup object.

        Args:
            soup (BeautifulSoup): Parsed HTML content.

        Returns:
            str | None: The author of the article if found, None otherwise.
        """
        try:
            author = soup.select_one('#main-content > div:nth-child(1) > span:nth-child(2)').text.strip()
            return author
        except AttributeError:
            return None

    @staticmethod
    def get_board(soup: BeautifulSoup) -> str | None:
        """
        Extract the board name of an article from the provided BeautifulSoup object.

        Args:
            soup (BeautifulSoup): Parsed HTML content.

        Returns:
            str | None: The board name if found, None otherwise.
        """
        try:
            board = soup.select_one('#main-content > div:nth-child(2) > span:nth-child(2)').text.strip()
            return board
        except AttributeError:
            return None

    @staticmethod
    def get_title(soup: BeautifulSoup) -> str | None:
        """
        Extract the title of an article from the provided BeautifulSoup object.

        Args:
            soup (BeautifulSoup): Parsed HTML content.

        Returns:
            str | None: The title if found, None otherwise.
        """
        try:
            title = soup.select_one('#main-content > div:nth-child(3) > span:nth-child(2)').text.strip()
            return title
        except AttributeError:
            return None

    @staticmethod
    def get_release_time(soup: BeautifulSoup) -> str | None:
        """
        Extract the release time of an article from the provided BeautifulSoup object.

        Args:
            soup (BeautifulSoup): Parsed HTML content.

        Returns:
            str | None: The release time if found, None otherwise.
        """
        try:
            post_time = soup.select_one('#main-content > div:nth-child(4) > span:nth-child(2)').text.strip()
            return post_time
        except AttributeError:
            return None

    @staticmethod
    def get_content(soup: BeautifulSoup) -> str | None:
        """
        Extract the content of an article from the provided BeautifulSoup object.

        Args:
            soup (BeautifulSoup): Parsed HTML content.

        Returns:
            str | None: The content of the article if found, None otherwise.
        """
        try:
            main_content = soup.find('div', id='main-content')
            content_texts = main_content.find_all(string=True, recursive=False)
            content = ''.join(content_texts).strip()
            return content
        except AttributeError:
            return None

    def get_article_data(self, board_name: str, pages_amount: int) -> list[dict]:
        """
        Retrieve articles from multiple pages and return detailed information about the articles.

        Args:
            board_name (str): The name of the board to scrape.
            pages_amount (int): The number of pages to scrape.

        Returns:
            list of dict: List of dictionaries, each containing detailed information about an article.
                Each dictionary contains:
                    - id (int): Index of the article.
                    - title (str): Title of the article.
                    - content (str): Content of the article.
                    - author (str): Author of the article.
                    - link (str): Link to the article.
                    - post_time (str): Post time of the article.
                    - generated_time (str): Time when the data was generated.
        """
        titles = self.get_titles(board_name, pages_amount)
        articles_data = []

        for article_index, (title, date, link) in enumerate(titles):
            article_info = self.get_article(link)
            if article_info:
                author, board, title, post_time, content = article_info
                generated_time = datetime.datetime.now().isoformat()

                article_data = {
                    "id": article_index,
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


if __name__ == "__main__":
    file_name = __file__.split("\\")[-1].split(".")[0]
    logging.info(f"{file_name} has been loaded")
