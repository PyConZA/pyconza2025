from .models import VisaInvitationLetter
from django.contrib import admin

# from django import forms
# from django.contrib import messages
# from django.shortcuts import render
# from django.http import HttpResponseRedirect
# from django.urls import reverse

# from .utils.visa_letter_utils import (
#     approve_visa_letter,
#     reject_visa_letter,
# )


# class RejectionForm(forms.Form):
#     rejection_reason = forms.CharField(
#         widget=forms.Textarea(attrs={"rows": 4, "cols": 60}),
#         label="Rejection Reason",
#         help_text="Please provide a clear reason for rejecting the visa letter request.",
#         required=True,
#     )


@admin.register(VisaInvitationLetter)
class VisaInvitationLetterAdmin(admin.ModelAdmin):
    change_form_template = "visa/admin/visa_letter_change_form.html"

    list_display = (
        "full_name",
        "country_of_origin",
        "status",
        "created_at",
    )
    list_filter = ("status", "country_of_origin")
    search_fields = ("full_name", "passport_number", "country_of_origin")
    date_hierarchy = "created_at"
    # actions = ["approve_and_send_email", "reject_visa_letters"]
    readonly_fields = (
        "created_at",
        "updated_at",
        "email_sent_at",
        "approved_at",
        "approved_by",
        "status",
        "rejection_reason",
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
            {"fields": ("full_name", "passport_number", "country_of_origin")},
        ),
        ("Embassy Information", {"fields": ("embassy_address",)}),
    )

    def response_change(self, request, obj):
        from django.http import HttpResponseRedirect
        from django.urls import reverse
        
        if "_approve" in request.POST:
            obj.approve_and_send_email()
            self.message_user(request, "Visa letter approved and email sent")
        elif "_reject" in request.POST:
            # Redirect to rejection form
            return HttpResponseRedirect(
                reverse('admin:visa_visainvitationletter_reject', args=[obj.pk])
            )
        elif "_permanently_reject" in request.POST:
            # Redirect to permanent rejection form
            return HttpResponseRedirect(
                reverse('admin:visa_visainvitationletter_permanently_reject', args=[obj.pk])
            )

        return super().response_change(request, obj)

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path(
                '<int:object_id>/reject/',
                self.admin_site.admin_view(self.reject_visa_letter_view),
                name='visa_visainvitationletter_reject',
            ),
            path(
                '<int:object_id>/permanently-reject/',
                self.admin_site.admin_view(self.permanently_reject_visa_letter_view),
                name='visa_visainvitationletter_permanently_reject',
            ),
        ]
        return custom_urls + urls

    def reject_visa_letter_view(self, request, object_id):
        from django.shortcuts import render, get_object_or_404, redirect
        from django.contrib import messages
        from django import forms
        
        visa_letter = get_object_or_404(VisaInvitationLetter, pk=object_id)
        
        class RejectionForm(forms.Form):
            rejection_reason = forms.CharField(
                widget=forms.Textarea(attrs={'rows': 4, 'cols': 60}),
                label='Rejection Reason',
                help_text='Please provide a clear reason for rejecting this visa letter request.',
                required=True
            )
        
        if request.method == 'POST':
            form = RejectionForm(request.POST)
            if form.is_valid():
                rejection_reason = form.cleaned_data['rejection_reason']
                
                # Update the visa letter
                visa_letter.status = 'rejected'
                visa_letter.rejection_reason = rejection_reason
                visa_letter.save(update_fields=['status', 'rejection_reason'])
                
                messages.success(request, f'Visa letter for {visa_letter.full_name} has been rejected.')
                return redirect('admin:visa_visainvitationletter_changelist')
        else:
            form = RejectionForm()
        
        context = {
            'title': f'Reject Visa Letter - {visa_letter.full_name}',
            'visa_letter': visa_letter,
            'form': form,
            'opts': self.model._meta,
            'has_change_permission': True,
            'is_permanent': False,
        }
        
        return render(request, 'visa/admin/reject_form.html', context)

    def permanently_reject_visa_letter_view(self, request, object_id):
        from django.shortcuts import render, get_object_or_404, redirect
        from django.contrib import messages
        from django import forms
        
        visa_letter = get_object_or_404(VisaInvitationLetter, pk=object_id)
        
        class PermanentRejectionForm(forms.Form):
            rejection_reason = forms.CharField(
                widget=forms.Textarea(attrs={'rows': 4, 'cols': 60}),
                label='Permanent Rejection Reason',
                help_text='Please provide a clear reason for permanently rejecting this visa letter request. The user will not be able to submit another request.',
                required=True
            )
        
        if request.method == 'POST':
            form = PermanentRejectionForm(request.POST)
            if form.is_valid():
                rejection_reason = form.cleaned_data['rejection_reason']
                
                # Update the visa letter
                visa_letter.status = 'permanently rejected'
                visa_letter.rejection_reason = rejection_reason
                visa_letter.save(update_fields=['status', 'rejection_reason'])
                
                messages.success(request, f'Visa letter for {visa_letter.full_name} has been permanently rejected.')
                return redirect('admin:visa_visainvitationletter_changelist')
        else:
            form = PermanentRejectionForm()
        
        context = {
            'title': f'Permanently Reject Visa Letter - {visa_letter.full_name}',
            'visa_letter': visa_letter,
            'form': form,
            'opts': self.model._meta,
            'has_change_permission': True,
            'is_permanent': True,
        }
        
        return render(request, 'visa/admin/reject_form.html', context)

    # def approve_and_send_email(self, request, queryset):
    #     """Approve selected visa letters and send approval emails."""
    #     if not queryset.exists():
    #         self.message_user(
    #             request, "No visa letters selected for approval.", level=messages.ERROR
    #         )
    #         return

    #     success_count = 0
    #     error_count = 0

    #     for letter in queryset.filter(status="pending"):
    #         success, error_message = approve_visa_letter(request, letter)

    #         if success:
    #             success_count += 1
    #             self.message_user(
    #                 request,
    #                 f"Visa letter for {letter.full_name} approved and email sent.",
    #                 level=messages.SUCCESS,
    #             )
    #         else:
    #             error_count += 1
    #             self.message_user(
    #                 request,
    #                 f"Error processing visa letter for {letter.full_name}: {error_message}",
    #                 level=messages.ERROR,
    #             )

    #     if success_count > 0:
    #         self.message_user(
    #             request,
    #             f"Successfully approved and sent {success_count} visa letter(s).",
    #             level=messages.SUCCESS,
    #         )

    #     if error_count > 0:
    #         self.message_user(
    #             request,
    #             f"Failed to process {error_count} visa letter(s). Check for errors.",
    #             level=messages.WARNING,
    #         )

    # def reject_visa_letters(self, request, queryset):
    #     """Reject selected visa letters with reason and send rejection emails."""
    #     if request.POST.get("post") == "yes":
    #         form = RejectionForm(request.POST)

    #         if form.is_valid():
    #             rejection_reason = form.cleaned_data["rejection_reason"]
    #             success_count = 0
    #             error_count = 0

    #             pending_letters = queryset.filter(status="pending")

    #             if not pending_letters.exists():
    #                 self.message_user(
    #                     request,
    #                     "No pending visa letters found in selection.",
    #                     level=messages.WARNING,
    #                 )
    #                 return HttpResponseRedirect(
    #                     reverse("admin:website_visainvitationletter_changelist")
    #                 )

    #             for letter in pending_letters:
    #                 try:
    #                     success, error_message = reject_visa_letter(
    #                         request, letter, rejection_reason
    #                     )

    #                     if success:
    #                         success_count += 1
    #                         if error_message:
    #                             self.message_user(
    #                                 request,
    #                                 f"Rejected visa letter for {letter.full_name} (status updated, but email failed: {error_message})",
    #                                 level=messages.WARNING,
    #                             )
    #                         else:
    #                             self.message_user(
    #                                 request,
    #                                 f"Successfully rejected visa letter for {letter.full_name} and sent notification email.",
    #                                 level=messages.SUCCESS,
    #                             )
    #                     else:
    #                         error_count += 1
    #                         self.message_user(
    #                             request,
    #                             f"Failed to reject visa letter for {letter.full_name}: {error_message}",
    #                             level=messages.ERROR,
    #                         )

    #                 except Exception as e:
    #                     error_count += 1
    #                     self.message_user(
    #                         request,
    #                         f"Unexpected error processing {letter.full_name}: {str(e)}",
    #                         level=messages.ERROR,
    #                     )
    #             if success_count > 0:
    #                 self.message_user(
    #                     request,
    #                     f"Processed {success_count} visa letter rejection(s).",
    #                     level=messages.SUCCESS,
    #                 )

    #             if error_count > 0:
    #                 self.message_user(
    #                     request,
    #                     f"Failed to process {error_count} rejection(s).",
    #                     level=messages.ERROR,
    #                 )

    #             return HttpResponseRedirect(
    #                 reverse("admin:website_visainvitationletter_changelist")
    #             )

    #         else:
    #             self.message_user(
    #                 request,
    #                 f"Please provide a rejection reason. Form errors: {form.errors}",
    #                 level=messages.ERROR,
    #             )
    #     context = {
    #         "queryset": queryset,
    #         "opts": self.model._meta,
    #         "form": RejectionForm(request.POST if request.POST else None),
    #     }
    #     return render(request, "visa/rejection_email_admin_form.html", context)

    # reject_visa_letters.short_description = "Reject selected visa letters"
    # approve_and_send_email.short_description = "Approve selected visa letters"
