# Generated by Django 2.2.13 on 2020-10-23 14:25

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

import schedule.models.schedule_entry


class Migration(migrations.Migration):
    initial = True

    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]

    operations = [
        migrations.CreateModel(
            name="Request",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("scheme", models.CharField(blank=True, max_length=16, null=True)),
                ("version", models.CharField(blank=True, max_length=16, null=True)),
                ("host", models.CharField(blank=True, max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="ScheduleEntry",
            fields=[
                (
                    "name",
                    models.SlugField(
                        help_text="[Required] The unique identifier used in URLs and filenames",
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                (
                    "action",
                    models.CharField(
                        choices=[
                            (
                                "acquire_iq_700MHz_ATT_DL",
                                "acquire_iq_700MHz_ATT_DL - Capture time-domain IQ samples at the following 1 frequencies: 739.00 MHz.",
                            ),
                            (
                                "acquire_iq_700MHz_ATT_UL",
                                "acquire_iq_700MHz_ATT_UL - Capture time-domain IQ samples at the following 1 frequencies: 709.00 MHz.",
                            ),
                            (
                                "acquire_iq_700MHz_FirstNet_DL",
                                "acquire_iq_700MHz_FirstNet_DL - Capture time-domain IQ samples at the following 1 frequencies: 763.00 MHz.",
                            ),
                            (
                                "acquire_iq_700MHz_FirstNet_UL",
                                "acquire_iq_700MHz_FirstNet_UL - Capture time-domain IQ samples at the following 1 frequencies: 793.00 MHz.",
                            ),
                            (
                                "acquire_iq_700MHz_P-SafetyNB_DL",
                                "acquire_iq_700MHz_P-SafetyNB_DL - Capture time-domain IQ samples at the following 1 frequencies: 772.00 MHz.",
                            ),
                            (
                                "acquire_iq_700MHz_P-SafetyNB_UL",
                                "acquire_iq_700MHz_P-SafetyNB_UL - Capture time-domain IQ samples at the following 1 frequencies: 802.00 MHz.",
                            ),
                            (
                                "acquire_iq_700MHz_T-Mobile_DL",
                                "acquire_iq_700MHz_T-Mobile_DL - Capture time-domain IQ samples at the following 1 frequencies: 731.50 MHz.",
                            ),
                            (
                                "acquire_iq_700MHz_T-Mobile_UL",
                                "acquire_iq_700MHz_T-Mobile_UL - Capture time-domain IQ samples at the following 1 frequencies: 700.50 MHz.",
                            ),
                            (
                                "acquire_iq_700MHz_Verizon_DL",
                                "acquire_iq_700MHz_Verizon_DL - Capture time-domain IQ samples at the following 1 frequencies: 751.00 MHz.",
                            ),
                            (
                                "acquire_iq_700MHz_Verizon_UL",
                                "acquire_iq_700MHz_Verizon_UL - Capture time-domain IQ samples at the following 1 frequencies: 782.00 MHz.",
                            ),
                            (
                                "acquire_m4s_700MHz_ATT_DL",
                                "acquire_m4s_700MHz_ATT_DL - Apply m4s detector over 300 1024-pt FFTs at 739.00 MHz.",
                            ),
                            (
                                "acquire_m4s_700MHz_ATT_UL",
                                "acquire_m4s_700MHz_ATT_UL - Apply m4s detector over 300 1024-pt FFTs at 709.00 MHz.",
                            ),
                            (
                                "acquire_m4s_700MHz_FirstNet_DL",
                                "acquire_m4s_700MHz_FirstNet_DL - Apply m4s detector over 300 1024-pt FFTs at 763.00 MHz.",
                            ),
                            (
                                "acquire_m4s_700MHz_FirstNet_UL",
                                "acquire_m4s_700MHz_FirstNet_UL - Apply m4s detector over 300 1024-pt FFTs at 793.00 MHz.",
                            ),
                            (
                                "acquire_m4s_700MHz_P-SafetyNB_DL",
                                "acquire_m4s_700MHz_P-SafetyNB_DL - Apply m4s detector over 300 1024-pt FFTs at 772.00 MHz.",
                            ),
                            (
                                "acquire_m4s_700MHz_P-SafetyNB_UL",
                                "acquire_m4s_700MHz_P-SafetyNB_UL - Apply m4s detector over 300 1024-pt FFTs at 802.00 MHz.",
                            ),
                            (
                                "acquire_m4s_700MHz_T-Mobile_DL",
                                "acquire_m4s_700MHz_T-Mobile_DL - Apply m4s detector over 300 1024-pt FFTs at 731.50 MHz.",
                            ),
                            (
                                "acquire_m4s_700MHz_T-Mobile_UL",
                                "acquire_m4s_700MHz_T-Mobile_UL - Apply m4s detector over 300 1024-pt FFTs at 700.50 MHz.",
                            ),
                            (
                                "acquire_m4s_700MHz_Verizon_DL",
                                "acquire_m4s_700MHz_Verizon_DL - Apply m4s detector over 300 1024-pt FFTs at 751.00 MHz.",
                            ),
                            (
                                "acquire_m4s_700MHz_Verizon_UL",
                                "acquire_m4s_700MHz_Verizon_UL - Apply m4s detector over 300 1024-pt FFTs at 782.00 MHz.",
                            ),
                            (
                                "logger",
                                'logger - Log the message "running test {name}/{tid}".',
                            ),
                            (
                                "survey_700MHz_band_10dB_1000ms_iq",
                                "survey_700MHz_band_10dB_1000ms_iq - Capture time-domain IQ samples at the following 10 frequencies: 700.50 MHz, 709.00 MHz, 731.50 MHz, 739.00 MHz, 751.00 MHz, 763.00 MHz, 772.00 MHz, 782.00 MHz, 793.00 MHz, 802.00 MHz.",
                            ),
                            (
                                "survey_700MHz_band_10dB_80ms_iq",
                                "survey_700MHz_band_10dB_80ms_iq - Capture time-domain IQ samples at the following 10 frequencies: 700.50 MHz, 709.00 MHz, 731.50 MHz, 739.00 MHz, 751.00 MHz, 763.00 MHz, 772.00 MHz, 782.00 MHz, 793.00 MHz, 802.00 MHz.",
                            ),
                            (
                                "survey_700MHz_band_20dB_1000ms_iq",
                                "survey_700MHz_band_20dB_1000ms_iq - Capture time-domain IQ samples at the following 10 frequencies: 700.50 MHz, 709.00 MHz, 731.50 MHz, 739.00 MHz, 751.00 MHz, 763.00 MHz, 772.00 MHz, 782.00 MHz, 793.00 MHz, 802.00 MHz.",
                            ),
                            (
                                "survey_700MHz_band_20dB_80ms_iq",
                                "survey_700MHz_band_20dB_80ms_iq - Capture time-domain IQ samples at the following 10 frequencies: 700.50 MHz, 709.00 MHz, 731.50 MHz, 739.00 MHz, 751.00 MHz, 763.00 MHz, 772.00 MHz, 782.00 MHz, 793.00 MHz, 802.00 MHz.",
                            ),
                            (
                                "survey_700MHz_band_40dB_1000ms_iq",
                                "survey_700MHz_band_40dB_1000ms_iq - Capture time-domain IQ samples at the following 10 frequencies: 700.50 MHz, 709.00 MHz, 731.50 MHz, 739.00 MHz, 751.00 MHz, 763.00 MHz, 772.00 MHz, 782.00 MHz, 793.00 MHz, 802.00 MHz.",
                            ),
                            (
                                "survey_700MHz_band_40dB_80ms_iq",
                                "survey_700MHz_band_40dB_80ms_iq - Capture time-domain IQ samples at the following 10 frequencies: 700.50 MHz, 709.00 MHz, 731.50 MHz, 739.00 MHz, 751.00 MHz, 763.00 MHz, 772.00 MHz, 782.00 MHz, 793.00 MHz, 802.00 MHz.",
                            ),
                            (
                                "survey_700MHz_band_iq",
                                "survey_700MHz_band_iq - Capture time-domain IQ samples at the following 10 frequencies: 700.50 MHz, 709.00 MHz, 731.50 MHz, 739.00 MHz, 751.00 MHz, 763.00 MHz, 772.00 MHz, 782.00 MHz, 793.00 MHz, 802.00 MHz.",
                            ),
                        ],
                        help_text="[Required] The name of the action to be scheduled",
                        max_length=50,
                    ),
                ),
                (
                    "priority",
                    models.SmallIntegerField(
                        default=10,
                        help_text="Lower number is higher priority (default=10)",
                        validators=[
                            django.core.validators.MinValueValidator(-20),
                            django.core.validators.MaxValueValidator(19),
                        ],
                    ),
                ),
                (
                    "start",
                    models.BigIntegerField(
                        blank=True,
                        default=schedule.models.schedule_entry.next_schedulable_timefn,
                        help_text="Absolute time (epoch) to start, or leave blank for 'now'",
                    ),
                ),
                (
                    "stop",
                    models.BigIntegerField(
                        blank=True,
                        help_text="Absolute time (epoch) to stop, or leave blank for 'never'",
                        null=True,
                    ),
                ),
                (
                    "interval",
                    models.PositiveIntegerField(
                        blank=True,
                        help_text="Seconds between tasks, or leave blank to run once",
                        null=True,
                        validators=[django.core.validators.MinValueValidator(1)],
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Indicates whether the entry should be removed from the scheduler without removing it from the system",
                    ),
                ),
                (
                    "callback_url",
                    models.URLField(
                        blank=True,
                        help_text="If given, the scheduler will POST a `TaskResult` JSON object to this URL after each task completes",
                        null=True,
                    ),
                ),
                (
                    "next_task_time",
                    models.BigIntegerField(
                        editable=False,
                        help_text="The time the next task is scheduled to be executed",
                        null=True,
                    ),
                ),
                (
                    "next_task_id",
                    models.IntegerField(
                        default=1,
                        editable=False,
                        help_text="The id of the next task to be executed",
                    ),
                ),
                (
                    "created",
                    models.DateTimeField(
                        auto_now_add=True, help_text="The date the entry was created"
                    ),
                ),
                (
                    "modified",
                    models.DateTimeField(
                        auto_now=True, help_text="The date the entry was modified"
                    ),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        editable=False,
                        help_text="The name of the user who owns the entry",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="schedule_entries",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "request",
                    models.ForeignKey(
                        editable=False,
                        help_text="The request that created the entry",
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="schedule.Request",
                    ),
                ),
            ],
            options={"db_table": "schedule", "ordering": ("created",)},
        ),
    ]
