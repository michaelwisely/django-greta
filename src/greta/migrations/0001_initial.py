# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Repository'
        db.create_table('greta_repository', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('default_branch', self.gf('django.db.models.fields.CharField')(default='master', max_length=30)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=100)),
            ('forked_from', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='forks', null=True, on_delete=models.SET_NULL, to=orm['greta.Repository'])),
            ('task_id', self.gf('django.db.models.fields.CharField')(max_length=60, null=True)),
            ('owner_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True, blank=True)),
            ('owner_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal('greta', ['Repository'])


    def backwards(self, orm):
        # Deleting model 'Repository'
        db.delete_table('greta_repository')


    models = {
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'greta.repository': {
            'Meta': {'object_name': 'Repository'},
            'default_branch': ('django.db.models.fields.CharField', [], {'default': "'master'", 'max_length': '30'}),
            'forked_from': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'forks'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': "orm['greta.Repository']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'owner_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'owner_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            'task_id': ('django.db.models.fields.CharField', [], {'max_length': '60', 'null': 'True'})
        }
    }

    complete_apps = ['greta']