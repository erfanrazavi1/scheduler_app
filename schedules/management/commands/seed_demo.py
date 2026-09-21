from datetime import time

from django.core.management.base import BaseCommand
from django.db import transaction

from schedules.models import ClassSession, Day

DEMO_CLASSES = [
    # Saturday
    {"title": "ریاضی پایه", "instructor": "خانم رضایی", "day": Day.SATURDAY,
     "start_time": time(8, 0), "end_time": time(10, 0), "location": "کلاس ۱۰۱",
     "color": "#3b82f6", "description": "مرور مفاهیم پایه ریاضی و حل تمرین."},
    {"title": "Python", "instructor": "Rezaei", "day": Day.SATURDAY,
     "start_time": time(14, 0), "end_time": time(16, 0), "location": "Room 203",
     "color": "#0ea5e9", "description": "Introduction to Python programming and problem solving."},
    # Sunday
    {"title": "Django", "instructor": "Rezaei", "day": Day.SUNDAY,
     "start_time": time(10, 0), "end_time": time(12, 0), "location": "Room 205",
     "color": "#10b981", "description": "Building web applications with Django."},
    {"title": "زبان انگلیسی", "instructor": "احمدی", "day": Day.SUNDAY,
     "start_time": time(17, 0), "end_time": time(19, 0), "location": "کلاس ۲۰۳",
     "color": "#f59e0b", "description": "مکالمه و گرامر سطح متوسط."},
    # Monday
    {"title": "پایگاه داده", "instructor": "دکتر محمدی", "day": Day.MONDAY,
     "start_time": time(8, 30), "end_time": time(10, 30), "location": "آزمایشگاه ۲",
     "color": "#8b5cf6", "description": "طراحی پایگاه داده رابطه‌ای و دستورات SQL."},
    # Tuesday
    {"title": "Web Design", "instructor": "Karimi", "day": Day.TUESDAY,
     "start_time": time(9, 0), "end_time": time(11, 0), "location": "Studio A",
     "color": "#ec4899", "description": "HTML, CSS and accessible interface design."},
    {"title": "طراحی الگوریتم", "instructor": "دکتر نوری", "day": Day.TUESDAY,
     "start_time": time(13, 0), "end_time": time(15, 0), "location": "کلاس ۳۰۵",
     "color": "#ef4444", "description": "تحلیل الگوریتم‌ها و ساختار داده."},
    # Wednesday
    {"title": "شبکه‌های کامپیوتری", "instructor": "کاظمی", "day": Day.WEDNESDAY,
     "start_time": time(10, 0), "end_time": time(12, 0), "location": "کلاس ۲۰۷",
     "color": "#14b8a6", "description": "مبانی شبکه و پروتکل‌های اینترنت."},
    {"title": "Machine Learning", "instructor": "Dr. Ahmadi", "day": Day.WEDNESDAY,
     "start_time": time(15, 0), "end_time": time(17, 0), "location": "Lab 1",
     "color": "#6366f1", "description": "Foundations of supervised and unsupervised learning."},
    # Thursday
    {"title": "پروژه پایانی", "instructor": "دکتر رضایی", "day": Day.THURSDAY,
     "start_time": time(11, 0), "end_time": time(13, 0), "location": "کلاس ۴۰۱",
     "color": "#a855f7", "description": "جلسه راهنمایی و ارائه پروژه‌های پایانی."},
    # Friday intentionally left without classes.
]


class Command(BaseCommand):
    help = "Load realistic demo class sessions for local development."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing classes before seeding.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["reset"]:
            deleted, _ = ClassSession.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Deleted {deleted} existing class(es)."))

        created = 0
        for data in DEMO_CLASSES:
            _, was_created = ClassSession.objects.get_or_create(
                title=data["title"],
                day=data["day"],
                start_time=data["start_time"],
                defaults={
                    "instructor": data["instructor"],
                    "end_time": data["end_time"],
                    "location": data["location"],
                    "color": data["color"],
                    "description": data["description"],
                },
            )
            created += int(was_created)

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {created} new class(es); {ClassSession.objects.count()} total."
            )
        )
