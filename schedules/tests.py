from datetime import date, time, timedelta

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .forms import ClassSessionForm
from .models import ClassSession, Day
from .utils import (
    format_jalali,
    gregorian_to_jalali,
    parse_week_param,
    start_of_week,
    to_persian_digits,
    week_days,
    week_range_label,
)


class ClassSessionModelTests(TestCase):
    def test_valid_class_creation(self):
        session = ClassSession.objects.create(
            title="Python",
            instructor="Rezaei",
            day=Day.SATURDAY,
            start_time=time(14, 0),
            end_time=time(16, 0),
            location="Room 203",
        )
        self.assertEqual(str(session), "Python (Saturday 14:00)")
        self.assertEqual(session.time_range, "14:00 — 16:00")
        self.assertEqual(session.day_name_fa, "شنبه")
        self.assertTrue(session.is_active)

    def test_end_time_must_be_after_start_time(self):
        session = ClassSession(
            title="Bad",
            day=Day.MONDAY,
            start_time=time(16, 0),
            end_time=time(14, 0),
        )
        with self.assertRaises(ValidationError) as ctx:
            session.full_clean()
        self.assertIn("end_time", ctx.exception.message_dict)
        self.assertEqual(
            ctx.exception.message_dict["end_time"][0],
            "ساعت پایان باید بعد از ساعت شروع باشد.",
        )

    def test_equal_start_and_end_time_is_invalid(self):
        session = ClassSession(
            title="Zero length",
            day=Day.MONDAY,
            start_time=time(10, 0),
            end_time=time(10, 0),
        )
        with self.assertRaises(ValidationError):
            session.full_clean()

    def test_overlaps_are_allowed(self):
        ClassSession.objects.create(
            title="A", day=Day.MONDAY, start_time=time(10, 0), end_time=time(12, 0)
        )
        second = ClassSession(
            title="B", day=Day.MONDAY, start_time=time(11, 0), end_time=time(13, 0)
        )
        second.full_clean()
        second.save()
        self.assertEqual(ClassSession.objects.filter(day=Day.MONDAY).count(), 2)

    def test_overlapping_helper_returns_intersecting_classes(self):
        first = ClassSession.objects.create(
            title="A", day=Day.MONDAY, start_time=time(10, 0), end_time=time(12, 0)
        )
        overlapping = ClassSession.objects.create(
            title="B", day=Day.MONDAY, start_time=time(11, 0), end_time=time(13, 0)
        )
        touching = ClassSession.objects.create(
            title="C", day=Day.MONDAY, start_time=time(12, 0), end_time=time(14, 0)
        )
        inactive = ClassSession.objects.create(
            title="D", day=Day.MONDAY, start_time=time(11, 0), end_time=time(13, 0),
            is_active=False,
        )

        conflicts = list(first.conflicts())
        self.assertIn(overlapping, conflicts)
        self.assertNotIn(touching, conflicts)  # adjacent is not an overlap
        self.assertNotIn(inactive, conflicts)  # inactive classes are ignored


class DayOrderingTests(TestCase):
    def test_default_ordering_is_day_then_start_time(self):
        late = ClassSession.objects.create(
            title="Late", day=Day.WEDNESDAY, start_time=time(15, 0), end_time=time(16, 0)
        )
        early = ClassSession.objects.create(
            title="Early", day=Day.WEDNESDAY, start_time=time(8, 0), end_time=time(9, 0)
        )
        saturday = ClassSession.objects.create(
            title="Sat", day=Day.SATURDAY, start_time=time(9, 0), end_time=time(10, 0)
        )
        self.assertEqual(list(ClassSession.objects.all()), [saturday, early, late])

    def test_python_weekday_mapping(self):
        self.assertEqual(Day.from_python_weekday(5), Day.SATURDAY)  # Saturday
        self.assertEqual(Day.from_python_weekday(6), Day.SUNDAY)  # Sunday
        self.assertEqual(Day.from_python_weekday(0), Day.MONDAY)  # Monday
        self.assertEqual(Day.from_python_weekday(4), Day.FRIDAY)  # Friday

    def test_day_choices_are_ordered_saturday_first(self):
        """The database representation stays integer-ordered and untouched."""
        values = [value for value, _ in Day.choices]
        self.assertEqual(values, list(range(7)))
        self.assertEqual(Day.choices[0][1], "Saturday")
        self.assertEqual(Day.choices[-1][1], "Friday")


