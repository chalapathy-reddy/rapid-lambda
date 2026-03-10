class Router:

    def __init__(self):
        self._routes = {}

    def add(self, path: str, method: str, handler, log=True):
        self._routes[(path, method.upper())] = {
            "handler": handler,
            "log": log
        }

    def add_routes(self, routes: dict):
        for (path, method), config in routes.items():
            if callable(config):
                self.add(path, method, config)
            elif isinstance(config, dict):
                self.add(path, method, config["handler"], log=config.get("log", True))
            else:
                raise ValueError(
                    f"Route config for ({path}, {method}) must be a callable or dict "
                    "with 'handler' key, e.g. {'handler': fn, 'log': False}"
                )

    def resolve(self, path: str, method: str):
        return self._routes.get((path, method.upper()))