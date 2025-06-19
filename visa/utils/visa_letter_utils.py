import os
import tempfile
from smtplib import SMTPException

from django.db import transaction
from django.utils import timezone
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
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

    html_string = render_to_string("visa/visa_letter_template.html", context)
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as output_file:
        html = HTML(string=html_string, base_url=request.build_absolute_uri("/"))
        html.write_pdf(output_file)
        temp_file_path = output_file.name
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

        html_message = render_to_string("visa/visa_letter_email.html", context)

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
            "conference_name": getattr(
                settings, "CONFERENCE_NAME", "PyCon Africa 2025"
            ),
            "conference_dates": getattr(settings, "CONFERENCE_DATES", "March 2025"),
            "conference_location": getattr(
                settings, "CONFERENCE_LOCATION", "Cape Town, South Africa"
            ),
            "organizer_email": settings.VISA_ORGANISER_CONTACT_EMAIL,
            "organizer_phone": getattr(settings, "VISA_ORGANISER_CONTACT_PHONE", ""),
            "website_url": getattr(settings, "WEBSITE_URL", "https://za.pycon.org"),
        }

        try:
            html_message = render_to_string(
                "visa/visa_letter_rejection_email.html",
                context,
            )
        except (FileNotFoundError, ImportError):
            html_message = f"""
            <html>
            <body>
                <h2>PyCon Africa 2025 - Visa Invitation Letter Request</h2>
                <p>Dear {visa_letter.participant_name},</p>
                <p>Unfortunately, we cannot provide a visa invitation letter for your request.</p>
                <p>Reason: {rejection_reason}</p>
                <p>If you have any questions, please contact us at {settings.VISA_ORGANISER_CONTACT_EMAIL}</p>
                <p>Best regards,<br>PyCon Africa 2025 Team</p>
            </body>
            </html>
            """

        email = EmailMultiAlternatives(
            subject=subject,
            body=html_message,
            from_email=settings.VISA_ORGANISER_CONTACT_EMAIL,
            to=[visa_letter.user.email],
            reply_to=[settings.VISA_ORGANISER_CONTACT_EMAIL],
        )

        email.send(fail_silently=False)
        return True

    except (SMTPException, ConnectionError, OSError, IOError) as e:
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


@transaction.atomic
def reject_visa_letter(request, visa_letter, rejection_reason):
    """
    Reject a visa letter and send notification email.
    Returns (success: bool, error_message: str or None)
    """
    try:
        if not hasattr(settings, "VISA_ORGANISER_CONTACT_EMAIL"):
            return False, "VISA_ORGANISER_CONTACT_EMAIL not configured in settings"

        if not settings.VISA_ORGANISER_CONTACT_EMAIL:
            return False, "VISA_ORGANISER_CONTACT_EMAIL is empty in settings"

        visa_letter.status = "rejected"
        visa_letter.rejection_reason = rejection_reason
        visa_letter.save(update_fields=["status", "rejection_reason"])

        email_sent = False
        email_error = None
        try:
            email_sent = send_visa_rejection_email(
                request, visa_letter, rejection_reason
            )
        except Exception as e:
            email_error = str(e)
            print(f"DEBUG: Email sending failed: {email_error}")

        if email_sent:
            visa_letter.email_sent_at = timezone.now()
            visa_letter.save(update_fields=["email_sent_at"])

        if email_sent:
            return True, None
        else:
            return (
                True,
                f"Status updated but email failed: {email_error or 'Unknown email error'}",
            )

    except Exception as e:
        return False, f"Error in reject_visa_letter: {str(e)}"
