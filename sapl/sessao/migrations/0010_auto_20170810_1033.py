# -*- coding: utf-8 -*-
# Generated by Django 1.9.11 on 2017-08-10 10:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sessao', '0009_auto_20170619_1441'),
    ]

    operations = [
        migrations.AddField(
            model_name='registrovotacao',
            name='data_hora_atualizacao',
            field=models.DateTimeField(auto_now=True, null=True, verbose_name='Data'),
        ),
        migrations.AddField(
            model_name='registrovotacao',
            name='data_hora_criacao',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='Data Criação'),
        ),
    ]
