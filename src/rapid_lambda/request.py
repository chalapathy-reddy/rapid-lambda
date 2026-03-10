
import json

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
            self._json = json.loads(self._raw_body or "{}")
        return self._json
