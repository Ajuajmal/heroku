# -*- coding: utf-8 -*-
# Generated by Django 1.11.9 on 2018-02-25 00:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('invoices', '0003_invoiced_entity'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='compound',
            field=models.BooleanField(default=False),
        ),
    ]