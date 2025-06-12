from django.conf import settings
from django.db import models
from django.utils import timezone


class VisaInvitationLetter(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='visa_letters')

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='approved_visa_letters'
    )

    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)

    participant_name = models.CharField(max_length=255)
    passport_number = models.CharField(max_length=50)
    country_of_origin = models.CharField(max_length=100)
    email = models.EmailField()

    registration_type = models.CharField(max_length=50, default='Attendee')
    arrival_date = models.DateField()
    departure_date = models.DateField()

    is_speaker = models.BooleanField(default=False)
    presentation_title = models.CharField(max_length=255, blank=True, null=True)

    embassy_address = models.TextField(default='Embassy of South Africa')

    organizer_name = models.CharField(max_length=255, default='PyCon Africa 2025 Organizing Committee')
    organizer_role = models.CharField(max_length=100, default='Conference Chair')
    contact_email = models.EmailField(default='team@pycon.africa')
    contact_phone = models.CharField(max_length=20, default='+27 XX XXX XXXX')

    conference_location = models.CharField(max_length=100, default='Johannesburg, South Africa')
    conference_dates = models.CharField(max_length=100, default='October 8-12, 2025')
    website_url = models.URLField(default='africa.pycon.org')

    def __str__(self):
        return f"Visa Letter for {self.participant_name} ({self.get_status_display()})"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Visa Invitation Letter"
        verbose_name_plural = "Visa Invitation Letters"
        unique_together = [
            ('user', 'participant_name', 'passport_number', 'arrival_date', 'departure_date'),
            ('user', 'email', 'country_of_origin', 'arrival_date', 'departure_date')
        ]
