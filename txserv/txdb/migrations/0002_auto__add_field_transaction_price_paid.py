# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Adding field 'Transaction.price_paid'
        db.add_column('txdb_transaction', 'price_paid', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=16, decimal_places=8), keep_default=False)


    def backwards(self, orm):
        
        # Deleting field 'Transaction.price_paid'
        db.delete_column('txdb_transaction', 'price_paid')


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
            'price_paid': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '16', 'decimal_places': '8'}),
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
