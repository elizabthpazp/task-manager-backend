from pymongo import MongoClient
import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://elizabthpazp:aYtuDczsMJSGwLfW@cluster0.xhdresy.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

client = MongoClient(MONGO_URI)
db = client.get_database("task-manager")
tasks_collection = db.get_collection("tasks")
