from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone


class Day(models.IntegerChoices):
    """Day of week, ordered as the local (Persian) week.

    Saturday is the first day of the week, Friday the last. Storing the day as
    an integer keeps sorting trivial in the database and avoids scattering
    day-ordering logic across templates.
    """

    SATURDAY = 0, "Saturday"
    SUNDAY = 1, "Sunday"
    MONDAY = 2, "Monday"
    TUESDAY = 3, "Tuesday"
    WEDNESDAY = 4, "Wednesday"
    THURSDAY = 5, "Thursday"
    FRIDAY = 6, "Friday"

    @classmethod
    def from_python_weekday(cls, weekday: int) -> int:
        """Map ``datetime.weekday()`` (Mon=0..Sun=6) to our ordering."""
        return (weekday + 2) % 7

    @classmethod
    def persian_names(cls) -> dict[int, str]:
        return {
            cls.SATURDAY: "شنبه",
            cls.SUNDAY: "یکشنبه",
            cls.MONDAY: "دوشنبه",
            cls.TUESDAY: "سه‌شنبه",
            cls.WEDNESDAY: "چهارشنبه",
            cls.THURSDAY: "پنجشنبه",
            cls.FRIDAY: "جمعه",
        }

    @classmethod
    def short_persian_names(cls) -> dict[int, str]:
        return {
            cls.SATURDAY: "ش",
            cls.SUNDAY: "ی",
            cls.MONDAY: "د",
            cls.TUESDAY: "س",
            cls.WEDNESDAY: "چ",
            cls.THURSDAY: "پ",
            cls.FRIDAY: "ج",
        }


class ClassSession(models.Model):
    """A recurring weekly class.

    ``day`` is a weekday (not a calendar date); the same class appears every
    week. Times are wall-clock times local to ``TIME_ZONE``.
    """

    COLOR_VALIDATOR = RegexValidator(
        regex=r"^#[0-9A-Fa-f]{6}$",
        message="کد رنگ باید یک مقدار هگز معتبر مانند #3b82f6 باشد.",
    )

    title = models.CharField(max_length=120)
    instructor = models.CharField(max_length=120, blank=True)
    day = models.IntegerField(
        choices=Day.choices,
        db_index=True,
        help_text="The class repeats weekly on this day.",
    )
    start_time = models.TimeField()
    end_time = models.TimeField()
    location = models.CharField(max_length=120, blank=True)
    description = models.TextField(blank=True)
    color = models.CharField(
        max_length=7,
        default="#3b82f6",
        validators=[COLOR_VALIDATOR],
        help_text="Hex accent color, e.g. #3b82f6.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Inactive classes are hidden from the public schedule.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["day", "start_time"]
        indexes = [
            models.Index(
                fields=["is_active", "day", "start_time"],
                name="schedule_active_day_start_idx",
            )
        ]
        verbose_name = "class"
        verbose_name_plural = "classes"

    def __str__(self) -> str:
        return f"{self.title} ({self.get_day_display()} {self.start_time:%H:%M})"

    def clean(self):
        super().clean()
        if self.start_time and self.end_time and self.end_time <= self.start_time:
            raise ValidationError(
                {"end_time": "ساعت پایان باید بعد از ساعت شروع باشد."}
            )

    # -- Display helpers (kept on the model so templates stay logic-free) --

    @property
    def day_name(self) -> str:
        return self.get_day_display()

    @property
    def day_name_fa(self) -> str:
        return Day.persian_names()[self.day]

    @property
    def time_range(self) -> str:
        return f"{self.start_time:%H:%M} — {self.end_time:%H:%M}"

    # -- Overlap policy -------------------------------------------------
    #
    # Overlapping classes are allowed on purpose. Real timetables frequently
    # have parallel sessions (different groups, labs, instructors), and
    # silently rejecting them would be worse than showing them. The helpers
    # below make the behaviour explicit and testable instead of hidden.
    @classmethod
    def overlapping(cls, *, day, start_time, end_time, exclude_pk=None):
        """Active classes on ``day`` whose time range intersects the given one."""
        qs = cls.objects.filter(day=day, is_active=True)
        if exclude_pk is not None:
            qs = qs.exclude(pk=exclude_pk)
        return qs.filter(start_time__lt=end_time, end_time__gt=start_time)

    def conflicts(self):
        if self.pk is None:
            return ClassSession.objects.none()
        return ClassSession.overlapping(
            day=self.day,
            start_time=self.start_time,
            end_time=self.end_time,
            exclude_pk=self.pk,
        )

    def is_today(self) -> bool:
        today = Day.from_python_weekday(timezone.localdate().weekday())
        return self.day == today
