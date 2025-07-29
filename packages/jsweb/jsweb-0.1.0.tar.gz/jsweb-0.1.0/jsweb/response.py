import json as pyjson

def html(body, status="200 OK", headers=None):
    headers = headers or []
    headers.insert(0, ("Content-Type", "text/html"))
    return body, status, headers

def json(data, status="200 OK", headers=None):
    headers = headers or []
    headers.insert(0, ("Content-Type", "application/json"))
    body = pyjson.dumps(data)
    return body, status, headers
