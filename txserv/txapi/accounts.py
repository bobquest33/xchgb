import base64, bitcoinrpc as bitcoin, errors, utils
from txdb.models import *

@utils.db_transaction
def register_account(ip, username, password, email=None):
    if Account.objects.filter(username__iexact=username).count() > 0:
        raise errors.UsernameTakenError(username)

    account = Account(username=username, password=utils.hash_password(password), email=email, commission_rate=settings.DEFAULT_TRADE_COMMISSION)
    try:
        account.full_clean()
        account.save()
    except:
        raise errors.AccountValidationError(username, password, email)

    # create a balance for each currency
    for currency in Currency.objects.all():
        Balance(account=account, currency=currency).save()

    # get deposit address for this username from the Bitcoin client
    # FIXME: shouldn't we do this outside of a DB transaction?
    conn = utils.get_bitcoin_conn()
    account.deposit_address = conn.getaccountaddress(username)

    # generate deposit reference and save again
    account.deposit_ref = "B" + base64.b32encode(account.id).strip('=')
    account.save()

    return {'result': True}

@utils.db_transaction
@utils.authenticate_user
def change_password(ip, username, password, new_password):
    account = Account.objects.select_for_update().get(username=username)

    account.password = utils.hash_password(new_password)
    account.full_clean()
    account.save()

    return {'result': True}

@utils.db_transaction
@utils.authenticate_user
def change_email(ip, username, password, new_email, callback_url):
    account = Account.objects.select_for_update().get(username=username)

    account.email = new_email
    account.full_clean()
    account.save()

    return {'result': True}

def query_balances(ip, username, currency=None):
    balances = Balance.objects.select_related('currency').filter(account__username=username)

    if currency is not None:
        balances = balances.filter(currency__code=currency)

    return dict([(balance.currency.code, str(balance.amount)) for balance in balances])
