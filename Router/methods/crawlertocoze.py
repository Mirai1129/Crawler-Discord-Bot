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


def crawl_and_store_articles(crawler: PttCrawler,
                             num_pages: int,
                             board_list: list[tuple[int, str, str]] | None,
                             ):
    """
    从多个看板中检索文章并将其存储到 MongoDB 中。

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
            print(f"skipped board: {board_name} ({board_title})")
            continue

        print(f"crawling board: {board_name} ({board_title})")
        article_titles = crawler.get_titles(board_name, num_pages)

        for (article_title, article_date, article_link) in article_titles:
            print(f"第 {article_index} 篇文章：")
            article_info = crawler.get_article(article_link)
            print(article_info)

            if article_info is None:
                print(f"无法获取文章信息：{article_link}")
                continue

            author, board, title, post_time, content = article_info

            post_time = convert_time_to_iso_date(post_time)
            now = datetime.now()
            generated_time = bson.datetime.datetime(now.year, now.month, now.day,
                                                    now.hour, now.minute, now.second)
            # generated_date = datetime.datetime.now(datetime.timezone.utc).isoformat()

            # Check if the article already exists in the database
            if database.read({"title": title}):
                print(f"重复的文章：{title}")
                continue

            try:
                # Call CozeApi for sentiment analysis
                content_emotion = coze_api.get_article_emoji(content)
                if len(content_emotion) > 20:
                    print(content_emotion)
                    return all_articles_data
            except Exception as e:
                print(f"发生错误：{e}")
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
            database.insert(article_data)
            print(f"插入文章：{title}")
            all_articles_data.append(article_data)

            article_index += 1
            time.sleep(random.uniform(PAGE_LOADING_TIME_MIN, PAGE_LOADING_TIME_MAX))

    return all_articles_data


def convert_time_to_iso_date(post_time):
    """
    将从 PTT 网站获取的日期和时间字符串转换为 BSON 格式。
    """
    try:
        post_date = datetime.strptime(post_time, "%a %b %d %H:%M:%S %Y").astimezone(timezone.utc)
    except ValueError as e:
        print(f"日期转换错误：{e}")
        return bson.datetime.datetime(1970, 1, 1, tzinfo=timezone.utc)
    return bson.datetime.datetime(post_date.year, post_date.month, post_date.day,
                                  post_date.hour, post_date.minute, post_date.second)


def main():
    crawler = PttCrawler()
    board_categories = crawler.get_board_categories()
    crawl_and_store_articles(PttCrawler(), 2, board_list=board_categories)


if __name__ == "__main__":
    main()
