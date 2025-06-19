from django import forms
from django.contrib import admin
from django.contrib import messages
from django.shortcuts import render

from .models import VisaInvitationLetter
from .utils.visa_letter_utils import (
    approve_visa_letter,
    reject_visa_letter,
)


class RejectionForm(forms.Form):
    rejection_reason = forms.CharField(widget=forms.Textarea)


@admin.register(VisaInvitationLetter)
class VisaInvitationLetterAdmin(admin.ModelAdmin):
    list_display = (
        "participant_name",
        "country_of_origin",
        "status",
        "created_at",
    )
    list_filter = ("status", "country_of_origin")
    search_fields = ("participant_name", "passport_number", "country_of_origin")
    date_hierarchy = "created_at"
    actions = ["approve_and_send_email", "reject_visa_letters"]
    readonly_fields = (
        "created_at",
        "updated_at",
        "email_sent_at",
        "approved_at",
        "approved_by",
    )

    fieldsets = (
        (
            "Status",
            {
                "fields": (
                    "status",
                    "created_at",
                    "updated_at",
                    "email_sent_at",
                    "approved_at",
                    "approved_by",
                    "rejection_reason",
                )
            },
        ),
        (
            "Participant Information",
            {"fields": ("participant_name", "passport_number", "country_of_origin")},
        ),
        ("Embassy Information", {"fields": ("embassy_address",)}),
    )

    def save_model(self, request, obj, form, change):
        """
        Simplified save_model - only handles basic model saving.
        Email sending logic moved to explicit admin actions.
        """
        super().save_model(request, obj, form, change)

    def approve_and_send_email(self, request, queryset):
        """Approve selected visa letters and send approval emails."""
        if not queryset.exists():
            self.message_user(
                request, "No visa letters selected for approval.", level=messages.ERROR
            )
            return

        success_count = 0
        error_count = 0

        for letter in queryset.filter(status="pending"):
            success, error_message = approve_visa_letter(request, letter)

            if success:
                success_count += 1
                self.message_user(
                    request,
                    f"Visa letter for {letter.participant_name} approved and email sent.",
                    level=messages.SUCCESS,
                )
            else:
                error_count += 1
                self.message_user(
                    request,
                    f"Error processing visa letter for {letter.participant_name}: {error_message}",
                    level=messages.ERROR,
                )

        if success_count > 0:
            self.message_user(
                request,
                f"Successfully approved and sent {success_count} visa letter(s).",
                level=messages.SUCCESS,
            )

        if error_count > 0:
            self.message_user(
                request,
                f"Failed to process {error_count} visa letter(s). Check for errors.",
                level=messages.WARNING,
            )

    def reject_visa_letters(self, request, queryset):
        """Reject selected visa letters with reason and send rejection emails."""
        context = {
            "queryset": queryset,
            "opts": self.model._meta,
        }

        if request.POST.get("post") == "yes":
            form = RejectionForm(request.POST)
            if form.is_valid():
                rejection_reason = form.cleaned_data["rejection_reason"]
                success_count = 0
                error_count = 0

                for letter in queryset:
                    success, error_message = reject_visa_letter(
                        request, letter, rejection_reason
                    )

                    if success:
                        success_count += 1
                    else:
                        error_count += 1
                        self.message_user(
                            request,
                            f"Error rejecting visa letter for {letter.participant_name}: {error_message}",
                            level=messages.ERROR,
                        )

                if success_count > 0:
                    self.message_user(
                        request,
                        f"Successfully rejected and notified {success_count} visa letter applicant(s).",
                        level=messages.SUCCESS,
                    )

                if error_count > 0:
                    self.message_user(
                        request,
                        f"Failed to process {error_count} rejection(s). Check for errors.",
                        level=messages.WARNING,
                    )
                return None
            context["form"] = form
        else:
            context["form"] = RejectionForm()

        return render(request, "website/rejection_email_admin_form.html", context)

    reject_visa_letters.short_description = "Reject selected visa letters"
    approve_and_send_email.short_description = "Approve selected visa letters"
