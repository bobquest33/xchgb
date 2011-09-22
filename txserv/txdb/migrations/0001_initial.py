# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding model 'Account'
        db.create_table('txdb_account', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('username', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=60)),
            ('email', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('allow_auth', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('allow_orders', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('allow_transfers', self.gf('django.db.models.fields.BooleanField')(default=True)),
        ))
        db.send_create_signal('txdb', ['Account'])

        # Adding model 'Currency'
        db.create_table('txdb_currency', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=40)),
            ('code', self.gf('django.db.models.fields.CharField')(unique=True, max_length=4)),
            ('symbol', self.gf('django.db.models.fields.CharField')(max_length=1, null=True, blank=True)),
        ))
        db.send_create_signal('txdb', ['Currency'])

        # Adding model 'Balance'
        db.create_table('txdb_balance', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('account', self.gf('django.db.models.fields.related.ForeignKey')(related_name='balances', to=orm['txdb.Account'])),
            ('currency', self.gf('django.db.models.fields.related.ForeignKey')(related_name='balances', to=orm['txdb.Currency'])),
            ('amount', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=16, decimal_places=8)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
        ))
        db.send_create_signal('txdb', ['Balance'])

        # Adding unique constraint on 'Balance', fields ['account', 'currency']
        db.create_unique('txdb_balance', ['account_id', 'currency_id'])

        # Adding model 'Order'
        db.create_table('txdb_order', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('balance', self.gf('django.db.models.fields.related.ForeignKey')(related_name='orders', to=orm['txdb.Balance'])),
            ('offer_amount', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=16, decimal_places=8)),
            ('initial_offer_amount', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=16, decimal_places=8)),
            ('want_currency', self.gf('django.db.models.fields.related.ForeignKey')(related_name='orderbook', to=orm['txdb.Currency'])),
            ('want_amount', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=16, decimal_places=8)),
            ('initial_want_amount', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=16, decimal_places=8)),
            ('bid', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=16, decimal_places=8)),
            ('ask', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=16, decimal_places=8)),
            ('filled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('cancelled', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('placed', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('ip_address', self.gf('django.db.models.fields.IPAddressField')(max_length=15)),
        ))
        db.send_create_signal('txdb', ['Order'])

        # Adding model 'Transaction'
        db.create_table('txdb_transaction', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('order', self.gf('django.db.models.fields.related.ForeignKey')(related_name='transactions', to=orm['txdb.Order'])),
            ('from_balance', self.gf('django.db.models.fields.related.ForeignKey')(related_name='sent_transactions', to=orm['txdb.Balance'])),
            ('to_balance', self.gf('django.db.models.fields.related.ForeignKey')(related_name='received_transactions', to=orm['txdb.Balance'])),
            ('amount', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=16, decimal_places=8)),
            ('reversed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('linked_transaction', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['txdb.Transaction'], unique=True, null=True)),
            ('executed', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('txdb', ['Transaction'])

        # Adding model 'Transfer'
        db.create_table('txdb_transfer', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('from_balance', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['txdb.Balance'])),
            ('to', self.gf('django.db.models.fields.TextField')()),
            ('amount', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=16, decimal_places=8)),
            ('status', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('last_updated', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, blank=True)),
            ('requested', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal('txdb', ['Transfer'])


    def backwards(self, orm):
        
        # Removing unique constraint on 'Balance', fields ['account', 'currency']
        db.delete_unique('txdb_balance', ['account_id', 'currency_id'])

        # Deleting model 'Account'
        db.delete_table('txdb_account')

        # Deleting model 'Currency'
        db.delete_table('txdb_currency')

        # Deleting model 'Balance'
        db.delete_table('txdb_balance')

        # Deleting model 'Order'
        db.delete_table('txdb_order')

        # Deleting model 'Transaction'
        db.delete_table('txdb_transaction')

        # Deleting model 'Transfer'
        db.delete_table('txdb_transfer')


    models = {
        'txdb.account': {
            'Meta': {'object_name': 'Account'},
            'allow_auth': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'allow_orders': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'allow_transfers': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '60'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'txdb.balance': {
            'Meta': {'unique_together': "(('account', 'currency'),)", 'object_name': 'Balance'},
            'account': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'balances'", 'to': "orm['txdb.Account']"}),
            'amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '16', 'decimal_places': '8'}),
            'currency': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'balances'", 'to': "orm['txdb.Currency']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'txdb.currency': {
            'Meta': {'object_name': 'Currency'},
            'code': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '4'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '40'}),
            'symbol': ('django.db.models.fields.CharField', [], {'max_length': '1', 'null': 'True', 'blank': 'True'})
        },
        'txdb.order': {
            'Meta': {'object_name': 'Order'},
            'ask': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '16', 'decimal_places': '8'}),
            'balance': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'orders'", 'to': "orm['txdb.Balance']"}),
            'bid': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '16', 'decimal_places': '8'}),
            'cancelled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'filled': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'initial_offer_amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '16', 'decimal_places': '8'}),
            'initial_want_amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '16', 'decimal_places': '8'}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'max_length': '15'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'offer_amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '16', 'decimal_places': '8'}),
            'placed': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'want_amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '16', 'decimal_places': '8'}),
            'want_currency': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'orderbook'", 'to': "orm['txdb.Currency']"})
        },
        'txdb.transaction': {
            'Meta': {'object_name': 'Transaction'},
            'amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '16', 'decimal_places': '8'}),
            'executed': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'from_balance': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'sent_transactions'", 'to': "orm['txdb.Balance']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'linked_transaction': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['txdb.Transaction']", 'unique': 'True', 'null': 'True'}),
            'order': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'transactions'", 'to': "orm['txdb.Order']"}),
            'reversed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'to_balance': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'received_transactions'", 'to': "orm['txdb.Balance']"})
        },
        'txdb.transfer': {
            'Meta': {'object_name': 'Transfer'},
            'amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '16', 'decimal_places': '8'}),
            'from_balance': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['txdb.Balance']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'requested': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'to': ('django.db.models.fields.TextField', [], {})
        }
    }

    complete_apps = ['txdb']
