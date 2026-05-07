"""
Executor — orchestrates parameter resolution and handler invocation.

Responsibilities (single):
  Walk a handler's signature, ask each resolver in order whether it can
  handle a parameter, delegate to the first match, then call the handler.

Executor knows nothing about Query, Path, Depends, or Pydantic.
Adding a new injection source = register a new resolver. This file stays closed.
"""

from __future__ import annotations

import inspect
from typing import List

from .resolvers import (
    ParameterResolver,
    RequestResolver,
    DependsResolver,
    QueryResolver,
    PathResolver,
    BodyModelResolver,
)
from .request import LambdaRequest


class Executor:

    def __init__(self, extra_resolvers: List[ParameterResolver] | None = None):
        """
        Resolvers are evaluated in order; first match wins.

        The order below is intentional:
          1. RequestResolver   — cheap annotation check, no ambiguity.
          2. DependsResolver   — must beat body/query so DI is always explicit.
          3. QueryResolver     — explicit Query(...) descriptor.
          4. PathResolver      — explicit Path(...) descriptor.
          5. BodyModelResolver — type-based fallback; checked last to avoid
                                 shadowing any explicit descriptor above.
          6. caller-supplied extras — placed after builtins so they can
                                      override only what they target.
        """
        self._resolvers: List[ParameterResolver] = [
            RequestResolver(),
            DependsResolver(self),   # passes self for recursive _call
            QueryResolver(),
            PathResolver(),
            BodyModelResolver(),
            *(extra_resolvers or []),
        ]

    # ── public ────────────────────────────────────────────────────────────────

    def execute(self, handler, request: LambdaRequest):
        return self._call(handler, request)

    # ── internal ──────────────────────────────────────────────────────────────

    def _call(self, func, request: LambdaRequest):
        sig = inspect.signature(func)
        kwargs = {}

        for name, param in sig.parameters.items():
            for resolver in self._resolvers:
                if resolver.can_resolve(param):
                    kwargs[name] = resolver.resolve(name, param, request)
                    break
            # parameters with no matching resolver are simply skipped;
            # Python will use their default values (or raise TypeError if none).

        return func(**kwargs)
