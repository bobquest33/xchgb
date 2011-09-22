import errors, settings, utils
from txdb.models import *

def get_deposit_reference(ip, username, currency='BTC'):
    account = Account.objects.get(username=username).values('deposit_address', 'deposit_ref')
    return account['deposit_address'] if currency == 'BTC' else account['deposit_ref']

@utils.db_transaction
@utils.authenticate_user
def request_withdrawal(ip, username, password, currency, amount, withdraw_to):
    pass
    #check that user has sufficient funds
    #jsonify withdraw_to - throw ex on error
    #remove funds from user balance
    #add request

def confirm_withdrawal(ip, withdrawal_id, deduct_fees=0):
    pass

def decline_withdrawal(ip, withdrawal_id, reason):
    pass

def confirm_deposit(ip, currency, reference, source, amount, deduct_fees=0):
    pass
    #find balance by currency/reference

def decline_deposit(ip, currency, reference, source, amount, reason):
    pass

def query_deposits(ip, username=None, limit=None, offset=0, start_date=None, end_date=None, currency=None, accepted=None):
    pass

def query_withdrawals(ip, username=None, limit=None, offset=0, start_date=None, end_date=None, currency=None, processed=None, accepted=None):
    pass