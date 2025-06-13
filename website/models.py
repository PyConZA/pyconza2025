from django.conf import settings
from django.db import models
from django_countries.fields import CountryField


class VisaInvitationLetter(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='visa_letters',
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='approved_visa_letters'
    )

    email_sent_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True, null=True)

    participant_name = models.CharField(max_length=255)
    passport_number = models.CharField(max_length=50)
    country_of_origin = CountryField(
        blank_label='Select Country',
        help_text="Country of origin for the visa application",
    )

    embassy_address = models.TextField(default=settings.VISA_DEFAULT_EMBASSY_ADDRESS)

    def __str__(self):
        return f"Visa Letter for {self.participant_name} ({self.get_status_display()})"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Visa Invitation Letter"
        verbose_name_plural = "Visa Invitation Letters"
        unique_together = [
            ('user', 'participant_name', 'passport_number',),
            ('user', 'country_of_origin',)
        ]
