import datetime
import random
import time
from datetime import datetime, timezone

import bson

from Features import PttCrawler
from Features.Api import CozeApi
from Mongo import MongoAdapter

PAGE_LOADING_TIME_MIN = 0.5
PAGE_LOADING_TIME_MAX = 1

coze_api = CozeApi()
database = MongoAdapter()


def get_ptt_articles_data(crawler: PttCrawler,
                          num_pages: int = 2,
                          board_list: list[tuple[int, str, str]] | None = None):
    """
    Retrieve articles from multiple boards and store them in MongoDB.

    Args:
        crawler (PttCrawler): PTT Crawler instance.
        num_pages (int): Number of pages to crawl.
        board_list (list of tuple | None): List of tuples containing board information (id, title, name).

    Returns:
        tuple: Contains all articles data, total inserted articles count, and total duplicates count.
    """
    skipped_boards = ['HatePolitics', 'HateP_Picket', 'HatePicket']
    all_articles_data = []
    if board_list is None:
        return

    # Get the current maximum index from the database
    max_index = database.find_one_lasted("id")
    if max_index is not None:
        article_index = max_index["id"] + 1
    else:
        article_index = 0

    for board_id, board_title, board_name in board_list:
        # Skip specified boards
        if board_name in skipped_boards:
            print(f"Skipped board: {board_name} ({board_title})")
            continue

        print(f"Crawling board: {board_name} ({board_title})")
        article_titles = crawler.get_titles(board_name, num_pages)

        for (article_title, article_date, article_link) in article_titles:
            print(article_titles)
            print(f"Article number {article_index}:")
            article_info = crawler.get_article(article_link)
            print(article_info)

            if article_info is None:
                print(f"Unable to get article info: {article_link}")
                continue

            author, board, title, post_time, content = article_info

            post_time = convert_time_to_iso_date(post_time)
            now = datetime.now()
            generated_time = bson.datetime.datetime(now.year, now.month, now.day,
                                                    now.hour, now.minute, now.second)

            # Check if the article already exists in the database
            if database.read({"title": title}):
                print(f"Duplicate article: {title}")
                continue

            try:
                # Call CozeApi for sentiment analysis
                content_emotion = "happy"
                # content_emotion = coze_api.get_article_emoji(content)
                if len(content_emotion) > 20:
                    print(content_emotion)
                    continue
            except Exception as e:
                print(f"Error occurred: {e}")
                continue

            article_data = {
                'id': article_index,
                'title': title,
                'content': content,
                'author': author,
                'link': article_link,
                'emotion': content_emotion,
                'post_time': post_time,
                'generated_time': generated_time
            }
            all_articles_data.append(article_data)
            print(f"Appended article: {title}")

            article_index += 1
            time.sleep(random.uniform(PAGE_LOADING_TIME_MIN, PAGE_LOADING_TIME_MAX))

    return all_articles_data


def store_articles_in_database(articles_data):
    """
    Store articles data in the database.

    Args:
        articles_data (list): List of article data dictionaries.

    Returns:
        int: Total inserted articles count.
    """
    inserted_count = 0
    for article_data in articles_data:
        try:
            database.insert(article_data)
            inserted_count += 1
            print(f"Inserted article: {article_data['title']}")
        except Exception as e:
            print(f"Error occurred while inserting article: {e}")
    return inserted_count


def convert_time_to_iso_date(post_time):
    """
    Convert the date and time string retrieved from the PTT website to BSON format.
    """
    try:
        post_date = datetime.strptime(post_time, "%a %b %d %H:%M:%S %Y").astimezone(timezone.utc)
    except ValueError as e:
        print(f"Date conversion error: {e}")
        return bson.datetime.datetime(1970, 1, 1, tzinfo=timezone.utc)
    return bson.datetime.datetime(post_date.year, post_date.month, post_date.day,
                                  post_date.hour, post_date.minute, post_date.second)


def main():
    crawler = PttCrawler()
    board_categories = crawler.get_board_categories()
    get_ptt_articles_data(PttCrawler(), 2, board_list=board_categories)


if __name__ == "__main__":
    main()
