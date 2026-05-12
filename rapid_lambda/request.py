
import json

from .exceptions import BadRequest


class LambdaRequest:
    def __init__(self, event: dict, context):
        self.event = event
        self.context = context

        self.headers = event.get("headers") or {}
        self.method = event.get("httpMethod")
        self.path = event.get("path")

        self.query_params = event.get("queryStringParameters") or {}
        self.path_params = event.get("pathParameters") or {}

        self._raw_body = event.get("body")
        self._json = None

    @property
    def body(self):
        return self._raw_body
    
    def json(self):
        if self._json is None:
            try:
                self._json = json.loads(self._raw_body or "{}") if isinstance(self._raw_body, str) else self._raw_body
            except json.JSONDecodeError:
                raise BadRequest("Invalid JSON in request body")
        return self._json
