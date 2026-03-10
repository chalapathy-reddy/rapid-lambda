
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
from rapid_lambda import LambdaApp, Depends, Query

app = LambdaApp()

def get_user():
    return {"id": "123"}

@app.route("/profile", "GET")
def profile(user = Depends(get_user)):
    return {"user": user}

@app.route("/login", "POST", log=False)
def login():
    return {"token": "abc"}

@app.route("/items", "GET")
def list_items(page: int = Query(default=1)):
    return {"page": page}

def lambda_handler(event, context):
    return app.handler(event, context)
```



## Contributing & License

* Source: `https://github.com/chalapathy-reddy/rapid-lambda`
* License: MIT

Contributions are welcome via PRs. Please follow the repository's contribution guidelines for tests and code style.
