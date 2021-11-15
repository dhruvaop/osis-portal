# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2018-03-28 11:15
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0035_auto_20180312_0913'),
    ]

    operations = [
        # Remove all deleted records physically
        migrations.RunSQL("""
            DELETE FROM base_learningunitcomponent
            WHERE deleted is not null OR
                id in (
                    SELECT base_learningunitcomponent.id
                    FROM base_learningunitcomponent
                    JOIN base_learningcomponentyear on (base_learningcomponentyear.id = base_learningunitcomponent.learning_component_year_id)
                    JOIN base_learningcontaineryear on (base_learningcontaineryear.id = base_learningcomponentyear.learning_container_year_id)
                    JOIN base_learningcontainer on (base_learningcontainer.id = base_learningcontaineryear.learning_container_id)
                    WHERE base_learningunitcomponent.deleted is null AND
                        ( base_learningcomponentyear is not null OR base_learningcontaineryear.deleted is not null OR base_learningcontainer.deleted is not null )
                ) OR
                id in (
                    SELECT base_learningunitcomponent.id
                    FROM base_learningunitcomponent
                    JOIN base_learningunityear on (base_learningunityear.id = base_learningunitcomponent.learning_unit_year_id)
                     WHERE base_learningunitcomponent.deleted is null AND
                        ( base_learningunityear is not null)
                )
        """),
        migrations.RunSQL("""
            DELETE FROM base_entitycomponentyear
            WHERE deleted is not null OR
                  id in (
                    SELECT base_entitycomponentyear.id
                    FROM base_entitycomponentyear
                    JOIN base_entitycontaineryear on (base_entitycontaineryear.id = base_entitycomponentyear.entity_container_year_id)
                    JOIN base_learningcontaineryear on (base_learningcontaineryear.id = base_entitycontaineryear.learning_container_year_id)
                    JOIN base_learningcontainer on (base_learningcontainer.id = base_learningcontaineryear.learning_container_id)
                    WHERE base_entitycomponentyear.deleted is null AND
                    ( base_entitycontaineryear.deleted is not null OR base_learningcontaineryear.deleted is not null OR base_learningcontainer.deleted is not null )
                  )
        """),
        migrations.RunSQL("""
            DELETE FROM base_entitycontaineryear
            WHERE deleted is not null OR
                  id in (
                    SELECT base_entitycontaineryear.id
                    FROM base_entitycontaineryear
                    JOIN base_learningcontaineryear on (base_learningcontaineryear.id = base_entitycontaineryear.learning_container_year_id)
                    JOIN base_learningcontainer on (base_learningcontainer.id = base_learningcontaineryear.learning_container_id)
                    WHERE base_entitycontaineryear.deleted is null AND
                    ( base_learningcontaineryear.deleted is not null OR base_learningcontainer.deleted is not null )
                  )
        """),
        migrations.RunSQL("""
            DELETE FROM base_learningcomponentyear
            WHERE deleted is not null OR
                  id in (
                     SELECT base_learningcomponentyear.id
                     FROM base_learningcomponentyear
                     JOIN base_learningcontaineryear on (base_learningcontaineryear.id = base_learningcomponentyear.learning_container_year_id)
                     JOIN base_learningcontainer on (base_learningcontainer.id = base_learningcontaineryear.learning_container_id)
                     WHERE base_learningcomponentyear.deleted is null AND
                      ( base_learningcontaineryear.deleted is not null OR base_learningcontainer.deleted is not null )
                  )
        """),
        migrations.RunSQL("""
            DELETE FROM base_learningunityear
            WHERE deleted is not null OR
                  id in (
                    SELECT base_learningunityear.id
                    FROM base_learningunityear
                     WHERE base_learningunityear.deleted is null
                  )
        """),
        migrations.RunSQL("DELETE FROM base_learningunit WHERE deleted is not null"),
        migrations.RunSQL("""
            DELETE FROM base_learningcontaineryear
            WHERE deleted is not null OR
                  id in (
                    SELECT base_learningcontaineryear.id
                    FROM base_learningcontaineryear
                    JOIN base_learningcontainer on (base_learningcontainer.id = base_learningcontaineryear.learning_container_id)
                    WHERE base_learningcontaineryear.deleted is null AND base_learningcontainer.deleted is not null
                  )
        """),
        migrations.RunSQL("DELETE FROM base_learningcontainer WHERE deleted is not null"),
    ]
