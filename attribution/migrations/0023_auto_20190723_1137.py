# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2019-07-23 09:37
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('attribution', '0022_auto_20181221_0955'),
    ]

    operations = [
        migrations.AlterField(
            model_name='attribution',
            name='learning_unit_year',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, to='base.LearningUnitYear'),
        ),
    ]