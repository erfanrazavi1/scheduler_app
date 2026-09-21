from django.contrib import admin
from django.utils.html import format_html

from .models import ClassSession


@admin.register(ClassSession)
class ClassSessionAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "day",
        "time_range",
        "instructor",
        "location",
        "color_swatch",
        "is_active",
    )
    list_filter = ("is_active", "day", "instructor")
    search_fields = ("title", "instructor", "location", "description")
    list_editable = ("is_active",)
    ordering = ("day", "start_time")
    list_per_page = 30
    actions = ("activate", "deactivate")
    readonly_fields = ("created_at", "updated_at")
    save_on_top = True

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "instructor",
                    "day",
                    ("start_time", "end_time"),
                    "location",
                )
            },
        ),
        ("Presentation", {"fields": ("color", "is_active")}),
        ("Details", {"fields": ("description",)}),
        ("Timestamps", {"classes": ("collapse",), "fields": ("created_at", "updated_at")}),
    )

    @admin.display(description="Time", ordering="start_time")
    def time_range(self, obj):
        return obj.time_range

    @admin.display(description="Color")
    def color_swatch(self, obj):
        return format_html(
            '<span style="display:inline-block;width:1.1rem;height:1.1rem;'
            'border-radius:9999px;border:1px solid rgba(0,0,0,.15);'
            'background:{}"></span>',
            obj.color,
        )

    @admin.action(description="Activate selected classes")
    def activate(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} class(es) activated.")

    @admin.action(description="Deactivate selected classes")
    def deactivate(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} class(es) deactivated.")
