import bcrypt, bitcoinrpc as bitcoin, errors, inspect
from decorator import decorator
from django.db import transaction
from txdb.models import Account

@decorator
def db_transaction(f, *args, **kwargs):
    """Proxy to Django's commit_on_success decorator that preserves method signatures."""
    return transaction.commit_on_success(f)(*args, **kwargs)

@decorator
def authenticate_user(f, *args, **kwargs):
    """Ensures that the provided username and password are OK."""
    username = kwargs.get('username')
    password = kwargs.get('password')

    # what if username/password were provided as regular args?
    spec = inspect.getargspec(f)
    if username is None and 'username' in spec[0]:
        username = args[spec[0].index('username')]
    if password is None and 'password' in spec[0]:
        password = args[spec[0].index('password')]

    if not isinstance(username, str) or not isinstance(password, str):
        raise errors.AuthenticationFailedError()

    try:
        account = Account.objects.get(username=username, allow_auth=True)
    except Account.DoesNotExist:
        raise errors.AuthenticationFailedError()

    if bcrypt.hashpw(password, account.password) == account.password:
        return f(*args, **kwargs)
    else:
        raise errors.AuthenticationFailedError()

def hash_password(password):
    # bcrypt with default difficulty
    return bcrypt.hashpw(password, bcrypt.gensalt())

def get_bitcoin_conn():
    """Gets a connection to the Bitcoin wallet."""
    try:
        return bitcoin.connect_to_local()
    except:
        raise errors.BitcoinConnectionError()
