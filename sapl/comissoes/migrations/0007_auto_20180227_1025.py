# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2018-02-27 13:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('comissoes', '0006_auto_20180227_0842'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reuniao',
            name='hora_fim',
            field=models.CharField(max_length=5, verbose_name='Horário de Término (hh:mm)'),
        ),
        migrations.AlterField(
            model_name='reuniao',
            name='hora_inicio',
            field=models.CharField(max_length=5, verbose_name='Horário de Início (hh:mm)'),
        ),
    ]
