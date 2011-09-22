import calendar, errors, hashlib, hmac, inspect, settings, time, urllib

from accounts import register_account, change_password, change_email, query_balances
from orders import place_buy_order, place_sell_order, cancel_order, query_orders
from market.gbp import historical_prices, market_depth, accumulated_market_depth,
    market_summary, query_transactions
from transfers import get_deposit_reference, request_withdrawal, confirm_withdrawal,
    decline_withdrawal, confirm_deposit, decline_deposit, query_deposits, query_withdrawals

REQUEST_TABLE = {
    # app stuff
    'RegisterAccount':     register_account,
    'ChangePassword':      change_password,
    'ChangeEmail':         change_email,
    'QueryBalances':       query_balances,
    'PlaceBuyOrder':       place_buy_order,
    'PlaceSellOrder':      place_sell_order,
    'CancelOrder':         cancel_order,
    'QueryOrders':         query_orders,
    'HistoricalPrices':    historical_prices,
    'MarketDepth':         market_depth,
    'AccumulMarketDepth':  accumulated_market_depth,
    'MarketSummary':       market_summary,
    'QueryTransactions':   query_transactions,
    'GetDepositRef':       get_deposit_reference,
    'RequestWithdrawal':   request_withdrawal,
    'QueryDeposits':       query_deposits,
    'QueryWithdrawals':    query_withdrawals,
    # admin stuff
    'ConfirmWithdrawal':   confirm_withdrawal,
    'DeclineWithdrawal':   decline_withdrawal,
    'ConfirmDeposit':      confirm_deposit,
    'DeclineDeposit':      decline_deposit,
}

def handle_request(ip, request):
    if request.get('version') != '1':
        raise errors.UnsupportedVersionError()

    if request.get('api_key') not in settings.API_KEYS:
        raise errors.InvalidAPIKeyError()

    if not is_nonce_ok(request):
        raise errors.InvalidNonceError()

    if not is_signature_ok(request):
        raise errors.InvalidSignatureError()

    if not is_timestamp_ok(request):
        raise errors.InvalidTimestampError()

    if request.get('request') not in REQUEST_TABLE:
        raise errors.InvalidRequestError()

    if not is_request_authorized(request):
        raise errors.UnauthorizedRequestError()

    if not is_ip_authorized(ip, request):
        raise errors.UnauthorizedIPAddressError(ip)

    return dispatch_request(ip, request)

def dispatch_request(ip, request):
    method = REQUEST_TABLE[request['request']]
    spec = inspect.getargspec(method)
    
    # figure out what args are required
    if spec[3] is not None:
        required_args = set(spec[0][:-len(spec[3])]) # set of args with no default value
    else:
        required_args = set(spec[0]) # all args are required

    # remove compulsory stuff from request dict, add IP
    del request['version']
    del request['api_key']
    del request['nonce']
    del request['signature']
    del request['timestamp']
    del request['request']
    request['ip'] = ip

    # check required args are provided and we haven't been sent superfluous args
    keys = set(request.keys())
    if not keys.issubset(spec[0]):
        raise errors.InvalidArgumentError() # some request args aren't in method args
    elif not required_args.issubset(keys):
        raise errors.InvalidArgumentError() # some required method args aren't in request args

    return method(**request) # call into target method

def is_nonce_ok(request):
    return 'nonce' in request

def is_signature_ok(request):
    keys = request.keys()
    keys.sort()
    encoded = urllib.urlencode([(key, request[key]) for key in filter(lambda a: a != 'signature', keys)])
    correct_sig = hmac.new(settings.API_KEYS[request['api_key']]['secret'], encoded, hashlib.sha1).hexdigest()
    return request['signature'] == correct_sig

def is_timestamp_ok(request):
    if 'timestamp' not in request:
        return False
    ts_now = calendar.timegm(time.gmtime())
    try:
        return abs(ts_now - int(request['timestamp'])) <= settings.MAX_TIMESTAMP_DELTA
    except TypeError: # timestamp isn't an int, so fail
        return False

def is_request_authorized(request):
    allowed_reqs = settings.API_KEYS[request['api_key']].get('requests')
    return allowed_reqs is None or request['request'] in allowed_reqs

def is_ip_authorized(ip, request):
    allowed_ips = settings.API_KEYS[request['api_key']].get('allowed_ips')
    return allowed_ips is None or ip in allowed_ips
