import wafer
from django import forms

from wafer.talks.models import Talk
from django_select2.forms import Select2MultipleWidget
from markitup.widgets import MarkItUpWidget


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
            # "abstract": forms.Textarea(attrs={"class": "input-xxlarge"}),
            "abstract": MarkItUpWidget(
                attrs={
                    "class": "input-xxlarge textarea appearance-none border leading-normal block w-full border-gray-300 bg-white py-2 px-4 text-gray-700 rounded-lg focus:outline-none"
                }
            ),
            "notes": forms.Textarea(),
            "authors": Select2MultipleWidget,
        }
