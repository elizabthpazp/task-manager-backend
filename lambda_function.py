import json
from db import tasks_collection
from bson import ObjectId
from datetime import datetime

def lambda_handler(event, context):
    http_method = event.get("httpMethod")
    
    if http_method == "GET":
        return get_tasks()
    elif http_method == "POST":
        return add_task(json.loads(event["body"]))
    elif http_method == "PUT":
        return update_task(json.loads(event["body"]))
    elif http_method == "DELETE":
        return delete_task(json.loads(event["body"]))
    else:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Unsupported method"})
        }

def get_tasks():
    tasks = list(tasks_collection.find({}, {"_id": 0}))
    return {"statusCode": 200, "body": json.dumps(tasks)}

def add_task(task):
    task["createdAt"] = datetime.utcnow()
    result = tasks_collection.insert_one(task)
    return {"statusCode": 201, "body": json.dumps({"message": "Task added", "task_id": str(result.inserted_id)})}

def update_task(task):
    task_id = task.get("_id")
    if not task_id:
        return {"statusCode": 400, "body": json.dumps({"error": "Task ID is required"})}

    task["_id"] = ObjectId(task["_id"])
    result = tasks_collection.update_one({"_id": task["_id"]}, {"$set": task})

    if result.matched_count > 0:
        return {"statusCode": 200, "body": json.dumps({"message": "Task updated successfully"})}
    else:
        return {"statusCode": 404, "body": json.dumps({"error": "Task not found"})}

def delete_task(task):
    task_id = task.get("_id")
    if not task_id:
        return {"statusCode": 400, "body": json.dumps({"error": "Task ID is required"})}

    task["_id"] = ObjectId(task["_id"])
    result = tasks_collection.delete_one({"_id": task["_id"]})

    if result.deleted_count > 0:
        return {"statusCode": 200, "body": json.dumps({"message": "Task deleted successfully"})}
    else:
        return {"statusCode": 404, "body": json.dumps({"error": "Task not found"})}
