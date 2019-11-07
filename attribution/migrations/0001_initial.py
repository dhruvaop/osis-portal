# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-12-01 14:10
from __future__ import unicode_literals

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('base', '0005_auto_20170110_1050'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attribution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('external_id', models.CharField(blank=True, max_length=100, null=True)),
                ('function', models.CharField(blank=True, choices=[('COORDINATOR', 'COORDINATOR'), ('HOLDER', 'HOLDER'), ('CO_HOLDER', 'CO_HOLDER'), ('DEPUTY', 'DEPUTY')], db_index=True, max_length=15, null=True)),
                ('learning_unit_year', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='base.LearningUnitYear')),
                ('tutor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.Tutor')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='AttributionCharge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(db_index=True, default=uuid.uuid4, editable=False, unique=True)),
                ('allocation_charge', models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True)),
                ('attribution', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='attribution.Attribution')),
                ('learning_unit_component', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='base.LearningUnitComponent')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
