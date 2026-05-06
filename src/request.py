
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

    def json(self):
        if self._json is None:
            try:
                self._json = json.loads(self._raw_body or "{}")
            except json.JSONDecodeError:
                raise BadRequest("Invalid JSON in request body")
        return self._json
