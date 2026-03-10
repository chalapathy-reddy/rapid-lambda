import inspect
from pydantic import BaseModel, ValidationError

from .dependencies import Depends
from .query import Query
from .exceptions import BadRequest
from .request import LambdaRequest


class Executor:

    def execute(self, handler, request: LambdaRequest):
        return self._call(handler, request)

    def _call(self, func, request: LambdaRequest):

        sig = inspect.signature(func)
        kwargs = {}

        for name, param in sig.parameters.items():

            annotation = param.annotation

            if annotation == LambdaRequest:
                kwargs[name] = request
                continue

            if isinstance(param.default, Depends):
                dep = param.default.dependency
                kwargs[name] = self._call(dep, request)
                continue

            if isinstance(param.default, Query):

                raw = request.query_params.get(name)

                if raw is None:
                    if param.default.default is not None:
                        kwargs[name] = param.default.default
                        continue
                    raise BadRequest(f"Missing query parameter '{name}'")

                if annotation is inspect.Parameter.empty:
                    kwargs[name] = raw
                else:
                    try:
                        kwargs[name] = annotation(raw)
                    except Exception:
                        raise BadRequest(f"Invalid value for '{name}'")

                continue

            if isinstance(annotation, type) and issubclass(annotation, BaseModel):

                try:
                    kwargs[name] = annotation(**request.json())
                except ValidationError as e:
                    raise BadRequest(e.errors())

                continue

        return func(**kwargs)