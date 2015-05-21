# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import cropduster.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Crop',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('crop_x', models.PositiveIntegerField(default=0, null=True, blank=True)),
                ('crop_y', models.PositiveIntegerField(default=0, null=True, blank=True)),
                ('crop_w', models.PositiveIntegerField(default=0, null=True, blank=True)),
                ('crop_h', models.PositiveIntegerField(default=0, null=True, blank=True)),
            ],
            options={
                'db_table': 'cropduster_crop',
            },
            bases=(cropduster.models.CachingMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', models.ImageField(max_length=255, upload_to=b'img/upload/%Y/%m/%d', db_index=True)),
                ('attribution', models.CharField(max_length=255, null=True, blank=True)),
                ('caption', models.CharField(max_length=255, null=True, blank=True)),
            ],
            options={
                'db_table': 'cropduster_image',
                'verbose_name': 'Image',
                'verbose_name_plural': 'Image',
            },
            bases=(cropduster.models.CachingMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Size',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, db_index=True)),
                ('slug', models.SlugField()),
                ('height', models.PositiveIntegerField(null=True, blank=True)),
                ('width', models.PositiveIntegerField(null=True, blank=True)),
                ('auto_size', models.PositiveIntegerField(default=0, verbose_name=b'Thumbnail Generation', choices=[(0, b'Manually Crop'), (1, b'Auto-Crop'), (2, b'Auto-Size')])),
                ('aspect_ratio', models.FloatField(default=1)),
                ('create_on_request', models.BooleanField(default=False, verbose_name=b'Crop on request')),
                ('retina', models.BooleanField(default=False, verbose_name=b'Auto-create retina thumb')),
            ],
            options={
                'db_table': 'cropduster_size',
            },
            bases=(cropduster.models.CachingMixin, models.Model),
        ),
        migrations.CreateModel(
            name='SizeSet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, db_index=True)),
                ('slug', models.SlugField()),
            ],
            bases=(cropduster.models.CachingMixin, models.Model),
        ),
        migrations.AddField(
            model_name='size',
            name='size_set',
            field=models.ForeignKey(to='cropduster.SizeSet'),
        ),
        migrations.AddField(
            model_name='image',
            name='size_set',
            field=models.ForeignKey(to='cropduster.SizeSet'),
        ),
        migrations.AddField(
            model_name='crop',
            name='image',
            field=models.ForeignKey(related_name='images', verbose_name=b'images', to='cropduster.Image'),
        ),
        migrations.AddField(
            model_name='crop',
            name='size',
            field=models.ForeignKey(related_name='size', verbose_name=b'sizes', to='cropduster.Size'),
        ),
        migrations.AlterUniqueTogether(
            name='crop',
            unique_together=set([('size', 'image')]),
        ),
    ]
