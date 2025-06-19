import os
import tempfile
from smtplib import SMTPException

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone
from weasyprint import HTML
from wafer.talks.models import Talk


def generate_visa_letter_pdf(request, visa_letter):
    """Generate PDF file for visa invitation letter."""
    current_date = timezone.now().strftime("%B %d, %Y")
    talk = Talk.objects.filter(authors=visa_letter.user, status="accepted").first()
    is_speaker = talk is not None
    presentation_title = talk.title if talk else None
    registration_type = "Speaker" if is_speaker else "Attendee"

    context = {
        "current_date": current_date,
        "participant_name": visa_letter.participant_name,
        "passport_number": visa_letter.passport_number,
        "country_of_origin": visa_letter.country_of_origin.name,
        "registration_type": registration_type,
        "is_speaker": is_speaker,
        "presentation_title": presentation_title if is_speaker else None,
        "embassy_address": visa_letter.embassy_address,
        "conference_location": settings.CONFERENCE_LOCATION,
        "conference_name": settings.CONFERENCE_NAME,
        "conference_dates": settings.CONFERENCE_DATES,
        "organizer_name": settings.VISA_ORGANISER_NAME,
        "organizer_role": settings.VISA_ORGANISER_ROLE,
        "contact_email": settings.VISA_ORGANISER_CONTACT_EMAIL,
        "contact_phone": settings.VISA_ORGANISER_CONTACT_PHONE,
        "website_url": settings.WEBSITE_URL,
        "logo_url": request.build_absolute_uri("/static/img/letter_header.png"),
    }

    html_string = render_to_string("website/visa_letter_template.html", context)
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as output_file:
        html = HTML(string=html_string, base_url=request.build_absolute_uri("/"))
        html.write_pdf(output_file)
        temp_file_path = output_file.name

    # DEBUG: Save a copy to project root for debugging
    import shutil
    debug_path = f"debug_visa_letter_{visa_letter.participant_name.replace(' ', '_')}.pdf"
    shutil.copy2(temp_file_path, debug_path)

    return temp_file_path


def send_visa_approval_email(request, visa_letter, pdf_file_path):
    """Send visa approval email with PDF attachment."""
    try:
        subject = f"PyCon Africa 2025 - Your Visa Invitation Letter"

        context = {
            "participant_name": visa_letter.participant_name,
            "conference_name": settings.CONFERENCE_NAME,
            "conference_dates": settings.CONFERENCE_DATES,
            "conference_location": settings.CONFERENCE_LOCATION,
            "organizer_email": settings.VISA_ORGANISER_CONTACT_EMAIL,
            "organizer_phone": settings.VISA_ORGANISER_CONTACT_PHONE,
            "website_url": settings.WEBSITE_URL,
        }

        html_message = render_to_string("website/visa_letter_email.html", context)

        email = EmailMultiAlternatives(
            subject=subject,
            body=html_message,
            from_email=settings.VISA_ORGANISER_CONTACT_EMAIL,
            to=[visa_letter.user.email],
            reply_to=[settings.VISA_ORGANISER_CONTACT_EMAIL],
        )

        with open(pdf_file_path, "rb") as pdf:
            pdf_content = pdf.read()
            email.attach(
                f"PyCon_Africa_2025_Visa_Letter_{visa_letter.participant_name}.pdf",
                pdf_content,
                "application/pdf",
            )

        email.send(fail_silently=False)
        return True

    except (SMTPException, ConnectionError, OSError, IOError) as e:
        raise e
    finally:
        if os.path.exists(pdf_file_path):
            os.unlink(pdf_file_path)


def send_visa_rejection_email(request, visa_letter, rejection_reason):
    """Send visa rejection email."""
    try:
        subject = f"PyCon Africa 2025 - Visa Invitation Letter Request"

        context = {
            "participant_name": visa_letter.participant_name,
            "rejection_reason": rejection_reason,
            "conference_name": settings.CONFERENCE_NAME,
            "conference_dates": settings.CONFERENCE_DATES,
            "conference_location": settings.CONFERENCE_LOCATION,
            "organizer_email": settings.VISA_ORGANISER_CONTACT_EMAIL,
            "organizer_phone": settings.VISA_ORGANISER_CONTACT_PHONE,
            "website_url": settings.WEBSITE_URL,
        }

        html_message = render_to_string(
            "website/visa_letter_rejection_email.html",
            context,
        )

        email = EmailMultiAlternatives(
            subject=subject,
            body=html_message,
            from_email=settings.VISA_ORGANISER_CONTACT_EMAIL,
            to=[visa_letter.user.email],
            reply_to=[settings.VISA_ORGANISER_CONTACT_EMAIL],
        )

        email.send(fail_silently=False)
        return True

    except (SMTPException, ConnectionError, OSError) as e:
        raise e


def approve_visa_letter(request, visa_letter):
    """
    Approve a visa letter and send notification email.
    Returns (success: bool, error_message: str or None)
    """
    try:
        visa_letter.status = "approved"
        visa_letter.approved_at = timezone.now()
        visa_letter.approved_by = request.user

        pdf_file_path = generate_visa_letter_pdf(request, visa_letter)
        email_sent = send_visa_approval_email(request, visa_letter, pdf_file_path)

        if email_sent:
            visa_letter.email_sent_at = timezone.now()

        visa_letter.save(
            update_fields=["status", "approved_at", "approved_by", "email_sent_at"]
        )

        return True, None

    except (SMTPException, ConnectionError, OSError, IOError) as e:
        return False, str(e)


def reject_visa_letter(request, visa_letter, rejection_reason):
    """
    Reject a visa letter and send notification email.
    Returns (success: bool, error_message: str or None)
    """
    try:
        visa_letter.status = "rejected"
        visa_letter.rejection_reason = rejection_reason

        email_sent = send_visa_rejection_email(request, visa_letter, rejection_reason)

        if email_sent:
            visa_letter.email_sent_at = timezone.now()

        visa_letter.save(update_fields=["status", "rejection_reason", "email_sent_at"])

        return True, None

    except (SMTPException, ConnectionError, OSError, IOError) as e:
        return False, str(e)
