
import re


def _compile(path: str):
    """
    Convert a path template like /users/{id}/posts/{post_id}
    into a compiled regex and an ordered list of param names.
    """
    param_names = []

    def replacer(match):
        param_names.append(match.group(1))
        return r"([^/]+)"

    pattern = re.sub(r"\{(\w+)\}", replacer, path)
    return re.compile(f"^{pattern}$"), param_names


class Router:

    def __init__(self):
        # list of (compiled_regex, param_names, method, route_config)
        # kept in insertion order so more specific routes added first take priority
        self._routes = []

    def add(self, path: str, method: str, handler, log=True):
        regex, param_names = _compile(path)
        self._routes.append((regex, param_names, method.upper(), {
            "handler": handler,
            "log": log,
            "path_template": path,
        }))

    def add_routes(self, routes: dict):
        for (path, method), config in routes.items():
            if callable(config):
                self.add(path, method, config)
            elif isinstance(config, dict):
                self.add(path, method, config["handler"], log=config.get("log", True))
            else:
                raise ValueError(
                    f"Route config for ({path}, {method}) must be a callable or dict "
                    "with 'handler' key, e.g. {{'handler': fn, 'log': False}}"
                )

    def resolve(self, path: str, method: str):
        method = method.upper()
        for regex, param_names, route_method, config in self._routes:
            if route_method != method:
                continue
            match = regex.match(path or "")
            if match:
                path_params = dict(zip(param_names, match.groups()))
                return config, path_params
        return None, {}
