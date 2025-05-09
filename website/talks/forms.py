import wafer
from django import forms

from wafer.talks.models import Talk
from django_select2.forms import Select2MultipleWidget


class TalkForm(wafer.talks.forms.TalkForm):
    class Meta:
        model = Talk
        fields = (
            "title",
            "language",
            "talk_type",
            "track",
            "abstract",
            "authors",
            "video",
            "video_reviewer",
            "notes",
            "private_notes",
        )
        widgets = {
            "abstract": forms.Textarea(attrs={"class": "input-xxlarge"}),
            "notes": forms.Textarea(attrs={"class": "input-xxlarge"}),
            "authors": Select2MultipleWidget,
        }
