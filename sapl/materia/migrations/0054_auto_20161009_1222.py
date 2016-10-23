# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-10-09 15:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


def clear_model_autoria(apps, schema_editor):
    Autoria = apps.get_model("materia", "Autoria")
    Autoria.objects.all().delete()
    Proposicao = apps.get_model("materia", "Proposicao")
    Proposicao.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('protocoloadm', '0003_auto_20161009_1222'),
        ('materia', '0053_auto_20161004_1854'),
    ]

    operations = [
        migrations.RunPython(clear_model_autoria),
        migrations.RemoveField(
            model_name='autor',
            name='comissao',
        ),
        migrations.RemoveField(
            model_name='autor',
            name='parlamentar',
        ),
        migrations.RemoveField(
            model_name='autor',
            name='partido',
        ),
        migrations.RemoveField(
            model_name='autor',
            name='tipo',
        ),
        migrations.RemoveField(
            model_name='autor',
            name='user',
        ),
        migrations.AlterField(
            model_name='autoria',
            name='autor',
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE, to='base.Autor', verbose_name='Autor'),
        ),
        migrations.AlterField(
            model_name='proposicao',
            name='autor',
            field=models.ForeignKey(
                blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='base.Autor'),
        ),
        migrations.DeleteModel(
            name='Autor',
        ),
        migrations.DeleteModel(
            name='TipoAutor',
        ),
    ]
