import calendar, datetime, errors, settings
from txdb.models import *
from decimal import Decimal
from django.db import connection
from django.db.models import Sum

def historical_prices(ip, start_date=None, end_date=None, scope='daily'):
    try:
        start_date = int(start_date) if start_date is not None else None
        end_date = int(end_date) if end_date is not None else None
    except:
        raise errors.InvalidArgumentError()

    # are both valid unix timestamps?
    if start_date is not None and (start_date < 0 or start_date > 0x7FFFFFFF):
        raise errors.InvalidArgumentError()
    elif end_date is not None and (end_date < 0 or end_date > 0x7FFFFFFF or end_date <= start_date):
        raise errors.InvalidArgumentError()

    # adjust scope of query
    if scope == 'monthly':
        group_by = 'YEAR(txdb_transaction.executed), MONTH(txdb_transaction.executed)'
    elif scope == 'weekly':
        group_by = 'YEARWEEK(txdb_transaction.executed)'
    elif scope == 'hourly':
        group_by = 'DATE(txdb_transaction.executed), HOUR(txdb_transaction.executed)'
    elif scope == '15mins':
        group_by = 'DATE(txdb_transaction.executed), HOUR(txdb_transaction.executed), CAST(MINUTE(txdb_transaction.executed) / 15 AS INTEGER)'
    else: # scope == 'daily'
        group_by = 'DATE(txdb_transaction.executed)'

    # construct where clause limiting date range
    date_limits = ""
    date_params = []
    if start_date:
        date_limits += " AND txdb_transaction.executed >= FROM_UNIXTIME(%s)"
        date_params.append(start_date)
    if end_date:
        date_limits += " AND txdb_transaction.executed <= FROM_UNIXTIME(%s)"
        date_params.append(end_date)

    # abusing MySQL since 2011
    query = """SELECT
        txdb_transaction.executed as 'timestamp',
        SUBSTRING_INDEX(GROUP_CONCAT(txdb_order.bid ORDER BY txdb_transaction.executed ASC), ',', 1) AS 'open',
        SUBSTRING_INDEX(GROUP_CONCAT(txdb_order.bid ORDER BY txdb_transaction.executed DESC), ',', 1) AS 'close',
        SUBSTRING_INDEX(GROUP_CONCAT(txdb_order.bid ORDER BY txdb_order.bid ASC), ',', 1) AS 'low',
        SUBSTRING_INDEX(GROUP_CONCAT(txdb_order.bid ORDER BY txdb_order.bid DESC), ',', 1) AS 'high',
        AVG(txdb_order.bid) as 'mean',
        SUM(linked_transaction.amount) as 'volume'
    FROM txdb_transaction
    INNER JOIN txdb_balance from_balance
        ON txdb_transaction.from_balance_id = from_balance.id
    INNER JOIN txdb_currency from_currency
        ON from_balance.currency_id = from_currency.id
    INNER JOIN txdb_transaction linked_transaction
        ON txdb_transaction.linked_transaction_id = linked_transaction.id
    INNER JOIN txdb_order
        ON txdb_transaction.order_id = txdb_order.id
    WHERE txdb_transaction.reversed = 0 AND from_currency.code = 'GBP'
        %s
    GROUP BY %s
    ORDER BY txdb_transaction.executed ASC
    LIMIT %d""" % (date_limits, group_by, settings.HISTORICAL_PRICES_ROW_LIMIT)

    cursor = connection.cursor()
    cursor.execute(query, date_params)

    results = {
        'timestamp': [],
        'open': [],
        'close': [],
        'low': [],
        'high': [],
        'mean': [],
        'volume': []
    }

    # format the results into something usable by ChartDirector
    row = cursor.fetchone()
    while row:
        ts = calendar.timegm(floor_datetime(row[0], scope).timetuple())
        results['timestamp'].append(ts)
        results['open'].append(str(row[1]))
        results['close'].append(str(row[2]))
        results['low'].append(str(row[3]))
        results['high'].append(str(row[4]))
        results['mean'].append(str(row[5]))
        results['volume'].append(str(row[6]))
        row = cursor.fetchone()

    return results

def floor_datetime(ts, scope):
    if scope == 'monthly':
        return datetime.datetime(ts.year, ts.month, 1, 0, 0, 0)
    elif scope == 'weekly':
        return datetime.datetime(ts.year, ts.month, (int((ts.day - 1) / 7) * 7) + 1, 0, 0, 0)
    elif scope == 'hourly':
        return datetime.datetime(ts.year, ts.month, ts.day, ts.hour, 0, 0)
    elif scope == '15mins':
        return datetime.datetime(ts.year, ts.month, ts.day, ts.hour, int(ts.minute / 15) * 15, 0)
    else: # scope == 'daily'
        return datetime.datetime(ts.year, ts.month, ts.day, 0, 0, 0)

def market_depth(ip, step=0.05):
    try:
        step = Decimal(str(step))
    except:
        raise errors.InvalidArgumentError()

    if step <= 0:
        raise errors.InvalidArgumentError()

    cursor_bid = run_market_depth_query(step, 'bid')
    cursor_ask = run_market_depth_query(step, 'ask')

    return {
        'bid': compile_market_depth_results(cursor_bid, step),
        'ask': compile_market_depth_results(cursor_ask, step)
    }

