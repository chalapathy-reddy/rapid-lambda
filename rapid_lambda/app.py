import json
import logging

from .router import Router
from .executor import Executor
from .request import LambdaRequest
from .exceptions import HTTPException, NotFound


class LambdaApp:

    def __init__(self, logger=None, extra_resolvers=None):
        self.router = Router()
        self.executor = Executor(extra_resolvers=extra_resolvers)
        self.logger = logger or logging.getLogger("rapid_lambda")

    def route(self, path: str, method: str, log=True):

        def decorator(func):
            self.router.add(path, method, func, log=log)
            return func

        return decorator

    def add_routes(self, routes: dict):
        self.router.add_routes(routes)

    def handler(self, event, context):

        request = LambdaRequest(event, context)
        should_log = True

        try:

            route, path_params = self.router.resolve(request.path, request.method)

            if not route:
                raise NotFound()

            # Merge router-extracted path params into the request,
            # overriding anything API Gateway may have already populated.
            request.path_params = path_params

            handler = route["handler"]
            should_log = route["log"]

            if should_log:
                self.logger.info(
                    "incoming request",
                    extra={
                        "path": request.path,
                        "method": request.method,
                        "request_id": getattr(context, "aws_request_id", None)
                    }
                )

            result = self.executor.execute(handler, request)

            if should_log:
                self.logger.info("request completed")

            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps(result)
            }

        except HTTPException as e:

            if should_log:
                self.logger.warning(
                    "http error",
                    extra={"status": e.status_code, "detail": e.detail}
                )

            return {
                "statusCode": e.status_code,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"detail": e.detail})
            }

        except Exception:

            self.logger.exception("unhandled error")

            return {
                "statusCode": 500,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"detail": "Internal Server Error"})
            }
