# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2018-03-28 11:16
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0036_auto_20180328_1315'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='entitycomponentyear',
            name='deleted',
        ),
        migrations.RemoveField(
            model_name='entitycontaineryear',
            name='deleted',
        ),
        migrations.RemoveField(
            model_name='learningcomponentyear',
            name='deleted',
        ),
        migrations.RemoveField(
            model_name='learningcontainer',
            name='deleted',
        ),
        migrations.RemoveField(
            model_name='learningcontaineryear',
            name='deleted',
        ),
        migrations.RemoveField(
            model_name='learningunit',
            name='deleted',
        ),
        migrations.RemoveField(
            model_name='learningunitcomponent',
            name='deleted',
        ),
        migrations.RemoveField(
            model_name='learningunitenrollment',
            name='deleted',
        ),
        migrations.RemoveField(
            model_name='learningunityear',
            name='deleted',
        ),
    ]
