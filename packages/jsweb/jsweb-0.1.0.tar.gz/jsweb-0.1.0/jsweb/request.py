from urllib.parse import parse_qs

class Request:
    def __init__(self, environ):
        self.method = environ.get("REQUEST_METHOD", "GET").upper()
        self.path = environ.get("PATH_INFO", "/")
        self.query = self._parse_query(environ.get("QUERY_STRING", ""))
        self.headers = self._parse_headers(environ)
        self.body = self._parse_body(environ)
        self.form = self._parse_form(environ)

    def _parse_query(self, query_string):
        return {k: v[0] for k, v in parse_qs(query_string).items()}

    def _parse_headers(self, environ):
        return {
            k[5:].replace("_", "-").title(): v
            for k, v in environ.items()
            if k.startswith("HTTP_")
        }

    def _parse_body(self, environ):
        try:
            length = int(environ.get("CONTENT_LENGTH", 0))
            return environ["wsgi.input"].read(length).decode("utf-8")
        except:
            return ""

    def _parse_form(self, environ):
        if self.method == "POST" and "application/x-www-form-urlencoded" in environ.get("CONTENT_TYPE", ""):
            return {k: v[0] for k, v in parse_qs(self.body).items()}
        return {}