class PersianFormattingTests(TestCase):
    def test_gregorian_to_jalali_known_dates(self):
        self.assertEqual(gregorian_to_jalali(2024, 3, 20), (1403, 1, 1))
        self.assertEqual(gregorian_to_jalali(2024, 1, 5), (1402, 10, 15))
        self.assertEqual(gregorian_to_jalali(2025, 3, 21), (1404, 1, 1))

    def test_format_jalali_uses_persian_digits(self):
        self.assertEqual(format_jalali(date(2024, 1, 5)), "۱۵ دی")
        self.assertEqual(format_jalali(date(2024, 1, 5), with_year=True), "۱۵ دی ۱۴۰۲")

    def test_to_persian_digits(self):
        self.assertEqual(to_persian_digits("14:00 — 16:00"), "۱۴:۰۰ — ۱۶:۰۰")

    def test_week_range_label(self):
        self.assertEqual(week_range_label(date(2024, 1, 6)), "۱۶ دی تا ۲۲ دی")


class WeekUtilsTests(TestCase):
    def test_start_of_week_returns_saturday(self):
        self.assertEqual(start_of_week(date(2024, 1, 5)), date(2023, 12, 30))
        self.assertEqual(start_of_week(date(2023, 12, 30)), date(2023, 12, 30))
        self.assertEqual(start_of_week(date(2024, 1, 3)), date(2023, 12, 30))

    def test_parse_week_param_normalizes_to_saturday(self):
        self.assertEqual(
            parse_week_param("2024-01-03", today=date(2024, 1, 3)),
            date(2023, 12, 30),
        )

    def test_parse_week_param_falls_back_on_invalid_input(self):
        self.assertEqual(
            parse_week_param("not-a-date", today=date(2024, 1, 3)),
            date(2023, 12, 30),
        )
        self.assertEqual(
            parse_week_param(None, today=date(2024, 1, 3)),
            date(2023, 12, 30),
        )

    def test_week_days_are_ordered_and_marked_today(self):
        today = timezone.localdate()
        week_start = start_of_week(today)
        days = week_days(week_start)
        self.assertEqual(len(days), 7)
        self.assertEqual(days[0]["value"], Day.SATURDAY)
        self.assertEqual(days[0]["date"], week_start)
        self.assertEqual(days[0]["name"], "شنبه")
        self.assertEqual(sum(1 for d in days if d["is_today"]), 1)


