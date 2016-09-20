# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-09-12 08:48
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0010_auto_20160906_1451'),
        ('dissertation', '0003_remove_offerproposition_readers_visibility_date_for_students'),
    ]

    operations = [
        migrations.AddField(
            model_name='propositiondissertation',
            name='creator',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='base.Person'),
        ),
    ]
