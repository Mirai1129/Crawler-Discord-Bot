import logging
import os

import dotenv
import pymongo
from pymongo import errors

dotenv.load_dotenv()


class MongoBuilder:
    def __init__(self):
        try:
            self.client = pymongo.MongoClient(os.getenv('MONGODB_CONNECTION_URL'))
            self.db = None
            logging.basicConfig(level=logging.INFO, format='[MONGODB_INFO] %(message)s')
        except pymongo.errors.ServerSelectionTimeoutError as err:
            logging.error(f"MongoDB connection timeout: {err}")
        except TimeoutError as err:
            logging.error(f"Connection timeout: {err}")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")

    def is_database_existed(self, database_name: str) -> bool:
        try:
            return database_name in self.client.list_database_names()
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            return False

    def is_collection_existed(self, collection_name: str) -> bool:
        try:
            return collection_name in self.db.list_collection_names()
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            return False

    def create_database(self, database_name: str) -> None:
        self.db = self.client[database_name]
        if self.is_database_existed(database_name):
            logging.info(f"Database '{database_name}' already exists")
        else:
            logging.info(f"Database '{database_name}' created")

    def create_collection(self, collection_name: str) -> None:
        if self.db is None:
            raise Exception("Database not created. Please create the database first.")

        if not self.is_collection_existed(collection_name):
            collection = self.db[collection_name]
            collection.create_index([("name", pymongo.TEXT)])
            logging.info(f"Collection '{collection_name}' created.")
        else:
            logging.info(f"Collection '{collection_name}' already exists.")

    def close_connection(self) -> None:
        self.client.close()

    def setup_database(self, database_name: str, collection_name: str) -> bool:
        if self.is_database_existed(database_name):
            logging.info(f"Database '{database_name}' already exists, skipping creation.")
            return False  # 表示数据库已存在
        else:
            self.create_database(database_name)
            self.create_collection(collection_name)
            logging.info(f"Setup complete for database '{database_name}' and collection '{collection_name}'")
            return True  # 表示数据库是新创建的


if __name__ == "__main__":
    file_name = __file__.split("\\")[-1].split(".")[0]
    logging.info(f"{file_name} has been loaded")
