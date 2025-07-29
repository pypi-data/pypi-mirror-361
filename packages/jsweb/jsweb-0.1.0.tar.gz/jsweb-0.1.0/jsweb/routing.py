# jsweb/routing.py

class Router:
    def __init__(self):
        self.routes = {}

    def route(self, path, methods=None):
        if methods is None:
            methods = ["GET"]

        def decorator(func):
            for method in methods:
                self.routes[(path, method.upper())] = func
            return func
        return decorator

    def resolve(self, path, method):
        return self.routes.get((path, method.upper()), None)
