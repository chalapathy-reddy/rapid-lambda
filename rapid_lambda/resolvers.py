"""
Parameter resolvers — one class per injection source.

Design contract
---------------
- `ParameterResolver` is the abstraction (Protocol).  Executor depends only on it.
- Each resolver decides for itself whether it can handle a given parameter
  (can_resolve) and how to produce the value (resolve).
- Adding a new source (headers, cookies, form-data) = add a new resolver class.
  Executor.py is never touched again → OCP satisfied.
- Each resolver owns exactly one concern → SRP satisfied.
- Executor depends on the Protocol, not on Query/Path/Depends → DIP satisfied.
"""

from __future__ import annotations

import inspect
from typing import TYPE_CHECKING, Protocol, runtime_checkable

from .exceptions import BadRequest

if TYPE_CHECKING:
    from .request import LambdaRequest


@runtime_checkable
class ParameterResolver(Protocol):
    """
    Abstraction every resolver must satisfy.

    can_resolve  — cheap guard; called first so resolvers are skipped fast.
    resolve      — produces the final value or raises BadRequest.
    """

    def can_resolve(self, param: inspect.Parameter) -> bool:
        ...

    def resolve(self, name: str, param: inspect.Parameter, request: "LambdaRequest") -> object:
        ...


# ── helpers ───────────────────────────────────────────────────────────────────

def _coerce(raw: str, annotation, label: str, name: str) -> object:
    """Cast `raw` to `annotation` or raise BadRequest."""
    if annotation is inspect.Parameter.empty:
        return raw
    try:
        return annotation(raw)
    except Exception:
        raise BadRequest(f"Invalid value for {label} parameter '{name}'")


# ── concrete resolvers ────────────────────────────────────────────────────────

class RequestResolver:
    """Injects the raw LambdaRequest when a parameter is typed as one."""

    def can_resolve(self, param: inspect.Parameter) -> bool:
        from .request import LambdaRequest  # local import avoids circular at module level
        return param.annotation is LambdaRequest

    def resolve(self, name: str, param: inspect.Parameter, request: "LambdaRequest") -> object:
        return request


class DependsResolver:
    """
    Resolves Depends(...) by recursively calling the Executor.

    Receives the executor via constructor injection so this resolver
    never has to import or instantiate Executor itself (DIP).
    """

    def __init__(self, executor):
        self._executor = executor

    def can_resolve(self, param: inspect.Parameter) -> bool:
        from .dependencies import Depends
        return isinstance(param.default, Depends)

    def resolve(self, name: str, param: inspect.Parameter, request: "LambdaRequest") -> object:
        return self._executor._call(param.default.dependency, request)


class QueryResolver:
    """Resolves Query(...) descriptors from request.query_params."""

    def can_resolve(self, param: inspect.Parameter) -> bool:
        from .query import Query
        return isinstance(param.default, Query)

    def resolve(self, name: str, param: inspect.Parameter, request: "LambdaRequest") -> object:
        raw = request.query_params.get(name)
        if raw is None:
            if param.default.default is not None:
                return param.default.default
            raise BadRequest(f"Missing query parameter '{name}'")
        return _coerce(raw, param.annotation, "query", name)


class PathResolver:
    """Resolves Path(...) descriptors from request.path_params."""

    def can_resolve(self, param: inspect.Parameter) -> bool:
        from .path import Path
        return isinstance(param.default, Path)

    def resolve(self, name: str, param: inspect.Parameter, request: "LambdaRequest") -> object:
        raw = request.path_params.get(name)
        if raw is None:
            if param.default.default is not None:
                return param.default.default
            raise BadRequest(f"Missing path parameter '{name}'")
        return _coerce(raw, param.annotation, "path", name)


class BodyModelResolver:
    """
    Resolves parameters whose annotation is a Pydantic BaseModel subclass
    by deserialising request.json() into the model.
    """

    def can_resolve(self, param: inspect.Parameter) -> bool:
        try:
            from pydantic import BaseModel
            ann = param.annotation
            return (
                ann is not inspect.Parameter.empty
                and isinstance(ann, type)
                and issubclass(ann, BaseModel)
            )
        except ImportError:
            return False

    def resolve(self, name: str, param: inspect.Parameter, request: "LambdaRequest") -> object:
        from pydantic import ValidationError
        try:
            return param.annotation(**request.json())
        except ValidationError as e:
            raise BadRequest(e.errors())
