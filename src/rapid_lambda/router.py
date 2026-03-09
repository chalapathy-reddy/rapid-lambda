
class Router:

    def __init__(self):
        self._routes = {}

    def add(self, path: str, method: str, handler, log=True):
        self._routes[(path, method.upper())] = {
            "handler": handler,
            "log": log
        }

    def add_routes(self, routes: dict):
        for (path, method), handler in routes.items():
            self.add(path, method, handler)

    def resolve(self, path: str, method: str):
        return self._routes.get((path, method.upper()))
