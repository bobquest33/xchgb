import calendar, errors, utils, settings
from txdb.models import *
from django.db.models import Sum, F
from django.db import connection
from decimal import Decimal

@utils.db_transaction
@utils.authenticate_user
def place_order(ip, username, password, offer_currency, offer_amount, want_currency, want_amount):
    try:
        # select_for_update() locks rows until end of transaction
        balance = Balance.objects.select_for_update().get(account__username=username, currency__code=offer_currency, account__allow_orders=True)
    except Balance.DoesNotExist:
        raise errors.InvalidBalanceForAccountError()

    if offer_currency == want_currency:
        raise errors.InvalidCurrencyError()

    try:
        want_currency = Currency.objects.select_for_update().get(code=want_currency)
    except Currency.DoesNotExist:
        raise errors.InvalidCurrencyError()

    if offer_amount <= 0 or want_amount <= 0:
        raise errors.NegativeAmountError()

#   balance.amount -= offer_amount
#   balance.save()

    # store these in DB instead of calculating each time
    bid = Decimal(offer_amount) / Decimal(want_amount)
    ask = Decimal(want_amount) / Decimal(offer_amount)

    # validate & save to DB
    order = Order(balance=balance, offer_amount=offer_amount, initial_offer_amount=offer_amount, want_currency=want_currency, want_amount=want_amount, initial_want_amount=want_amount, bid=bid, ask=ask, ip_address=ip)
    order.full_clean()
    order.save()

    # attempt to execute this order immediately
    try_execute(order)

def place_buy_order(ip, username, password, offer_gbp, want_btc):
    return place_order(ip, username, password, "GBP", offer_gbp, "BTC", want_btc)

def place_sell_order(ip, username, password, offer_btc, want_gbp):
    return place_order(ip, username, password, "BTC", offer_btc, "GBP", want_gbp)

@utils.db_transaction
@utils.authenticate_user
def cancel_order(ip, username, password, order):
    try:
        order = Order.objects.select_for_update().select_related('balance').get(id=order, balance__account__username=username, filled=False, cancelled=False)
    except:
        raise errors.InvalidOrderError()

#   refund_amount = order.offer_amount - order.amount_paid

#   if refund_amount <= 0 or refund_amount > order.offer_amount:
#       raise errors.OrderIntegrityError()

    order.cancelled = True
    order.save()
    
#   order.balance.amount += refund_amount
#   order.balance.save()

def query_orders(ip, username=None, limit=None, offset=0, start_date=None, end_date=None, buy_only=False, sell_only=False, cancelled=None, filled=None):
    orders = Order.objects.order_by('-placed')
    orders = orders.select_related('want_currency__code') # so we know if this is a buy or sell order

    if username is not None:
        orders = orders.filter(balance__account__username=username)

    if start_date is not None:
        order = orders.filter(placed__gte=start_date)

    if end_date is not None:
        order = orders.filter(placed__lte=end_date)

    if buy_only:
        orders = orders.filter(balance__currency__code="GBP")
    elif sell_only:
        orders = orders.filter(balance__currency__code="BTC")

    if cancelled in (True, False):
        orders = orders.filter(cancelled=cancelled)

    if filled in (True, False):
        orders = orders.filter(filled=filled)

    if limit is not None and limit < settings.ORDER_QUERY_HARD_LIMIT:
        orders = orders[offset:limit]
    else:
        orders = orders[offset:settings.ORDER_QUERY_HARD_LIMIT]

    return [{
        'type': 'buy' if order.want_currency.code == "BTC" else 'sell',
        'id': order.id,
        'price': order.bid if order.want_currency.code == "BTC" else order.ask,
        'amount_offered': str(order.initial_offer_amount),
        'amount_wanted': str(order.initial_want_amount),
        'amount_paid': order.initial_offer_amount - order.offer_amount,
        'amount_received': order.initial_want_amount - order.want_amount,
        'is_cancelled': order.cancelled,
        'is_closed': order.filled,
        'timestamp': calendar.timegm(order.placed.timetuple()),
    } for order in orders]

