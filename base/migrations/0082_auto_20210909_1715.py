# Generated by Django 2.2.13 on 2021-09-09 15:15

from django.db import migrations


def edit_gender_values(apps, schema_editor):
    Person = apps.get_model('base', 'Person')
    persons_to_update = []
    for person in Person.objects.all():
        if person.gender == 'M':
            person.gender = 'H'
            persons_to_update.append(person)

    Person.objects.bulk_update(persons_to_update, ['gender'], batch_size=1000)


class Migration(migrations.Migration):
    dependencies = [
        ('base', '0081_auto_20210909_1715'),
    ]

    operations = [
        migrations.RunPython(edit_gender_values, migrations.RunPython.noop),
    ]
