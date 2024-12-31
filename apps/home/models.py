from django.db import models
from django.core.validators import EmailValidator

class LandingPage(models.Model):
    """
    Model to store information about landing pages.
    """
    title = models.CharField(max_length=255, help_text="Title of the landing page")
    content = models.TextField(help_text="HTML content of the landing page")
    capture_data = models.BooleanField(default=False, help_text="Whether to capture form submissions")
    redirect_url = models.URLField(blank=True, null=True, help_text="Optional URL to redirect users after form submission")
    collect_emails = models.BooleanField(default=False, help_text="Enable email collection from the landing page")
    geolocation_tracking = models.BooleanField(default=False, help_text="Enable geolocation tracking of visitors")
    credential_harvesting = models.BooleanField(default=False, help_text="Enable credential harvesting from the landing page")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the page was created")
    updated_at = models.DateTimeField(auto_now=True, help_text="Timestamp when the page was last updated")

    class Meta:
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['title']),
        ]

    def __str__(self):
        return self.title


class CapturedData(models.Model):
    """
    Model to store data captured from form submissions on landing pages.
    """
    landing_page = models.ForeignKey(LandingPage, on_delete=models.CASCADE, related_name="captured_data", help_text="The landing page associated with this captured data")
    submitted_data = models.JSONField(help_text="Captured form submission data")
    submitted_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp of form submission")

    class Meta:
        indexes = [
            models.Index(fields=['submitted_at']),
            models.Index(fields=['landing_page']),
        ]

    def __str__(self):
        return f"Data from {self.landing_page.title} at {self.submitted_at}"


class VisitorAnalytics(models.Model):
    """
    Model to track visitor analytics for a landing page.
    """
    landing_page = models.ForeignKey(LandingPage, on_delete=models.CASCADE, related_name="visitor_analytics", help_text="The landing page associated with this visitor data")
    ip_address = models.GenericIPAddressField(help_text="IP address of the visitor")
    geolocation_data = models.JSONField(blank=True, null=True, help_text="Geolocation data of the visitor")
    visit_time = models.DateTimeField(auto_now_add=True, help_text="Timestamp of the visit")

    class Meta:
        indexes = [
            models.Index(fields=['visit_time']),
            models.Index(fields=['landing_page']),
        ]

    def __str__(self):
        return f"Visit to {self.landing_page.title} from {self.ip_address} at {self.visit_time}"


# Added Group and User models for your project

class Group(models.Model):
    """
    Model to store user groups.
    """
    name = models.CharField(max_length=255, unique=True, help_text="Name of the group")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the group was created")
    updated_at = models.DateTimeField(auto_now=True, help_text="Timestamp when the group was last updated")

    class Meta:
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return self.name


class User(models.Model):
    """
    Model to store information about users.
    """
    first_name = models.CharField(max_length=255, help_text="User's first name")
    last_name = models.CharField(max_length=255, help_text="User's last name")
    email = models.EmailField(unique=True, validators=[EmailValidator()], help_text="User's email address")
    position = models.CharField(max_length=255, blank=True, null=True, help_text="User's job position")
    group = models.ForeignKey(Group, related_name="users", on_delete=models.CASCADE, help_text="Group to which the user belongs")
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the user was created")
    updated_at = models.DateTimeField(auto_now=True, help_text="Timestamp when the user was last updated")

    class Meta:
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['group']),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

# Create your models here.

class EmailTemplate(models.Model):
    name = models.CharField(max_length=255)
    envelope_sender = models.EmailField()
    subject = models.CharField(max_length=255, blank=True, null=True)  # Allow null and blank
    use_tracker = models.BooleanField(default=False)
    text_content = models.TextField()
    html_content = models.TextField(blank=True, null=True)  # Allow null and blank

    def __str__(self):
        return self.name

