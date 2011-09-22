import cgi, errors, json, os, settings, sys, urlparse
from django.db import connection # for query count

DEFAULT_HEADERS = [('Content-type', 'application/json')]

globals()['last_query_count'] = 0 # Python, this is why we can't have nice things.

def application(environ, start_response):
    import dispatcher # don't import this elsewhere

    if environ['REQUEST_METHOD'] != 'POST':
        return handle_exception(errors.UnsupportedRequestMethodError(environ['REQUEST_METHOD']), start_response)

    # parse POST data into a dict, using first value for each item
    params = cgi.FieldStorage(fp=environ['wsgi.input'], environ=environ, keep_blank_values=True)
    params = dict([(k, params.getfirst(k)) for k in params])
    print "---\nRequest from %s\nParameters: %s" % (environ['REMOTE_ADDR'], params)

    try:
        response = dispatcher.handle_request(environ['REMOTE_ADDR'], params)
    except Exception as error:
        return handle_exception(error, start_response)

    query_count = len(connection.queries) - globals()['last_query_count']
    globals()['last_query_count'] = len(connection.queries)
    print "Queries: %s" % query_count
    response = prepare_response("200 OK", response, start_response)
    print "Response: %s" % response
    return response

def handle_exception(error, start_response):
    if isinstance(error, errors.TransactionAPIError):
        response = {'error_code': error.code, 'error_text': error.text}
        return prepare_response(error.get_http_status_response(), response, start_response)
    else:
        print "Error: %s" % repr(error)
        response = {'error_code': errors.ERR_PYTHON_EXCEPTION, 'error_text': "Application exception"}
        return prepare_response("500 Internal Server Error", response, start_response)

def prepare_response(status, obj, start_response):
    start_response(status, DEFAULT_HEADERS)
    json_response = json.dumps(obj)
    return json_response

def start_development_server():
    from wsgiref.simple_server import make_server
    srv = make_server('localhost', 8080, application)
    srv.serve_forever()

if __name__ == '__main__':
    start_development_server()
