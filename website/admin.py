import os
import tempfile

from django import forms
from django.contrib import admin
from django.contrib import messages
from django.core.mail import EmailMessage
from django.shortcuts import render
from django.template.loader import render_to_string
from django.utils import timezone
from weasyprint import HTML

from .models import VisaInvitationLetter


class RejectionForm(forms.Form):
    rejection_reason = forms.CharField(widget=forms.Textarea)


@admin.register(VisaInvitationLetter)
class VisaInvitationLetterAdmin(admin.ModelAdmin):
    list_display = ('participant_name', 'country_of_origin', 'email',
                    'status', 'created_at', 'email_sent')
    list_filter = ('status', 'email_sent', 'is_speaker', 'country_of_origin')
    search_fields = ('participant_name', 'email', 'passport_number', 'country_of_origin')
    date_hierarchy = 'created_at'
    actions = ['approve_and_send_email', 'reject_visa_letters']
    readonly_fields = ('created_at', 'updated_at', 'email_sent', 'email_sent_at',
                       'approved_at', 'approved_by')

    fieldsets = (
        ('Status', {
            'fields': ('status', 'created_at', 'updated_at', 'email_sent',
                       'email_sent_at', 'approved_at', 'approved_by', 'rejection_reason')
        }),
        ('Participant Information', {
            'fields': ('participant_name', 'passport_number', 'country_of_origin', 'email')
        }),
        ('Travel Information', {
            'fields': ('registration_type', 'arrival_date', 'departure_date',
                       'is_speaker', 'presentation_title')
        }),
        ('Embassy Information', {
            'fields': ('embassy_address',)
        }),
        ('Conference Details', {
            'fields': ('conference_location', 'conference_dates', 'website_url',
                       'organizer_name', 'organizer_role', 'contact_email', 'contact_phone'),
            'classes': ('collapse',)
        }),
    )

    def save_model(self, request, obj, form, change):
        original_status = None
        if change:
            try:
                original_obj = VisaInvitationLetter.objects.get(pk=obj.pk)
                original_status = original_obj.status
            except VisaInvitationLetter.DoesNotExist:
                pass

        super().save_model(request, obj, form, change)

        if original_status and original_status != 'approved' and obj.status == 'approved':
            try:
                obj.approved_at = timezone.now()
                obj.approved_by = request.user

                pdf_file = self.generate_pdf(request, obj)
                email_sent = self.send_visa_letter_email(request, obj, pdf_file)

                if email_sent:
                    obj.email_sent = True
                    obj.email_sent_at = timezone.now()
                    obj.save(update_fields=['approved_at', 'approved_by', 'email_sent', 'email_sent_at'])

                    self.message_user(
                        request,
                        f"Visa letter for {obj.participant_name} approved and email sent.",
                        level=messages.SUCCESS
                    )
            except Exception as e:
                self.message_user(
                    request,
                    f"Error sending approval email for {obj.participant_name}: {str(e)}",
                    level=messages.ERROR
                )

        elif original_status and original_status != 'rejected' and obj.status == 'rejected':
            try:
                if obj.rejection_reason:
                    email_sent = self.send_rejection_email(request, obj, obj.rejection_reason)

                    if email_sent:
                        obj.email_sent = True
                        obj.email_sent_at = timezone.now()
                        obj.save(update_fields=['email_sent', 'email_sent_at'])

                        self.message_user(
                            request,
                            f"Rejection email sent to {obj.participant_name}.",
                            level=messages.SUCCESS
                        )
                else:
                    self.message_user(
                        request,
                        f"No rejection reason provided. Rejection email was not sent.",
                        level=messages.WARNING
                    )
            except Exception as e:
                self.message_user(
                    request,
                    f"Error sending rejection email for {obj.participant_name}: {str(e)}",
                    level=messages.ERROR
                )

    def approve_and_send_email(self, request, queryset):
        if not queryset.exists():
            self.message_user(request, "No visa letters selected for approval.", level=messages.ERROR)
            return

        success_count = 0
        error_count = 0

        for letter in queryset.filter(status='pending'):
            try:
                letter.status = 'approved'
                letter.approved_at = timezone.now()
                letter.approved_by = request.user
                letter.save()

                pdf_file = self.generate_pdf(request, letter)

                email_sent = self.send_visa_letter_email(request, letter, pdf_file)

                if email_sent:
                    letter.email_sent = True
                    letter.email_sent_at = timezone.now()
                    letter.save()
                    success_count += 1
                else:
                    error_count += 1

            except Exception as e:
                error_count += 1
                self.message_user(
                    request,
                    f"Error processing visa letter for {letter.participant_name}: {str(e)}",
                    level=messages.ERROR
                )

        if success_count > 0:
            self.message_user(
                request,
                f"Successfully approved and sent {success_count} visa letter(s).",
                level=messages.SUCCESS
            )

        if error_count > 0:
            self.message_user(
                request,
                f"Failed to process {error_count} visa letter(s). Check for errors.",
                level=messages.WARNING
            )

    approve_and_send_email.short_description = "Approve selected visa letters and send email"

    def reject_visa_letters(self, request, queryset):
        context = {
            'queryset': queryset,
            'opts': self.model._meta,
        }

        if request.POST.get('post') == 'yes':
            form = RejectionForm(request.POST)
            if form.is_valid():
                rejection_reason = form.cleaned_data['rejection_reason']
                success_count = 0
                error_count = 0

                for letter in queryset:
                    try:
                        letter.status = 'rejected'
                        letter.rejection_reason = rejection_reason
                        letter.save()

                        email_sent = self.send_rejection_email(request, letter, rejection_reason)

                        if email_sent:
                            letter.email_sent = True
                            letter.email_sent_at = timezone.now()
                            letter.save()
                            success_count += 1
                        else:
                            error_count += 1
                    except Exception as e:
                        error_count += 1
                        self.message_user(
                            request,
                            f"Error rejecting visa letter for {letter.participant_name}: {str(e)}",
                            level=messages.ERROR
                        )

                if success_count > 0:
                    self.message_user(
                        request,
                        f"Successfully rejected and notified {success_count} visa letter applicant(s).",
                        level=messages.SUCCESS
                    )

                if error_count > 0:
                    self.message_user(
                        request,
                        f"Failed to process {error_count} rejection(s). Check for errors.",
                        level=messages.WARNING
                    )
                return None
            context['form'] = form
        else:
            context['form'] = RejectionForm()

        return render(
            request,
            'website/rejection_email.html',
            context
        )

    reject_visa_letters.short_description = "Reject selected visa letters"

    def generate_pdf(self, request, visa_letter):
        current_date = timezone.now().strftime("%B %d, %Y")

        context = {
            'current_date': current_date,
            'participant_name': visa_letter.participant_name,
            'passport_number': visa_letter.passport_number,
            'country_of_origin': visa_letter.country_of_origin,
            'registration_type': visa_letter.registration_type,
            'arrival_date': visa_letter.arrival_date.strftime("%B %d, %Y"),
            'departure_date': visa_letter.departure_date.strftime("%B %d, %Y"),
            'is_speaker': visa_letter.is_speaker,
            'presentation_title': visa_letter.presentation_title,
            'embassy_address': visa_letter.embassy_address,
            'conference_location': visa_letter.conference_location,
            'conference_dates': visa_letter.conference_dates,
            'organizer_name': visa_letter.organizer_name,
            'organizer_role': visa_letter.organizer_role,
            'contact_email': visa_letter.contact_email,
            'contact_phone': visa_letter.contact_phone,
            'website_url': visa_letter.website_url,
            'logo_url': request.build_absolute_uri('/static/img/hero-logo-2025.png'),
        }

        html_string = render_to_string('website/visa_letter_template.html', context)

        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as output_file:
            html = HTML(string=html_string, base_url=request.build_absolute_uri('/'))
            html.write_pdf(output_file)
            temp_file_path = output_file.name

        return temp_file_path

    def send_visa_letter_email(self, request, visa_letter, pdf_file_path):
        try:
            subject = f"PyCon Africa 2025 - Your Visa Invitation Letter"

            message = f"""Dear {visa_letter.participant_name},

            Your visa invitation letter for PyCon Africa 2025 has been approved and is attached to this email.
            
            Please print this letter and include it with your visa application to the South African embassy/consulate.
            
            If you have any questions or need further assistance, please contact us at {visa_letter.contact_email}.
            
            Best regards,
            PyCon Africa 2025 Organizing Team"""

            email = EmailMessage(
                subject=subject,
                body=message,
                from_email=visa_letter.contact_email,
                to=[visa_letter.email],
                reply_to=[visa_letter.contact_email],
            )

            with open(pdf_file_path, 'rb') as pdf:
                pdf_content = pdf.read()
                email.attach(
                    f'PyCon_Africa_2025_Visa_Letter_{visa_letter.participant_name}.pdf',
                    pdf_content,
                    'application/pdf'
                )
            email.send(fail_silently=False)

            if os.path.exists(pdf_file_path):
                os.unlink(pdf_file_path)

            return True

        except Exception as e:
            if os.path.exists(pdf_file_path):
                os.unlink(pdf_file_path)
            raise e

    def send_rejection_email(self, request, visa_letter, rejection_reason):
        try:
            subject = f"PyCon Africa 2025 - Visa Invitation Letter Request"

            message = f"""Dear {visa_letter.participant_name},

            Thank you for your interest in attending PyCon Africa 2025.
            
            We regret to inform you that your request for a visa invitation letter has been declined for the following reason:
            
            {rejection_reason}
            
            If you believe this decision was made in error or if you have additional documentation to support your request, please contact us at {visa_letter.contact_email}.
            
            Best regards,
            PyCon Africa 2025 Organizing Team"""

            email = EmailMessage(
                subject=subject,
                body=message,
                from_email=visa_letter.contact_email,
                to=[visa_letter.email],
                reply_to=[visa_letter.contact_email],
            )

            email.send(fail_silently=False)

            return True

        except Exception as e:
            raise e
