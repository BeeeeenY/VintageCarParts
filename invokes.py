import requests
from flask import redirect,url_for  # Import redirect from Flask

SUPPORTED_HTTP_METHODS = set([
    "GET", "OPTIONS", "HEAD", "POST", "PUT", "PATCH", "DELETE"
])

def invoke_http(url, method='GET', json=None, redirect_url='/', **kwargs):

    code = 200
    result = {}

    try:
        if method.upper() in SUPPORTED_HTTP_METHODS:
            r = requests.request(method, url, json=json, **kwargs)
        else:
            raise Exception("HTTP method {} unsupported.".format(method))
    except Exception as e:
        code = 500
        result = {"code": code, "message": "Invocation of service fails: {}. {}".format(url, str(e))}
    
    if code not in range(200, 300):
        return result

    # Check if the response is empty or not JSON
    try:
        response_json = r.json()
    except ValueError:
        # Response is not JSON, return a redirect response
        redirect_url = url_for("/",param=json)
        return redirect(redirect_url)

    # Return the JSON response if successful
    return response_json
