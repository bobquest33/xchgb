import calendar, hmac, hashlib, json, time, urllib, uuid, xchgb.aes
from django.conf import settings

class ResponseError(Exception):
    def __init__(self, code, text=None):
        self.code = code
        self.text = text if text is not None else "Unknown error"
    def __str__(self):
        return "%s (%d)" % (self.text, self.code)

def ksort(d):
    keys = d.keys()
    keys.sort()
    return [(key, d[key]) for key in keys]

def perform_request(request, **kwargs):
    kwargs['request'] = request
    kwargs['nonce'] = str(uuid.uuid4())
    kwargs['timestamp'] = str(calendar.timegm(time.gmtime()))
    kwargs['api_key'] = settings.TRANSACTION_API_KEY
    kwargs['version'] = 1

    # generate signature
    encoded = urllib.urlencode(ksort(kwargs))
    kwargs['signature'] = hmac.new(settings.TRANSACTION_API_SECRET, encoded, hashlib.sha1).hexdigest()

    # read response and convert to dict
    raw_response = urllib.urlopen(settings.TRANSACTION_API_URL, urllib.urlencode(kwargs)).read()
    response = json.loads(raw_response)

    if isinstance(response, dict) and 'error_code' in response:
        raise ResponseError(response['error_code'], response.get('error_text'))
    else:
        return response

class RequestProxyDispenser(object):
    def __getattr__(self, name):
        def request_proxy(**kwargs):
            return perform_request(name, **kwargs)
        return request_proxy

requests = RequestProxyDispenser()

def new_account(username, password, email=None):
    hashed_pw = hashlib.sha1(username + password).hexdigest()
    iv, crypt_email = xchgb.aes.encrypt(email) if email is not None else ""
    return requests.NewAccount(username=username, password=hashed_pw, email="%s;%s" % (iv, crypt_email))