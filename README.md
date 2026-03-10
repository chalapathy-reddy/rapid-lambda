
# rapid_lambda

Lightweight FastAPI-style dependency injection and routing for AWS Lambda.

Supports:
- Routing
- Dependency Injection
- Query parameter injection
- Structured exceptions
- Optional request logging with route-level control

Example:

```python
from rapid_lambda import LambdaApp, Depends, Query, Output, \
    HTTP_unauthorized, HTTP_not_found, \
    HTTP_bad_request, HTTP_server_error, \
    success_response, error_response

app = LambdaApp()


# ─── Dependencies ────────────────────────────────────────────

def get_user():
    return {"id": "123"}


@app.route("/profile", "GET")
def profile(user=Depends(get_user)):
    try:
        if not user:
            return error_response(statusCode=401, message="Unauthorized")
            # {"status": "error", "message": "Unauthorized"} → 401

        if not user.get("id"):
            return error_response(statusCode=400, message="User ID is missing")
            # {"status": "error", "message": "User ID is missing"} → 400

        return success_response(data=user)
        # {"status": "success", "data": {"id": "123"}} → 200

    except Exception as e:
        return error_response(statusCode=500, message=str(e))
        # {"status": "error", "message": "..."} → 500


@app.route("/login", "POST", log=False)
def login():
    try:
        token = "abc"

        if not token:
            return error_response(statusCode=500, message="Token generation failed")
            # {"status": "error", "message": "Token generation failed"} → 500

        return success_response(data={"token": token})
        # {"status": "success", "data": {"token": "abc"}} → 200

    except ValueError as e:
        return error_response(statusCode=400, message=str(e))
        # {"status": "error", "message": "..."} → 400

    except Exception as e:
        return error_response(statusCode=500, message=str(e))
        # {"status": "error", "message": "..."} → 500


@app.route("/items", "GET")
def list_items(page: int = Query(default=1)):
    try:
        if page < 1:
            return error_response(statusCode=400, message="page must be a positive integer")
            # {"status": "error", "message": "page must be a positive integer"} → 400

        items = []                          # replace with actual DB query

        if not items:
            return error_response(statusCode=404, message="No items found")
            # {"status": "error", "message": "No items found"} → 404

        return success_response(data={"items": items, "page": page})
        # {"status": "success", "data": {"items": [...], "page": 1}} → 200

    except ValueError as e:
        return error_response(statusCode=400, message=str(e))
        # {"status": "error", "message": "..."} → 400

    except Exception as e:
        return error_response(statusCode=500, message=str(e))
        # {"status": "error", "message": "..."} → 500


def lambda_handler(event, context):
    return app.handler(event, context)
```



## Contributing & License

* Source: `https://github.com/chalapathy-reddy/rapid-lambda`
* License: MIT

Contributions are welcome via PRs. Please follow the repository's contribution guidelines for tests and code style.
