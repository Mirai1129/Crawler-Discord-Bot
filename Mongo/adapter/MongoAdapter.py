import os
import dotenv
import pymongo
import logging

dotenv.load_dotenv()

# 配置日志
logging.basicConfig(level=logging.INFO, format='[MONGODB_INFO] %(message)s')


class MongoAdapter:
    def __init__(self):
        try:
            self.client = pymongo.MongoClient(os.getenv('MONGODB_CONNECTION_URL'), serverSelectionTimeoutMS=5000)
            self.db = self.client["Crawler"]
            self.collection = self.db["ptt"]
        except pymongo.errors.ServerSelectionTimeoutError as err:
            logging.error(f"MongoDB connection timeout: {err}")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")

    @staticmethod
    def check_fields(data, required_fields):
        for field in required_fields:
            if field not in data:
                return False
        return True

    @staticmethod
    def validate_article_data(data):
        required_fields = ["id", "title", "content", "author", "link", "emotion", "post_time", "generated_time"]

        # Check for missing fields
        for field in required_fields:
            if field not in data:
                logging.error(f"Missing field: {field}")
                return False

        # Additional checks can be added here (e.g., type checks)
        # Example type checks (adjust types as necessary)
        if not isinstance(data['id'], int):
            logging.error("Field 'id' must be an integer")
            return False
        if not isinstance(data['title'], str):
            logging.error("Field 'title' must be a string")
            return False
        if not isinstance(data['content'], str):
            logging.error("Field 'content' must be a string")
            return False
        if not isinstance(data['author'], str):
            logging.error("Field 'author' must be a string")
            return False
        if not isinstance(data['link'], str):
            logging.error("Field 'link' must be a string")
            return False
        if not isinstance(data['emotion'], str):
            logging.error("Field 'emotion' must be a string")
            return False
        if not isinstance(data['post_time'], str):
            logging.error("Field 'post_time' must be a string")
            return False
        if not isinstance(data['generated_time'], str):
            logging.error("Field 'generated_time' must be a string")
            return False

        return True

    def insert(self, data):
        try:
            if self.validate_article_data(data):
                self.collection.insert_one(data)
                logging.info("Article inserted successfully")
            else:
                logging.error("Invalid article data format")
        except pymongo.errors.ServerSelectionTimeoutError as err:
            logging.error(f"MongoDB operation timeout: {err}")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")

    def read(self, query):
        try:
            return self.collection.find_one(query)
        except pymongo.errors.ServerSelectionTimeoutError as err:
            logging.error(f"MongoDB operation timeout: {err}")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            return None

    def update(self, query, new_data):
        try:
            if self.validate_article_data(new_data):
                self.collection.update_one(query, {"$set": new_data})
                logging.info("Article updated successfully")
            else:
                logging.error("Invalid article data format")
        except pymongo.errors.ServerSelectionTimeoutError as err:
            logging.error(f"MongoDB operation timeout: {err}")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")

    def delete(self, query):
        try:
            self.collection.delete_one(query)
            logging.info("Article deleted successfully")
        except pymongo.errors.ServerSelectionTimeoutError as err:
            logging.error(f"MongoDB operation timeout: {err}")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")


# Example usage:
mongo_adapter = MongoAdapter()
article_data = {
    "id": 1,
    "title": "Sample Title",
    "content": "Sample content.",
    "author": "Author Name",
    "link": "http://example.com",
    "emotion": "Happy",
    "post_time": "2024-01-01T00:00:00Z",
    "generated_time": "2024-01-01T01:00:00Z"
}
mongo_adapter.insert(article_data)
