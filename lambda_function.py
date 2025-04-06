import json
import jwt
import bcrypt
from db import tasks_collection
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.get_database()
users_collection = db.users  

def lambda_handler(event, context):
    http_method = event.get("httpMethod")
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization"
    }
     
    if event['resource'] == "/login" and http_method == "POST":
        return login(event, headers)
     
    token = event.get("headers", {}).get("Authorization", "").replace("Bearer ", "")
    if token:
        try: 
            decoded_token = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            user_id = decoded_token["user_id"]
        except jwt.ExpiredSignatureError:
            return {
                "statusCode": 401,
                "body": json.dumps({"error": "Token has expired"}),
                "headers": headers
            }
        except jwt.InvalidTokenError:
            return {
                "statusCode": 401,
                "body": json.dumps({"error": "Invalid token"}),
                "headers": headers
            }
    else:
        return {
            "statusCode": 401,
            "body": json.dumps({"error": "Authorization token is required"}),
            "headers": headers
        }
 
    if http_method == "GET":
        return get_tasks(headers)
    elif http_method == "POST":
        return add_task(json.loads(event["body"]), headers)
    elif http_method == "PUT":
        return update_task(json.loads(event["body"]), headers)
    elif http_method == "DELETE":
        return delete_task(json.loads(event["body"]), headers)
    elif http_method == "OPTIONS":
        return {
            "statusCode": 200,
            "body": json.dumps({}),
            "headers": headers
        }
    else:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Unsupported method"}),
            "headers": headers
        }
 
def login(event, headers):
    try:
        body = json.loads(event["body"])
        email = body["email"]
        password = body["password"]
    except KeyError:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Email and password are required"}),
            "headers": headers
        }
  
    user = users_collection.find_one({"email": email})

    if not user:
        return {
            "statusCode": 401,
            "body": json.dumps({"error": "Invalid credentials"}),
            "headers": headers
        }
 
    if not bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
        return {
            "statusCode": 401,
            "body": json.dumps({"error": "Invalid credentials"}),
            "headers": headers
        }
 
    expiration = datetime.utcnow() + timedelta(hours=1)   
    payload = {
        "user_id": str(user["_id"]),
        "exp": expiration
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
 
    return {
        "statusCode": 200,
        "body": json.dumps({"token": token}),
        "headers": headers
    }
 
def get_tasks(headers):
    tasks = list(tasks_collection.find({}, {"_id": 0}))
    return {
        "statusCode": 200,
        "body": json.dumps(tasks),
        "headers": headers
    }
 
def add_task(task, headers):
    if "title" not in task or not task["title"].strip():
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Title is required and cannot be empty."}),
            "headers": headers
        }

    if "description" not in task or not task["description"].strip():
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Description is required and cannot be empty."}),
            "headers": headers
        }
 
    if len(task["title"]) > 100:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Title cannot exceed 100 characters."}),
            "headers": headers
        }
 
    if "due_date" in task:
        try: 
            datetime.strptime(task["due_date"], "%Y-%m-%d")
        except ValueError:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Due date must be in YYYY-MM-DD format."}),
                "headers": headers
            }
 
    result = tasks_collection.insert_one(task)
    return {
        "statusCode": 201,
        "body": json.dumps({"message": "Task added", "task_id": str(result.inserted_id)}),
        "headers": headers
    }
 
def update_task(task, headers):
    task_id = task.get("id")
     
    if not task_id:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Task ID is required for update."}),
            "headers": headers
        }

    try: 
        task["id"] = task["id"]
    except Exception as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid task ID."}),
            "headers": headers
        }
 
    if "title" in task and not task["title"].strip():
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Title cannot be empty."}),
            "headers": headers
        }

    if "description" in task and not task["description"].strip():
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Description cannot be empty."}),
            "headers": headers
        }

    result = tasks_collection.update_one({"id": task["id"]}, {"$set": task})

    if result.matched_count > 0:
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Task updated successfully"}),
            "headers": headers
        }
    else:
        return {
            "statusCode": 404,
            "body": json.dumps({"error": "Task not found"}),
            "headers": headers
        }
 
def delete_task(task, headers):
    task_id = task.get("id")
 
    if not task_id:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Task ID is required to delete."}),
            "headers": headers
        }

    try: 
        task["id"] = task["id"]
    except Exception as e:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid task ID."}),
            "headers": headers
        }
 
    result = tasks_collection.delete_one({"id": task["id"]})

    if result.deleted_count > 0:
        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Task deleted successfully"}),
            "headers": headers
        }
    else:
        return {
            "statusCode": 404,
            "body": json.dumps({"error": "Task not found"}),
            "headers": headers
        }