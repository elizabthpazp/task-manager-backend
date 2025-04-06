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
      
    path = event.get("resource") or event.get("path")

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