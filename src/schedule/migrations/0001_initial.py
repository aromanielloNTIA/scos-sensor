# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-10-26 00:32
from __future__ import unicode_literals

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import schedule.models.schedule_entry


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scheme', models.CharField(blank=True, max_length=16, null=True)),
                ('version', models.CharField(blank=True, max_length=16, null=True)),
                ('host', models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='ScheduleEntry',
            fields=[
                ('name', models.SlugField(help_text=b'[Required] The unique identifier used in URLs and filenames', primary_key=True, serialize=False)),
                ('action', models.CharField(choices=[(b'acquire700c', b'acquire700c - Apply m4s detector over 300 1024-point FFTs at 751.00 MHz.'), (b'logger', b'logger - Log the message "running test {name}/{tid}".')], help_text=b'[Required] The name of the action to be scheduled', max_length=50)),
                ('priority', models.SmallIntegerField(default=10, help_text=b'Lower number is higher priority (default=10)', validators=[django.core.validators.MinValueValidator(-20), django.core.validators.MaxValueValidator(19)])),
                ('start', models.BigIntegerField(blank=True, default=schedule.models.schedule_entry.next_schedulable_timefn, help_text=b"Absolute time (epoch) to start, or leave blank for 'now'")),
                ('stop', models.BigIntegerField(blank=True, help_text=b"Absolute time (epoch) to stop, or leave blank for 'never'", null=True)),
                ('interval', models.PositiveIntegerField(blank=True, help_text=b'Seconds between tasks, or leave blank to run once', null=True, validators=[django.core.validators.MinValueValidator(1)])),
                ('is_active', models.BooleanField(default=True, help_text=b'Indicates whether the entry should be removed from the scheduler without removing it from the system')),
                ('is_private', models.BooleanField(default=False, help_text=b'Indicates whether the entry, and resulting data, are only visible to admins')),
                ('callback_url', models.URLField(blank=True, help_text=b'If given, the scheduler will POST a `TaskResult` JSON object to this URL after each task completes', null=True)),
                ('next_task_time', models.BigIntegerField(editable=False, help_text=b'The time the next task is scheduled to be executed', null=True)),
                ('next_task_id', models.IntegerField(default=1, editable=False, help_text=b'The id of the next task to be executed')),
                ('created', models.DateTimeField(auto_now_add=True, help_text=b'The date the entry was created')),
                ('modified', models.DateTimeField(auto_now=True, help_text=b'The date the entry was modified')),
                ('owner', models.ForeignKey(editable=False, help_text=b'The name of the user who owns the entry', on_delete=django.db.models.deletion.CASCADE, related_name='schedule_entries', to=settings.AUTH_USER_MODEL)),
                ('request', models.ForeignKey(editable=False, help_text=b'The request that created the entry', null=True, on_delete=django.db.models.deletion.CASCADE, to='schedule.Request')),
            ],
            options={
                'ordering': ('created',),
                'db_table': 'schedule',
            },
        ),
    ]
