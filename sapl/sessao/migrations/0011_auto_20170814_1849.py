# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2017-08-14 18:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sessao', '0010_auto_20170814_1804'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tiporesultadovotacao',
            name='natureza',
            field=models.CharField(blank=True, choices=[('A', 'Aprovado'), ('R', 'Rejeitado')], max_length=100, null=True, verbose_name='Natureza do Tipo'),
        ),
    ]
