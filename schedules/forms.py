from django import forms

from .models import ClassSession, Day


class ClassSessionForm(forms.ModelForm):
    """Form used to create and edit classes from the public homepage.

    All validation is server-side and authoritative; the template only renders
    labels, widgets and errors. Times are validated by the model's ``clean``.
    """

    class Meta:
        model = ClassSession
        fields = [
            "title",
            "instructor",
            "day",
            "start_time",
            "end_time",
            "location",
            "description",
            "color",
        ]
        labels = {
            "title": "عنوان کلاس",
            "instructor": "مدرس",
            "day": "روز هفته",
            "start_time": "ساعت شروع",
            "end_time": "ساعت پایان",
            "location": "محل برگزاری",
            "description": "توضیحات",
            "color": "رنگ کارت",
        }
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "input", "placeholder": "مثلاً ریاضی پایه"}
            ),
            "instructor": forms.TextInput(
                attrs={"class": "input", "placeholder": "مثلاً خانم رضایی"}
            ),
            "day": forms.Select(attrs={"class": "input"}),
            "start_time": forms.TimeInput(
                attrs={"class": "input", "type": "time"}, format="%H:%M"
            ),
            "end_time": forms.TimeInput(
                attrs={"class": "input", "type": "time"}, format="%H:%M"
            ),
            "location": forms.TextInput(
                attrs={"class": "input", "placeholder": "مثلاً کلاس ۱۰۱"}
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "input",
                    "rows": 3,
                    "placeholder": "توضیحات اختیاری درباره کلاس",
                }
            ),
            "color": forms.TextInput(
                attrs={"class": "input", "type": "color"}
            ),
        }
        error_messages = {
            "title": {
                "required": "عنوان کلاس را وارد کنید.",
                "max_length": "عنوان کلاس نمی‌تواند بیش از ۱۲۰ نویسه باشد.",
            },
            "instructor": {
                "max_length": "نام مدرس نمی‌تواند بیش از ۱۲۰ نویسه باشد.",
            },
            "day": {"required": "روز هفته را انتخاب کنید.", "invalid_choice": "روز انتخاب‌شده معتبر نیست."},
            "start_time": {
                "required": "ساعت شروع را وارد کنید.",
                "invalid": "ساعت شروع معتبر نیست.",
            },
            "end_time": {
                "required": "ساعت پایان را وارد کنید.",
                "invalid": "ساعت پایان معتبر نیست.",
            },
            "location": {
                "max_length": "محل برگزاری نمی‌تواند بیش از ۱۲۰ نویسه باشد.",
            },
            "color": {
                "required": "رنگ کارت را انتخاب کنید.",
                "max_length": "کد رنگ معتبر نیست.",
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Model choices are stored in English; the public UI is Persian.
        self.fields["day"].choices = [
            (value, label) for value, label in Day.persian_names().items()
        ]
