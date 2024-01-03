from environs import Env
from pymongo.mongo_client import MongoClient

env = Env()
env.read_env()

MONGO_USER = env.str("MONGO_USER")
MONGO_PASSWORD = env.str("MONGO_PASSWORD")

uri = f"mongodb+srv://{MONGO_USER}:{MONGO_PASSWORD}@cluster0.tt0hiia.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(uri)

db = client["todo_db"]

collection = db["todo_collection"]

# print(db.list_collection_names())
