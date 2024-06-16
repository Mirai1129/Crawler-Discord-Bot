import datetime
import logging
import os
from datetime import datetime

import dotenv
import pymongo
from pymongo import errors

dotenv.load_dotenv()


class MongoAdapter:
    def __init__(self, db_name="Crawler", collection_name="ptt"):
        try:
            self.client = pymongo.MongoClient(os.getenv('MONGODB_CONNECTION_URL'), serverSelectionTimeoutMS=5000)
            self.db = self.client[db_name]
            self.collection = self.db[collection_name]
            logging.basicConfig(level=logging.INFO, format='[MONGODB_INFO] %(message)s')
        except pymongo.errors.ServerSelectionTimeoutError as err:
            logging.error(f"MongoDB connection timeout: {err}")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")

    @staticmethod
    def validate_article_data(data):
        required_fields = ["title", "content", "author", "link", "emotion", "post_time", "generated_time",
                           "result_id"]

        # Check for missing fields
        for field in required_fields:
            if field not in data:
                logging.error(f"Missing field: {field}")
                return False

        # Additional checks can be added here (e.g., type checks)
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
        if not isinstance(data['post_time'], datetime):
            logging.error("Field 'post_time' must be a datetime")
            return False
        if not isinstance(data['generated_time'], datetime):
            logging.error("Field 'generated_time' must be a datetime")
            return False
        if not isinstance(data['result_id'], str):
            logging.error("Field 'result_id' must be a string")
            return False

        return True

    def insert(self, data):
        try:
            if self.validate_article_data(data):
                if self.collection.find_one(
                        {
                            "title": data["title"],
                            "content": data["content"],
                            "author": data["author"],
                            "link": data["link"],
                            "post_time": data["post_time"],
                            "result_id": data["result_id"]
                        }
                ):
                    logging.error("Duplicate article. Article not inserted.")
                else:
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

    def find_one_lasted(self, query):
        """
        Find the latest document in the database based on a specific field and return it.

        Args:
            query (str): The field name by which the documents will be sorted (-1 for descending order).

        Returns:
            dict | None: The matching document dictionary, or None if no matching document is found.
        """
        try:
            return self.collection.find_one(sort=[(query, -1)])
        except pymongo.errors.ServerSelectionTimeoutError as err:
            logging.error(f"MongoDB operation timeout: {err}")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            return None

    def is_duplicate_article(self, data):
        if self.collection.find_one(
                {
                    "title": data["title"],
                    "content": data["content"],
                    "author": data["author"],
                    "link": data["link"],
                    "post_time": data["post_time"]
                }
        ):
            logging.error("Duplicate article. Article not inserted.")
            return True
        else:
            return False

    def get_emotions_summary(self, result_id: str = None):
        """
        Retrieve the summary of emotions grouped by their counts.

        Args:
            result_id (str, optional): The result_id to filter the documents. If None, it will summarize all documents.

        Returns:
            dict: A dictionary containing the summary of emotions and their counts, or an error message if no records found.
        """
        try:
            # Define the match stage in the aggregation pipeline
            match_stage = {"$match": {"result_id": result_id}} if result_id else {"$match": {}}

            # Define the group stage in the aggregation pipeline
            group_stage = {"$group": {"_id": "$emotion", "count": {"$sum": 1}}}

            # Build the complete pipeline
            pipeline = [match_stage, group_stage]

            # Execute the aggregation pipeline
            results = list(self.collection.aggregate(pipeline))

            if not results:
                logging.info(f"No records found for result_id: {result_id if result_id else 'all'}")
                return {"error": "No records found", "result_id": result_id}

            # Build the emotions summary from the results
            emotions_summary = {result["_id"]: result["count"] for result in results}
            logging.info(f"Emotions summary for result_id {result_id if result_id else 'all'}: {emotions_summary}")
            return {"emotions_summary": emotions_summary}

        except pymongo.errors.ServerSelectionTimeoutError as err:
            logging.error(f"MongoDB operation timeout: {err}")
            return {"error": "MongoDB operation timeout", "details": str(err)}
        except pymongo.errors.PyMongoError as err:
            logging.error(f"An error occurred with MongoDB: {err}")
            return {"error": "MongoDB error", "details": str(err)}

    def get_titles_and_links_by_result_id(self, result_id: str):
        """
        Retrieve all titles and links for documents with the specified result_id.

        Args:
            result_id (str): The result_id to filter the documents.

        Returns:
            list: A list of dictionaries containing the 'title' and 'link' fields for the matching documents.
        """
        try:
            # Using the find method to search for documents with the specified result_id
            cursor = self.collection.find(
                {"result_id": result_id},
                {"title": 1, "link": 1, "_id": 0}  # Include only the 'title' and 'link' fields, exclude '_id'
            )
            results = list(cursor)

            if not results:
                logging.info(f"No records found for result_id: {result_id}")
                return {"error": "No records found", "result_id": result_id}

            logging.info(f"Titles and links retrieved for result_id {result_id}: {results}")
            return results

        except pymongo.errors.ServerSelectionTimeoutError as err:
            logging.error(f"MongoDB operation timeout: {err}")
            return {"error": "MongoDB operation timeout", "details": str(err)}
        except pymongo.errors.PyMongoError as err:
            logging.error(f"An error occurred with MongoDB: {err}")
            return {"error": "MongoDB error", "details": str(err)}


if __name__ == '__main__':
    file_name = __file__.split("\\")[-1].split(".")[0]
    logging.info(f"{file_name} has been loaded")
