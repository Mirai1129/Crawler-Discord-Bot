import os
import dotenv
import pymongo

dotenv.load_dotenv()


class MongoAdapter:
    def __init__(self):
        self.client = pymongo.MongoClient(os.getenv('MONGODB_CONNECTION_URL'))
        self.db = self.client["Crawler"]
        self.collection = self.db["ptt"]

    @staticmethod
    def check_fields(data, required_fields):
        for field in required_fields:
            if field not in data:
                return False
        return True

    def insert(self, data, required_fields):
        if self.check_fields(data, required_fields):
            self.collection.insert_one(data)
        else:
            print("Missing required fields")

    def read(self, query):
        return self.collection.find_one(query)

    def update(self, query, new_data, required_fields):
        if self.check_fields(new_data, required_fields):
            self.collection.update_one(query, {"$set": new_data})
        else:
            print("Missing required fields")

    def delete(self, query):
        self.collection.delete_one(query)
