from decimal import Decimal
from datetime import datetime
import json

class Output(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif type(obj).__name__ == "RowMapping":
            return dict(obj)
        elif isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS"
}


def _encode(data):
    return json.dumps(data, cls=Output)


def HTTP_unauthorized():
    return {
        "statusCode": 401,
        "headers": CORS_HEADERS,
        "body": _encode({"error": "Unauthorized"})
    }

def HTTP_not_found(data):
    return {
        "statusCode": 404,
        "headers": CORS_HEADERS,
        "body": _encode({"error": "Not Found", "details": data})
    }

def HTTP_bad_request(data):
    return {
        "statusCode": 400,
        "headers": CORS_HEADERS,
        "body": _encode({"error": "Bad Request", "details": data})
    }

def HTTP_server_error(data):
    return {
        "statusCode": 500,
        "headers": CORS_HEADERS,
        "body": _encode({"error": "Internal Server Error", "details": data})
    }

def success_response(**kwargs):
    return {
        "statusCode": 200,
        "headers": CORS_HEADERS,
        "body": _encode({"status": "success", **kwargs})
    }

def error_response(statusCode=400, message="Error occurred"):
    return {
        "statusCode": statusCode,
        "headers": CORS_HEADERS,
        "body": _encode({"status": "error", "message": message})
    }