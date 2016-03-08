# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
                ('description', models.TextField(blank=True)),
                ('father', models.ForeignKey(to='owade.Category', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('checksum', models.TextField()),
                ('extension', models.TextField(blank=True)),
                ('size', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='FileInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
                ('dir_path', models.TextField()),
                ('file', models.ForeignKey(to='owade.File')),
            ],
        ),
        migrations.CreateModel(
            name='HardDrive',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('serial', models.TextField(unique=True)),
                ('size', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Partition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slot', models.TextField()),
                ('offset', models.TextField()),
                ('size', models.TextField()),
                ('type', models.TextField()),
                ('os', models.TextField()),
                ('files', models.ManyToManyField(to='owade.File')),
                ('harddrive', models.ForeignKey(to='owade.HardDrive')),
            ],
        ),
        migrations.CreateModel(
            name='Value',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.TextField()),
                ('value', models.TextField(null=True, blank=True)),
                ('category', models.ForeignKey(to='owade.Category')),
            ],
        ),
        migrations.AddField(
            model_name='fileinfo',
            name='partition',
            field=models.ForeignKey(to='owade.Partition'),
        ),
        migrations.AddField(
            model_name='category',
            name='partition',
            field=models.ForeignKey(to='owade.Partition', null=True),
        ),
    ]
