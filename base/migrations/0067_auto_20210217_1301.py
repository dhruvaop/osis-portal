# Generated by Django 2.2.13 on 2021-02-17 12:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0066_auto_20210209_1200'),
        ('dissertation', '0029_remove_offerproposition_offer'),
        ('continuing_education', '0030_auto_20190415_1130'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='offeryear',
            name='academic_year',
        ),
        migrations.RemoveField(
            model_name='offeryear',
            name='campus',
        ),
        migrations.RemoveField(
            model_name='offeryear',
            name='grade_type',
        ),
        migrations.RemoveField(
            model_name='offeryear',
            name='offer',
        ),
        migrations.RemoveField(
            model_name='offeryeardomain',
            name='domain',
        ),
        migrations.RemoveField(
            model_name='offeryeardomain',
            name='offer_year',
        ),
        migrations.RemoveField(
            model_name='offerenrollment',
            name='offer_year',
        ),
        migrations.AlterField(
            model_name='offerenrollment',
            name='education_group_year',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='base.EducationGroupYear'),
        ),
        migrations.DeleteModel(
            name='ExternalOffer',
        ),
        migrations.DeleteModel(
            name='Offer',
        ),
        migrations.DeleteModel(
            name='OfferYear',
        ),
        migrations.DeleteModel(
            name='OfferYearDomain',
        ),
    ]
