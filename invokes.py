import requests
from flask import redirect  # Import redirect from Flask

SUPPORTED_HTTP_METHODS = set([
    "GET", "OPTIONS", "HEAD", "POST", "PUT", "PATCH", "DELETE"
])

def invoke_http(url, method='GET', json=None, redirect_url='/', **kwargs):
    """A simple wrapper for requests methods.
       url: the url of the http service;
       method: the http method;
       json: the JSON input when needed by the http method;
       redirect_url: the URL to redirect to if the call succeeds;
       return: a redirect response if the call succeeds;
            otherwise, return a JSON object with a "code" name-value pair.
    """
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
        return redirect(redirect_url)

    # Return the JSON response if successful
    return response_json
