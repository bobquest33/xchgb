import sys, os
sys.path.append('/work/xchgb/txserv') # temporary, location of txdb module
os.environ['DJANGO_SETTINGS_MODULE'] = 'txapi.settings'

# enables logging of sql queries in Django
DEBUG = True

INSTALLED_APPS = ('txdb', 'south')  # required by Django

API_KEYS = {
    'iqb5ZHegFbjhbeDRSRTp': {
        'secret': 'DXWSPWLn7jXBUdmnC9A1eK4g5Ywm5WamK8g6dHzq',
        'allowed_ips': ('127.0.0.1',),
    },
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'xchgb',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '',
    }
}

MAX_TIMESTAMP_DELTA = 5                     # max delta between user and server UTC timestamps
ORDER_QUERY_HARD_LIMIT = 100                # max orders you can get for 1 request
HISTORICAL_PRICES_ROW_LIMIT = 500           # max rows you can get from historical_prices
ACCUMULATED_MARKET_DEPTH_RESOLUTION = 0.02  # price-step for the accumulated market depth results
MIN_BITCOIN_DEPOSIT_CONFIRMATIONS = 6       # minimum number of confirmations before deposit is accepted
DEFAULT_TRADE_COMMISSION = 0                # default commission multiplier between 0 and 1