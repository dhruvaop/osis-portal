# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2019-04-23 18:43
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0050_auto_20190408_1522'),
    ]

    operations = [
        migrations.RunSQL(
            """
                DELETE from base_entitycomponentyear
                USING base_learningcomponentyear 
                 where base_learningcomponentyear.id = base_entitycomponentyear.learning_component_year_id
                 and base_learningcomponentyear.learning_unit_year_id is null
            """
        ),
        migrations.RunSQL(
            """
                DELETE from base_learningcomponentyear where learning_unit_year_id is null
            """
        ),
    ]
