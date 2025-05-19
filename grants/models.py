from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

GRANT_STATUS_CHOICES = (
    ('submitted', 'Application Submitted'),
    ('under_review', 'Application Under Review'),
    ('approved', 'Application Approved'),
    ('rejected', 'Application Rejected'),
    ('accepted', 'Grant Accepted by Applicant'),
    ('declined', 'Grant Declined by Applicant'),
)

class GrantApplication(models.Model):
    # Link to the user
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='grant_application',
        on_delete=models.PROTECT
    )

    # Application Details
    motivation = models.TextField(
        help_text=_("Explain why you would like to attend PyCon Africa and how it would benefit you.")
    )
    contribution = models.TextField(
        help_text=_("Describe any contributions you have made to Python, PyCon Africa, or the broader tech community.")
    )
    financial_need = models.TextField(
        help_text=_("Please explain your financial circumstances and why you need this grant.")
    )
    
    # Grant Requests
    request_travel = models.BooleanField(
        default=False,
        help_text=_("Do you need assistance with travel costs?")
    )
    travel_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Estimated travel costs in USD")
    )
    travel_from = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("Where will you be traveling from?")
    )

    request_accommodation = models.BooleanField(
        default=False,
        help_text=_("Do you need assistance with accommodation?")
    )
    accommodation_nights = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_("Number of nights you need accommodation for")
    )

    request_ticket = models.BooleanField(
        default=False,
        help_text=_("Do you need a conference ticket?")
    )

    # Status and Review
    status = models.CharField(
        max_length=20,
        choices=GRANT_STATUS_CHOICES,
        default='submitted'
    )
    reviewer_notes = models.TextField(
        blank=True,
        help_text=_("Internal notes for reviewers")
    )
    amount_granted = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Total amount granted in USD")
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        permissions = (
            ("can_review_grants", "Can review grant applications"),
        )

    def __str__(self):
        return f"Grant Application - {self.user.username}"

    def get_absolute_url(self):
        return reverse('grants:application_detail', kwargs={'pk': self.pk})

    @property
    def is_pending(self):
        return self.status in ['submitted', 'under_review']

    @property
    def can_edit(self):
        return self.status == 'submitted'
