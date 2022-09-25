# Generated by Django 4.1 on 2022-09-15 00:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('be_api', '0002_alter_checkinrecord_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='checkinrecord',
            name='remark',
            field=models.CharField(blank=True, max_length=256),
        ),
        migrations.AddConstraint(
            model_name='checkinrecord',
            constraint=models.UniqueConstraint(fields=('session', 'user'), name='one_record_per_user_per_session', violation_error_message='each session each person can has only one record'),
        ),
    ]
