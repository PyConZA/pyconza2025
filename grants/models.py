from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django_countries.fields import CountryField
from django.core.validators import MinValueValidator, MaxValueValidator

GRANT_STATUS_CHOICES = (
    ('submitted', 'Application Submitted'),
    ('under_review', 'Application Under Review'),
    ('approved', 'Application Approved'),
    ('rejected', 'Application Rejected'),
    ('accepted', 'Grant Accepted by Applicant'),
    ('declined', 'Grant Declined by Applicant'),
)

TALK_PROPOSAL_CHOICES = (
    ('yes', 'Yes'),
    ('no', 'No'),
    ('other', 'Other'),
)

GENDER_CHOICES = (
    ('male', 'Male'),
    ('female', 'Female'),
    ('non_binary', 'Non-binary'),
    ('prefer_not_to_say', 'Prefer not to say'),
    ('other', 'Other'),
)

ROLE_CHOICES = (
    ('high_school_student', 'High School Student'),
    ('undergraduate_student', 'Undergraduate Student'),
    ('graduate_student', 'Graduate Student'),
    ('employed', 'Employed'),
    ('self_employed', 'Self-employed/Freelancer'),
    ('between_jobs', 'Between jobs/Seeking opportunities'),
    ('retired', 'Retired'),
    ('prefer_not_to_say', 'Prefer not to say'),
    ('other', 'Other'),
)

TRANSPORTATION_CHOICES = (
    ('air_travel', 'Air travel'),
    ('ground_travel', 'Ground travel (bus, car, train)'),
)

class GrantApplication(models.Model):
    # Link to the user
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='grant_application',
        on_delete=models.PROTECT
    )

    # Personal Information
    phone_number = models.CharField(
        max_length=20,
        default='',
        help_text=_("Your phone number for contact purposes")
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

    # Demographic Information
    talk_proposal = models.CharField(
        max_length=20,
        choices=TALK_PROPOSAL_CHOICES,
        default='no',
        help_text=_("Have you submitted a talk proposal?")
    )
    talk_proposal_details = models.TextField(
        blank=True,
        default='',
        help_text=_("Please provide more details if you selected 'Other'")
    )

    gender = models.CharField(
        max_length=20,
        choices=GENDER_CHOICES,
        default='prefer_not_to_say',
        help_text=_("Gender identity")
    )
    gender_details = models.TextField(
        blank=True,
        default='',
        help_text=_("Please provide more details if you selected 'Other'")
    )

    current_role = models.CharField(
        max_length=30,
        choices=ROLE_CHOICES,
        default='prefer_not_to_say',
        help_text=_("Which of the following best describes your current role?")
    )
    current_role_details = models.TextField(
        blank=True,
        default='',
        help_text=_("Please provide more details if you selected 'Other'")
    )

    # Travel Information
    transportation_type = models.CharField(
        max_length=20,
        choices=TRANSPORTATION_CHOICES,
        blank=True,
        default='',
        help_text=_("What type of transportation were you planning to take?")
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
    travel_from_city = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text=_("City you will be traveling from")
    )
    travel_from_country = CountryField(
        blank=True,
        null=True,
        help_text=_("Country you will be traveling from")
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

    # Additional Information
    conference_benefit = models.TextField(
        default='Not specified',
        help_text=_("How do you hope attending the PyCon Africa 2024 Conference will benefit you?")
    )
    additional_info = models.TextField(
        blank=True,
        default='',
        help_text=_("Is there anything else not covered above you would like to tell us?")
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

    # Decision maker fields
    decision_maker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='grant_decisions',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text=_("User who made the final decision")
    )
    decision_notes = models.TextField(
        blank=True,
        help_text=_("Final decision notes from decision maker")
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        permissions = (
            ("can_review_grants", "Can review grant applications"),
            ("can_make_grant_decisions", "Can make final grant decisions"),
        )

    def __str__(self):
        return f"Grant Application - {self.user.username}"

    def get_absolute_url(self):
        return reverse('grants:application_detail', kwargs={'pk': self.pk})

    @property
    def travel_from(self):
        """Combined display of city and country"""
        if self.travel_from_city and self.travel_from_country:
            return f"{self.travel_from_city}, {self.travel_from_country.name}"
        elif self.travel_from_country:
            return self.travel_from_country.name
        elif self.travel_from_city:
            return self.travel_from_city
        return ""

    @property
    def is_pending(self):
        return self.status in ['submitted', 'under_review']

    @property
    def can_edit(self):
        return self.status == 'submitted'

    @property
    def average_score(self):
        """Calculate average score from all reviews"""
        reviews = self.reviews.all()
        if reviews:
            return sum(review.score for review in reviews) / len(reviews)
        return None

    @property
    def review_count(self):
        """Get number of reviews"""
        return self.reviews.count()

    @property
    def suggested_amount_average(self):
        """Calculate average suggested amount from reviews"""
        reviews = self.reviews.filter(suggested_amount__isnull=False)
        if reviews:
            return sum(review.suggested_amount for review in reviews) / len(reviews)
        return None

    def save(self, *args, **kwargs):
        # Check if status has changed
        if self.pk:
            old_status = GrantApplication.objects.get(pk=self.pk).status
            status_changed = old_status != self.status
        else:
            status_changed = True
            old_status = None

        super().save(*args, **kwargs)

        # Send email notification if status changed
        if status_changed:
            self.send_status_notification(old_status)

    def send_status_notification(self, old_status):
        """Send email notification about status change."""
        subject = f'Grant Application Status Update - {self.get_status_display()}'
        
        context = {
            'application': self,
            'old_status': old_status,
            'user': self.user,
        }
        
        if self.status == 'under_review':
            template = 'grants/emails/under_review.html'
        elif self.status == 'approved':
            template = 'grants/emails/approved.html'
        elif self.status == 'rejected':
            template = 'grants/emails/rejected.html'
        else:
            template = 'grants/emails/status_update.html'

        html_message = render_to_string(template, context)
        plain_message = render_to_string(template.replace('.html', '.txt'), context)

        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.user.email],
            fail_silently=False,
        )

    def notify_reviewers(self):
        """Notify reviewers about new application."""
        subject = 'New Grant Application Submitted'
        context = {
            'application': self,
        }
        
        html_message = render_to_string('grants/emails/new_application_reviewer.html', context)
        plain_message = render_to_string('grants/emails/new_application_reviewer.txt', context)

        # Get all users with review permission
        from django.contrib.auth import get_user_model
        User = get_user_model()
        reviewers = User.objects.filter(
            groups__permissions__codename='can_review_grants'
        ).distinct()

        for reviewer in reviewers:
            send_mail(
                subject=subject,
                message=plain_message,    
                html_message=html_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[reviewer.email],
                fail_silently=True,
            )


class GrantReview(models.Model):
    """Individual reviewer scores and feedback"""
    application = models.ForeignKey(
        GrantApplication,
        related_name='reviews',
        on_delete=models.CASCADE
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='grant_reviews',
        on_delete=models.CASCADE
    )
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text=_("Score from 1 to 10")
    )
    notes = models.TextField(
        blank=True,
        help_text=_("Reviewer notes and feedback")
    )
    suggested_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Suggested grant amount in USD")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('application', 'reviewer')
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.reviewer.username} for {self.application.user.username} - Score: {self.score}"
