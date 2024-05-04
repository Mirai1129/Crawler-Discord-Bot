import pymongo


class MongoDBAdapter:
    def __init__(self, database_name):
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = None

    def is_database_exists(self, database_name):
        return database_name in self.client.list_database_names()

    def is_collection_exists(self, collection_name):
        return collection_name in self.db.list_collection_names()

    def is_query_exists(self, query_name):
        return query_name in self.db.list_collection_names()

    def create_database(self, database_name):
        if not self.is_database_exists(database_name):
            self.db = self.client[database_name]
            print("Database {} created".format(database_name))
        else:
            print("Database {} already exists".format(database_name))

    def create_collection(self, collection_name, schema):
        if not self.db:
            raise Exception("Database not created. Please create the database first.")

        if not self.is_collection_exists(collection_name):
            collection = self.db[collection_name]
            collection.create_index([("name", pymongo.TEXT)])
            print("Collection '{}' created.".format(collection_name))
        else:
            print("Collection '{}' already exists.".format(collection_name))

    def close_connection(self):
        self.client.close()


if __name__ == "__main__":
    # 定義資料庫名稱、表單名稱、結構和範例資料
    db_name = "your_database_name"
    coll_name = "your_collection_name"
    schema = {"name": "text", "age": "int"}  # 定義表單的結構
    data = [{"name": "John", "age": 30}, {"name": "Alice", "age": 25}]  # 插入範例資料

    # 初始化資料庫
    adapter = MongoDBAdapter(db_name)
    adapter.create_database(db_name)
    adapter.create_collection(coll_name, schema)
    adapter.close_connection()