class ClassSessionFormTests(TestCase):
    def test_day_choices_are_persian(self):
        form = ClassSessionForm()
        labels = [label for _, label in form.fields["day"].choices]
        self.assertEqual(labels[0], "شنبه")
        self.assertEqual(labels[-1], "جمعه")
        self.assertNotIn("Saturday", labels)

    def test_form_rejects_end_before_start(self):
        form = ClassSessionForm(
            data={
                "title": "x",
                "day": Day.MONDAY,
                "start_time": "10:00",
                "end_time": "09:00",
                "color": "#3b82f6",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("end_time", form.errors)

    def test_form_requires_title(self):
        form = ClassSessionForm(
            data={
                "title": "",
                "day": Day.MONDAY,
                "start_time": "10:00",
                "end_time": "11:00",
                "color": "#3b82f6",
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)


class WeeklyScheduleViewTests(TestCase):
    def setUp(self):
        self.url = reverse("schedules:weekly")
        self.create_url = reverse("schedules:class_create")

    def payload(self, **overrides):
        data = {
            "title": "ریاضی",
            "instructor": "رضایی",
            "day": Day.SATURDAY,
            "start_time": "08:00",
            "end_time": "10:00",
            "location": "کلاس ۱۰۱",
            "description": "توضیح کلاس",
            "color": "#3b82f6",
            "week": "2024-01-03",
        }
        data.update(overrides)
        return data

    # -- basic rendering -------------------------------------------------

    def test_homepage_renders(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "schedules/weekly.html")

    def test_homepage_is_public_and_rtl_persian(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'lang="fa"')
        self.assertContains(response, 'dir="rtl"')

    def test_all_persian_day_names_are_rendered(self):
        response = self.client.get(self.url)
        for name in Day.persian_names().values():
            self.assertContains(response, name)

    def test_active_classes_are_shown_and_inactive_hidden(self):
        ClassSession.objects.create(
            title="Visible Class", day=Day.SATURDAY,
            start_time=time(8, 0), end_time=time(9, 0),
        )
        ClassSession.objects.create(
            title="Hidden Class", day=Day.SATURDAY,
            start_time=time(10, 0), end_time=time(11, 0), is_active=False,
        )
        response = self.client.get(self.url)
        self.assertContains(response, "Visible Class")
        self.assertNotContains(response, "Hidden Class")

    def test_empty_day_renders_persian_empty_state(self):
        response = self.client.get(self.url)
        self.assertContains(response, "کلاسی برای این روز ثبت نشده است")

    def test_today_classes_are_listed(self):
        today_value = Day.from_python_weekday(timezone.localdate().weekday())
        ClassSession.objects.create(
            title="Today Session", day=today_value,
            start_time=time(7, 0), end_time=time(8, 0),
        )
        response = self.client.get(self.url)
        self.assertContains(response, "Today Session")
        self.assertEqual(len(response.context["today_classes"]), 1)

    def test_week_navigation_links(self):
        response = self.client.get(self.url)
        self.assertTrue(response.context["is_current_week"])
        week_start = response.context["week_start"]
        self.assertEqual(response.context["prev_week"], week_start - timedelta(days=7))
        self.assertEqual(response.context["next_week"], week_start + timedelta(days=7))

    def test_navigation_to_another_week(self):
        target = date(2024, 1, 3)
        response = self.client.get(self.url, {"week": target.isoformat()})
        self.assertFalse(response.context["is_current_week"])
        self.assertEqual(response.context["week_start"], start_of_week(target))

    # -- create ----------------------------------------------------------

    def test_valid_post_creates_class_in_database(self):
        response = self.client.post(self.create_url, self.payload())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ClassSession.objects.count(), 1)
        session = ClassSession.objects.get()
        self.assertEqual(session.title, "ریاضی")
        self.assertEqual(session.start_time, time(8, 0))
        self.assertEqual(session.end_time, time(10, 0))

    def test_created_class_appears_on_correct_day(self):
        self.client.post(self.create_url, self.payload(day=Day.MONDAY))
        response = self.client.get(self.url)
        monday = next(
            day for day in response.context["days"] if day["value"] == Day.MONDAY
        )
        self.assertEqual([s.title for s in monday["classes"]], ["ریاضی"])

    def test_created_class_persists_across_requests(self):
        self.client.post(self.create_url, self.payload())
        self.client.get(self.url)  # a completely new request/session
        response = self.client.get(self.url)
        self.assertContains(response, "ریاضی")

    def test_invalid_time_range_does_not_create_class(self):
        response = self.client.post(
            self.create_url, self.payload(start_time="10:00", end_time="09:00")
        )
        self.assertEqual(ClassSession.objects.count(), 0)
        self.assertContains(response, "ساعت پایان باید بعد از ساعت شروع باشد.")

    def test_missing_required_fields_are_rejected(self):
        response = self.client.post(self.create_url, self.payload(title=""))
        self.assertEqual(ClassSession.objects.count(), 0)
        self.assertIn("title", response.context["form"].errors)

    def test_invalid_submission_preserves_values_and_reopens_modal(self):
        response = self.client.post(
            self.create_url,
            self.payload(title="", instructor="رضایی", location="کلاس ۵"),
        )
        self.assertEqual(ClassSession.objects.count(), 0)
        self.assertContains(response, "رضایی")
        self.assertContains(response, "کلاس ۵")
        self.assertEqual(response.context["open_modal"], "form")
        self.assertEqual(response.context["form_mode"], "create")

    def test_invalid_edit_reopens_edit_form(self):
        session = ClassSession.objects.create(
            title="قدیمی", day=Day.SUNDAY,
            start_time=time(8, 0), end_time=time(9, 0),
        )
        edit_url = reverse("schedules:class_edit", args=[session.pk])
        response = self.client.post(
            edit_url, self.payload(title="جدید", start_time="10:00", end_time="09:00")
        )
        self.assertEqual(response.context["form_mode"], "edit")
        self.assertEqual(response.context["open_modal"], "form")
        self.assertEqual(response.context["editing"], session)

    def test_week_parameter_is_preserved_after_create(self):
        response = self.client.post(self.create_url, self.payload())
        self.assertIn("week=2023-12-30", response.url)

    def test_create_via_get_does_not_write(self):
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ClassSession.objects.count(), 0)

    # -- edit ------------------------------------------------------------

    def test_valid_post_updates_class(self):
        session = ClassSession.objects.create(
            title="قدیمی", day=Day.SUNDAY,
            start_time=time(8, 0), end_time=time(9, 0),
        )
        edit_url = reverse("schedules:class_edit", args=[session.pk])
        response = self.client.post(
            edit_url,
            self.payload(title="جدید", day=Day.SUNDAY, start_time="09:00", end_time="11:00"),
        )
        self.assertEqual(response.status_code, 302)
        session.refresh_from_db()
        self.assertEqual(session.title, "جدید")
        self.assertEqual(session.start_time, time(9, 0))

    def test_invalid_edit_keeps_existing_values(self):
        session = ClassSession.objects.create(
            title="قدیمی", day=Day.SUNDAY,
            start_time=time(8, 0), end_time=time(9, 0),
        )
        edit_url = reverse("schedules:class_edit", args=[session.pk])
        self.client.post(
            edit_url, self.payload(title="جدید", start_time="10:00", end_time="09:00")
        )
        session.refresh_from_db()
        self.assertEqual(session.title, "قدیمی")

    # -- delete ----------------------------------------------------------

    def test_delete_via_post_removes_record(self):
        session = ClassSession.objects.create(
            title="حذفی", day=Day.SUNDAY,
            start_time=time(8, 0), end_time=time(9, 0),
        )
        delete_url = reverse("schedules:class_delete", args=[session.pk])
        response = self.client.post(delete_url, {"week": "2024-01-03"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ClassSession.objects.count(), 0)

    def test_delete_via_get_does_not_remove_record(self):
        session = ClassSession.objects.create(
            title="حذفی", day=Day.SUNDAY,
            start_time=time(8, 0), end_time=time(9, 0),
        )
        delete_url = reverse("schedules:class_delete", args=[session.pk])
        response = self.client.get(delete_url)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(ClassSession.objects.count(), 1)

    def test_delete_preserves_week_parameter(self):
        session = ClassSession.objects.create(
            title="حذفی", day=Day.SUNDAY,
            start_time=time(8, 0), end_time=time(9, 0),
        )
        delete_url = reverse("schedules:class_delete", args=[session.pk])
        response = self.client.post(delete_url, {"week": "2024-02-07"})
        self.assertIn("week=2024-02-03", response.url)
