import json
from db import tasks_collection
from bson import ObjectId
from datetime import datetime

def lambda_handler(event, context):
    http_method = event.get("httpMethod")

    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type, Authorization"
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

def get_tasks(headers):
    tasks = list(tasks_collection.find({}, {"_id": 0}))
    return {
        "statusCode": 200,
        "body": json.dumps(tasks),
        "headers": headers
    }

def add_task(task, headers):
    result = tasks_collection.insert_one(task)
    return {
        "statusCode": 201,
        "body": json.dumps({"message": "Task added", "task_id": str(result.inserted_id)}),
        "headers": headers
    }

def update_task(task, headers):
    task_id = task.get("_id")
    if not task_id:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Task ID is required"}),
            "headers": headers
        }

    task["_id"] = ObjectId(task["_id"])
    result = tasks_collection.update_one({"_id": task["_id"]}, {"$set": task})

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
    task_id = task.get("_id")
    if not task_id:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Task ID is required"}),
            "headers": headers
        }

    task["_id"] = ObjectId(task["_id"])
    result = tasks_collection.delete_one({"_id": task["_id"]})

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