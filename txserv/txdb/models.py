from django.db import models

def get_amount_field():
    return models.DecimalField(default=0, max_digits=16, decimal_places=8)

class Account(models.Model):
    username = models.CharField(max_length=30, unique=True)
    password = models.CharField(max_length=60)
    email = models.TextField(blank=True, null=True) # stored encrypted
    created = models.DateTimeField(auto_now_add=True)
    allow_auth = models.BooleanField(default=True)
    allow_orders = models.BooleanField(default=True)
    allow_transfers = models.BooleanField(default=True)
    deposit_address = models.CharField(max_length=40, blank=True, null=True)
    deposit_ref = models.CharField(max_length=30, blank=True, null=True)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=4)

    def __str__(self):
        return self.username

class Currency(models.Model):
    name = models.CharField(max_length=40, unique=True)
    code = models.CharField(max_length=4, unique=True)
    symbol = models.CharField(max_length=1, blank=True, null=True)

    def __str__(self):
        return self.code

class Balance(models.Model):
    account = models.ForeignKey(Account, related_name='balances')
    currency = models.ForeignKey(Currency, related_name='balances')
    amount = get_amount_field()
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('account', 'currency'),)

    def __str__(self):
        return "%s has %s %s" % (self.account, self.amount, self.currency)

class Order(models.Model):
    balance = models.ForeignKey(Balance, related_name='orders')
    offer_amount = get_amount_field()
    initial_offer_amount = get_amount_field()
    want_currency = models.ForeignKey(Currency, related_name='orderbook')
    want_amount = get_amount_field()
    initial_want_amount = get_amount_field()
    bid = get_amount_field()
    ask = get_amount_field() # should probably use a Manager for this?
    filled = models.BooleanField(default=False)
    cancelled = models.BooleanField(default=False)
    last_updated = models.DateTimeField(auto_now=True)
    placed = models.DateTimeField(auto_now_add=True)
    ip_address = models.IPAddressField()

    def __str__(self):
        if self.filled or self.cancelled:
            return "%s offered %s %s for %s %s" % (
                self.balance.account,
                self.initial_offer_amount,
                self.balance.currency,
                self.initial_want_amount,
                self.want_currency
            )
        else:
            return "%s offers %s %s for %s %s" % (
                self.balance.account,
                self.offer_amount,
                self.balance.currency,
                self.want_amount,
                self.want_currency
            )

class Transaction(models.Model):
    order = models.ForeignKey(Order, related_name='transactions')
    from_balance = models.ForeignKey(Balance, related_name='sent_transactions')
    to_balance = models.ForeignKey(Balance, related_name='received_transactions')
    amount = get_amount_field() # including commission
    price_paid = get_amount_field()
    commission_rate = models.DecimalField(max_digits=5, decimal_places=4)
    commission_amount = get_amount_field()
    reversed = models.BooleanField(default=False)
    linked_transaction = models.OneToOneField('self', null=True)
    executed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.linked_transaction:
            return "%s paid %s %s to %s for %s %s" % (
                self.from_balance.account,
                self.amount,
                self.from_balance.currency,
                self.to_balance.account,
                self.linked_transaction.amount,
                self.linked_transaction.from_balance.currency
            )
        else:
            return "%s paid %s %s to %s" % (
                self.from_balance.account,
                self.amount,
                self.from_balance.currency,
                self.to_balance.account
            )

class Deposit(models.Model):
    balance = models.ForeignKey(Balance)
    source = models.TextField()
    amount_received = get_amount_field()
    amount_deposited = get_amount_field() # less fees
    accepted = models.BooleanField(default=True)
    refuse_reason = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

class Withdrawal(models.Model):
    balance = models.ForeignKey(Balance)
    beneficiary = models.TextField()
    amount_requested = get_amount_field()
    amount_withdrawn = get_amount_field() # less fees
    processed = models.BooleanField(default=False)
    accepted = models.BooleanField(default=False)
    refuse_reason = models.TextField(blank=True, null=True)
    requested = models.DateTimeDield(auto_now_add=True)
    last_updated = models.DateTimeDield(auto_now=True)