"""This should be called within a transaction when the order is placed."""
def try_execute(order):
    if order.balance.amount <= 0 or order.cancelled or order.filled:
        return False

    # get orders which are asking for less than this order is bidding
    counter_orders = Order.objects.select_for_update().filter(ask__lt=order.bid)
    # ...restrict to orders which are dealing with the correct currencies
    counter_orders = counter_orders.filter(balance__currency=order.want_currency, want_currency=order.balance.currency)
    # ...exclude orders which are cancelled or already filled
    counter_orders = counter_orders.filter(cancelled=False, filled=False)
    # ...restrict to accounts which have a nonzero balance
    counter_orders = counter_orders.filter(balance__amount__gt=0)
    # ...prioritise by lowest ask, then by timestamp
    counter_orders = counter_orders.order_by('ask', 'placed')

    for counter in counter_orders:
        if order.offer_amount >= counter.want_amount:
            execute_order_pair(order, counter.want_amount, counter, counter.offer_amount) 
        else:
            adjusted = order.offer_amount * counter.bid
            execute_order_pair(counter, adjusted, order, order.offer_amount)
        if order.filled:
            break

    return bool(counter_orders) # returns True if any counter orders were found and processed

"""This should not be called outside of try_execute."""
def execute_order_pair(consumer, consumer_pays, consumed, consumed_pays):
    assert consumer.balance.currency == consumed.want_currency
    assert consumer.want_currency == consumed.balance.currency

    # figure out what percentage of the deal each side can meet
    consumer_can_meet = min(consumer.balance.amount / consumer_pays, 1)
    consumed_can_meet = min(consumed.balance.amount / consumed_pays, 1)

    # what percentage of the deal can both sides meet?
    multiplier = min(consumer_can_meet, consumed_can_meet)
    assert multiplier > 0 and multiplier <= 1

    # adjust how much is each side paying in their respective currencies
    consumer_pays = consumer_pays * multiplier
    consumed_pays = consumed_pays * multiplier

    # consumer now offers and wants less
    consumer.offer_amount -= consumer_pays
    consumer.want_amount -= consumed_pays

    # if consumer no longer offers/wants anything, close it
    if consumer.offer_amount <= 0 or consumer.want_amount <= 0:
        consumer.offer_amount = consumer.want_amount = 0
        consumer.filled = True

    # consumed now offers and wants less
    consumed.offer_amount -= consumed_pays
    consumed.want_amount -= consumer_pays

    # if consumed no longer offers/wants anything, close it
    if consumed.offer_amount <= 0 or consumed.want_amount <= 0:
        consumed.offer_amount = consumed.want_amount = 0
        consumed.filled = True

    # remove amounts from balances
    consumer.balance.amount -= consumer_pays
    consumed.balance.amount -= consumed_pays

    # lookup other balances
    consumer_receiving_bal = Balance.objects.get(account=consumer.balance.account, currency=consumer.want_currency)
    consumed_receiving_bal = Balance.objects.get(account=consumed.balance.account, currency=consumed.want_currency)
    assert consumer.balance.currency == consumed_receiving_bal.currency
    assert consumed.balance.currency == consumer_receiving_bal.currency

    # which order pays commission?
    if consumer.balance.currency.code == 'BTC':
        commission_order = consumer
    elif consumed.balance.currency.code == 'BTC':
        commission_order = consumed
    else:
        commission_order = None

    # calculate commission rates and amounts
    commission_rate = commission_order.balance.account.commission_rate if commission_order is not None else 0
    consumer_commission_rate = commission_rate if commission_order == consumer else 0
    consumed_commission_rate = commission_rate if commission_order == consumed else 0
    consumer_commission_amount = consumer_pays * consumer_commission_rate
    consumed_commission_amount = consumed_pays * consumed_commission_rate

    # add amounts to balances
    consumer_receiving_bal.amount += consumed_pays - consumed_commission_amount
    consumed_receiving_bal.amount += consumer_pays - consumer_commission_amount

    # save orders and balances to DB
    consumer.save()
    consumed.save()
    consumer.balance.save()
    consumed.balance.save()
    consumer_receiving_bal.save()
    consumed_receiving_bal.save()

    # create transactions
    tx_consumer_consumed = Transaction(order=consumer, from_balance=consumer.balance, to_balance=consumed_receiving_bal, amount=consumer_pays, price_paid=consumer_paid / consumed_paid, commission_rate=consumer_commission_rate, commission_amount=consumer_commission_amount)
    tx_consumed_consumer = Transaction(order=consumed, from_balance=consumed.balance, to_balance=consumer_receiving_bal, amount=consumed_pays, price_paid=comsumed_paid / consumer_paid, commission_rate=consumed_commission_rate, commission_amount=consumed_commission_amount)

    # save linked transactions
    tx_consumer_consumed.save()
    tx_consumed_consumer.linked_transaction = tx_consumer_consumed
    tx_consumed_consumer.save()
    tx_consumer_consumed.linked_transaction = tx_consumed_consumer
    tx_consumer_consumed.save()
