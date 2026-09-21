from datetime import timedelta

from django.contrib import messages
from django.http import HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .forms import ClassSessionForm
from .models import ClassSession, Day
from .utils import (
    format_jalali,
    parse_week_param,
    start_of_week,
    week_days,
    week_range_label,
)


def _week_redirect(week_start):
    return f"{reverse('schedules:weekly')}?week={week_start.isoformat()}"


def _weekly_context(week_start, today, **overrides):
    """Build the full context for the weekly page.

    Classes are loaded in a single query and grouped in memory, so the template
    never triggers N+1 queries.
    """
    sessions = list(ClassSession.objects.filter(is_active=True))
    by_day: dict[int, list[ClassSession]] = {value: [] for value, _ in Day.choices}
    for session in sessions:
        by_day[session.day].append(session)

    days = week_days(week_start)
    for day in days:
        day["classes"] = by_day[day["value"]]

    today_value = Day.from_python_weekday(today.weekday())
    current_week_start = start_of_week(today)
    initial_day = today_value if week_start == current_week_start else Day.SATURDAY

    context = {
        "days": days,
        "today_classes": by_day[today_value],
        "today_name": Day.persian_names()[today_value],
        "today_fa": format_jalali(today, with_year=True),
        "initial_day": initial_day,
        "week_start": week_start,
        "week_param": week_start.isoformat(),
        "week_label": week_range_label(week_start),
        "prev_week": week_start - timedelta(days=7),
        "next_week": week_start + timedelta(days=7),
        "is_current_week": week_start == current_week_start,
        "total_classes": len(sessions),
        "form": ClassSessionForm(initial={"day": initial_day, "color": "#3b82f6"}),
        "form_action": reverse("schedules:class_create"),
        "form_mode": "create",
        "editing": None,
        "open_modal": "",
    }
    context.update(overrides)
    return context


def weekly_schedule(request):
    """Public homepage: the weekly schedule with today's classes."""
    today = timezone.localdate()
    week_start = parse_week_param(request.GET.get("week"), today=today)
    return render(
        request, "schedules/weekly.html", _weekly_context(week_start, today)
    )


def class_create(request):
    """Create a class from the homepage. POST only, then redirect back."""
    today = timezone.localdate()
    if request.method != "POST":
        return redirect(_week_redirect(parse_week_param(None, today=today)))

    week_start = parse_week_param(
        request.POST.get("week") or request.GET.get("week"), today=today
    )
    form = ClassSessionForm(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request, "کلاس با موفقیت ثبت شد.")
        return redirect(_week_redirect(week_start))

    context = _weekly_context(
        week_start,
        today,
        form=form,
        form_action=reverse("schedules:class_create"),
        form_mode="create",
        open_modal="form",
    )
    return render(request, "schedules/weekly.html", context)


def class_edit(request, pk):
    """Edit an existing class from the homepage. POST only, then redirect."""
    today = timezone.localdate()
    session = get_object_or_404(ClassSession, pk=pk)
    if request.method != "POST":
        return redirect(_week_redirect(parse_week_param(None, today=today)))

    week_start = parse_week_param(
        request.POST.get("week") or request.GET.get("week"), today=today
    )
    form = ClassSessionForm(request.POST, instance=session)
    if form.is_valid():
        form.save()
        messages.success(request, "کلاس با موفقیت ویرایش شد.")
        return redirect(_week_redirect(week_start))

    context = _weekly_context(
        week_start,
        today,
        form=form,
        form_action=reverse("schedules:class_edit", args=[session.pk]),
        form_mode="edit",
        editing=session,
        open_modal="form",
    )
    return render(request, "schedules/weekly.html", context)


def class_delete(request, pk):
    """Delete a class. State-changing, therefore POST only."""
    session = get_object_or_404(ClassSession, pk=pk)
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    today = timezone.localdate()
    week_start = parse_week_param(
        request.POST.get("week") or request.GET.get("week"), today=today
    )
    title = session.title
    session.delete()
    messages.success(request, f"کلاس «{title}» حذف شد.")
    return redirect(_week_redirect(week_start))
