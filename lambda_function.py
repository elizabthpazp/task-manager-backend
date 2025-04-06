import json
import jwt
from db import tasks_collection
from db import users_collection
from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")

def lambda_handler(event, context):
    http_method = event.get("httpMethod")
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization"
    }
      
    path = event.get("resource") or event.get("path") or ""

    if "/login" in path and http_method == "POST":
        return login(event, headers) 
    
    if "/register" in path and http_method == "POST":
        return register(event, headers)

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

def register(event, headers):
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
      
    existing_user = users_collection.find_one({"email": email})
    if existing_user:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Email is already registered"}),
            "headers": headers
        }
 
    user_data = {
        "email": email,
        "password": password,  
        "created_at": datetime.utcnow()
    }
 
    result = users_collection.insert_one(user_data)
   
    expiration = datetime.utcnow() + timedelta(hours=1)  
    payload = {
        "user_id": str(result.inserted_id), 
        "exp": expiration
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    
    return {
        "statusCode": 201,
        "body": json.dumps({"message": "User registered successfully", "token": token}),
        "headers": headers
    }

# Adaptación de las funciones de db.py para integrarlas con las respuestas HTTP

def get_tasks(headers):
    try:
        tasks = tasks_collection.find({}, {"_id": 0})
        return {
            "statusCode": 200,
            "body": json.dumps(list(tasks)),
            "headers": headers
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Error fetching tasks"}),
            "headers": headers
        }

def add_task(body, headers):
    try:
        task_id = tasks_collection.insert_one(body).inserted_id
        body["_id"] = str(task_id)
        return {
            "statusCode": 201,
            "body": json.dumps(body),
            "headers": headers
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Error adding task"}),
            "headers": headers
        }

def update_task(body, headers):
    task_id = body.get("_id")
    if not task_id:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Task ID is required"}),
            "headers": headers
        }

    result = tasks_collection.update_one({"_id": ObjectId(task_id)}, {"$set": body})

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

def delete_task(body, headers):
    task_id = body.get("_id")
    if not task_id:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Task ID is required"}),
            "headers": headers
        }

    result = tasks_collection.delete_one({"_id": ObjectId(task_id)})

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