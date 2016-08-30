# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-08-19 12:32
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0008_offer'),
        ('admission', '0005_applicationdocumentfile_documenttypeassimilation'),
    ]

    operations = [
        migrations.AddField(
            model_name='offeryear',
            name='offer',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='base.Offer', blank=True, null=True),
            preserve_default=False,
        ),
    ]