def run_market_depth_query(step, column):
    if column == 'bid':
        offer_currency = 'GBP'
    elif column == 'ask':
        offer_currency = 'BTC'
    else:
        raise errors.InvalidArgumentError()

    query = """SELECT
        CAST(txdb_order.%s / %s AS UNSIGNED INTEGER) * %s as 'price',
        SUM(txdb_order.want_amount) as 'volume'
    FROM txdb_order
    INNER JOIN txdb_balance
        ON txdb_order.balance_id = txdb_balance.id
    INNER JOIN txdb_currency
        ON txdb_balance.currency_id = txdb_currency.id
    WHERE txdb_order.filled = 0 AND txdb_order.cancelled = 0
        AND txdb_currency.code = %s
    GROUP BY CAST(txdb_order.%s / %s AS UNSIGNED INTEGER)
    ORDER BY price ASC""" % (column, '%s', '%s', '%s', column, '%s')

    cursor = connection.cursor()
    cursor.execute(query, [step, step, offer_currency, step])
    return cursor

def compile_market_depth_results(cursor, step):
    results = {
        'start': 0,
        'step': str(step),
        'volume': []
    }

    row = cursor.fetchone()
    if not row:
        return results
    else:
        price = Decimal(str(row[0]))
        results['start'] = price

    while row:
        if price == Decimal(str(row[0])):
            results['volume'].append(str(row[1]))
            row = cursor.fetchone()
        else:
            results['volume'].append(0)
        price += step

    results['end'] = str(results['start'] + (step * (len(results['volume']) - 1)))
    results['start'] = str(results['start'])

    return results

def accumulated_market_depth(ip):
    results = market_depth(ip, settings.ACCUMULATED_MARKET_DEPTH_RESOLUTION)

    compute_accumulated_volumes(results['bid']['volume'], -1)
    compute_accumulated_volumes(results['ask']['volume'], 1)

    return results

def compute_accumulated_volumes(volume, direction):
    iterator = xrange(len(volume) - 1, -1, direction) if direction < 0 else xrange(0, len(volume), direction)
    running_total = Decimal(0)

    for i in iterator:
        running_total += Decimal(str(volume[i]))
        volume[i] = str(running_total)

    return volume

def market_summary(ip):
    # used multiple times, so cache to prevent unnecessary joins
    gbp = Currency.objects.filter(code='GBP').values('id')[0]['id']
    btc = Currency.objects.filter(code='BTC').values('id')[0]['id']

    # calculate last trade price and delta between that and the trade before it
    most_recent_trades = Transaction.objects.filter(from_balance__currency=gbp).order_by('-executed')[:2]
    if len(most_recent_trades) == 2 and most_recent_trades[0].price_paid > 0 and most_recent_trades[1].price_paid > 0:
        last_trade = most_recent_trades[0].price_paid
        change_amount = most_recent_trades[1].price_paid - most_recent_trades[0].price_paid
        change_percent = (change_amount / last_trade) * 100
    else:
        last_trade = 0
        change_amount = 0
        change_percent = 0

    today = datetime.datetime.now()
    yesterday = today - datetime.timedelta(days=1)
    market_time = calendar.timegm(today.timetuple())

    # utility function to extract the first y from x or return 0 if fail
    prep_single = lambda x, y: x[0][y] if len(x) > 0 else 0
    # utility function to change None to 0
    no_none = lambda x: x if x is not None else 0

    previous_close = prep_single(Transaction.objects.filter(from_balance__currency=gbp, executed__year=yesterday.year, executed__month=yesterday.month, executed__day=yesterday.day).order_by('-executed').values('price_paid')[:1], 'price_paid')
    open_today = prep_single(Transaction.objects.filter(from_balance__currency=gbp, executed__year=today.year, executed__month=today.month, executed__day=today.day).order_by('-executed').values('price_paid')[:1], 'price_paid')
    low_today = prep_single(Transaction.objects.filter(from_balance__currency=gbp, executed__year=today.year, executed__month=today.month, executed__day=today.day).order_by('price_paid').values('price_paid')[:1], 'price_paid')
    high_today = prep_single(Transaction.objects.filter(from_balance__currency=gbp, executed__year=today.year, executed__month=today.month, executed__day=today.day).order_by('-price_paid').values('price_paid')[:1], 'price_paid')

    bid = prep_single(Order.objects.filter(balance__currency=gbp, filled=False, cancelled=False).order_by('-bid').values('bid')[:1], 'bid') 
    ask = prep_single(Order.objects.filter(balance__currency=btc, filled=False, cancelled=False).order_by('ask').values('ask')[:1], 'ask')

    # aggregates
    volume_today_gbp = no_none(Transaction.objects.filter(from_balance__currency=gbp, executed__year=today.year, executed__month=today.month, executed__day=today.day).aggregate(volume=Sum('amount'))['volume'])
    volume_today_btc = no_none(Transaction.objects.filter(from_balance__currency=btc, executed__year=today.year, executed__month=today.month, executed__day=today.day).aggregate(volume=Sum('amount'))['volume'])

    return {
        'last_trade':         str(last_trade),
        'change_amount':      str(change_amount),
        'change_percent':     str(change_percent),
        'market_time':        market_time,
        'previous_close':     str(previous_close),
        'open':               str(open_today),
        'day_low':            str(low_today),
        'day_high':           str(high_today),
        'bid':                str(bid),
        'ask':                str(ask),
#       'weighted_24h':       None, #TODO
#       'weighted_7d':        None, #TODO
#       'weighted_30d':       None, #TODO
        'day_vol_gbp':        str(volume_today_gbp),
        'day_vol_btc':        str(volume_today_btc)
    }

def query_transactions(ip):
    pass