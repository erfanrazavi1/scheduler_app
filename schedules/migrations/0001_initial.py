# Generated for the weekly class schedule application.
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ClassSession",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=120)),
                ("instructor", models.CharField(blank=True, max_length=120)),
                (
                    "day",
                    models.IntegerField(
                        choices=[
                            (0, "Saturday"),
                            (1, "Sunday"),
                            (2, "Monday"),
                            (3, "Tuesday"),
                            (4, "Wednesday"),
                            (5, "Thursday"),
                            (6, "Friday"),
                        ],
                        db_index=True,
                        help_text="The class repeats weekly on this day.",
                    ),
                ),
                ("start_time", models.TimeField()),
                ("end_time", models.TimeField()),
                ("location", models.CharField(blank=True, max_length=120)),
                ("description", models.TextField(blank=True)),
                (
                    "color",
                    models.CharField(
                        default="#3b82f6",
                        help_text="Hex accent color, e.g. #3b82f6.",
                        max_length=7,
                        validators=[
                            django.core.validators.RegexValidator(
                                message="Color must be a hex value such as #3b82f6.",
                                regex="^#[0-9A-Fa-f]{6}$",
                            )
                        ],
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Inactive classes are hidden from the public schedule.",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "class",
                "verbose_name_plural": "classes",
                "ordering": ["day", "start_time"],
            },
        ),
        migrations.AddIndex(
            model_name="classsession",
            index=models.Index(
                fields=["is_active", "day", "start_time"],
                name="schedule_active_day_start_idx",
            ),
        ),
    ]
