import pymongo
import os
import dotenv
import logging

dotenv.load_dotenv()

# 配置日志记录
logging.basicConfig(level=logging.INFO, format='[MONGODB_INFO] %(message)s')


class MongoDBAdapter:
    def __init__(self):
        self.client = pymongo.MongoClient(os.getenv('MONGODB_CONNECTION_URL'))
        self.db = None
        self.collection = None
        self.query = None

    def is_database_exists(self, database_name):
        return database_name in self.client.list_database_names()

    def is_collection_exists(self, collection_name):
        return collection_name in self.db.list_collection_names() if self.db is not None else False

    def create_database(self, database_name):
        if self.is_database_exists(database_name):
            logging.info("Database '{}' already exists".format(database_name))
        else:
            self.db = self.client[database_name]
            logging.info("Database '{}' created".format(database_name))

    def create_collection(self, collection_name):
        if self.db is None:
            raise Exception("Database not created. Please create the database first.")

        if not self.is_collection_exists(collection_name):
            self.collection = collection_name
            collection = self.db[collection_name]
            collection.create_index([("name", pymongo.TEXT)])
            logging.info("Collection '{}' created.".format(collection_name))
        else:
            logging.info("Collection '{}' already exists.".format(collection_name))

    def init_query(self, collection_name, query):
        existing_data = self.db[collection_name].find_one(query)
        if existing_data:
            logging.info("Data already exists in collection '{}'".format(collection_name))
        else:
            self.query = self.db[collection_name].insert_one(query)
            logging.info("Data inserted into collection '{}'".format(collection_name))

    def close_connection(self):
        self.client.close()

    def setup_database(self, database_name, collection_name, schema):
        self.db = self.client[database_name]
        self.create_database(database_name)
        self.create_collection(collection_name)
        self.init_query(collection_name, schema)
        self.close_connection()


if __name__ == "__main__":
    db_name = "Crawler"
    coll_name = "ptt"
    schema = {"id": 0, "title": "test title", "emotion": "happy"}

    adapter = MongoDBAdapter()
    adapter.setup_database(db_name, coll_name, schema)
    adapter.close_connection()
