# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Deleting field 'Repository.task_id'
        db.delete_column(u'greta_repository', 'task_id')


    def backwards(self, orm):
        # Adding field 'Repository.task_id'
        db.add_column(u'greta_repository', 'task_id',
                      self.gf('django.db.models.fields.CharField')(max_length=60, null=True),
                      keep_default=False)


    models = {
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'greta.repository': {
            'Meta': {'object_name': 'Repository'},
            'created_on_disk': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'default_branch': ('django.db.models.fields.CharField', [], {'default': "'master'", 'max_length': '30'}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'forked_from': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'forks'", 'null': 'True', 'on_delete': 'models.SET_NULL', 'to': u"orm['greta.Repository']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'owner_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'owner_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'})
        }
    }

    complete_apps = ['greta']