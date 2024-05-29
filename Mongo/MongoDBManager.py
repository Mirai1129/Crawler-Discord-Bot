import datetime
import os
import random
import time
from datetime import datetime, timezone

import pymongo
from pymongo import MongoClient, errors

from Features.API import CozeApi

PAGE_LOAD_WAIT_TIME_MIN = 0.5  # minimum seconds to wait
PAGE_LOAD_WAIT_TIME_MAX = 1  # maximum seconds to wait

coze_api = CozeApi()


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
                content_emo = coze_api.chat_with_bot(content)
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
