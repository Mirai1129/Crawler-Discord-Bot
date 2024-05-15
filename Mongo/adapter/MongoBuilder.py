import datetime
import dotenv
import os

import logging
import pymongo

dotenv.load_dotenv()

logging.basicConfig(level=logging.INFO, format='[MONGODB_INFO] %(message)s')


class MongoBuilder:
    def __init__(self):
        self.client = pymongo.MongoClient(os.getenv('MONGODB_CONNECTION_URL'))
        self.db = None
        self.collection = None
        self.query = None

    def is_database_existed(self, database_name: str) -> bool:
        return database_name in self.client.list_database_names()

    def is_collection_existed(self, collection_name: str) -> bool:
        return collection_name in self.db.list_collection_names()

    def create_database(self, database_name: str) -> None:
        if self.is_database_existed(database_name):
            logging.info(f"Database '{database_name}' already exists")
        else:
            self.db = self.client[database_name]
            logging.info(f"Database '{database_name}' created")

    def create_collection(self, collection_name: str) -> None:
        if self.db is None:
            raise Exception("Database not created. Please create the database first.")

        if not self.is_collection_existed(collection_name):
            self.collection = collection_name
            collection = self.db[collection_name]
            collection.create_index([("name", pymongo.TEXT)])
            logging.info(f"Collection '{collection_name}' created.")
        else:
            logging.info(f"Collection '{collection_name}' already exists.")

    def init_query(self, collection_name: str, query: dict) -> None:
        existing_data = self.db[collection_name].find_one(query)
        if existing_data:
            logging.info(f"Data already exists in collection '{collection_name}'")
        else:
            self.query = self.db[collection_name].insert_one(query)
            logging.info(f"Data inserted into collection '{collection_name}'")

    def close_connection(self) -> None:
        self.client.close()

    def setup_database(self, database_name: str, collection_name: str, schema: dict) -> None:
        self.db = self.client[database_name]
        self.create_database(database_name)
        self.create_collection(collection_name)
        self.init_query(collection_name, schema)
        self.close_connection()


if __name__ == "__main__":
    db_name = "Crawler"
    coll_name = "ptt"
    data = {
        "id": 0,
        "title": "test title",
        "content": "test content",
        "author": "test author",
        "date": "Wed May 15 11:56:53 2024",  # ctime
        "link": "https://test.test/",
        "emotion": "happy",
        "generated_date_time": datetime.datetime.ctime(datetime.datetime.today())
    }
    adapter = MongoBuilder()
    adapter.setup_database(db_name, coll_name, data)
    adapter.close_connection()
