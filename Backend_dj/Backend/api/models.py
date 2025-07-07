from django.db import models
from django.core.validators import MinLengthValidator, EmailValidator
from django.core.exceptions import ValidationError
from django.utils import timezone

class Hospital(models.Model):
    """
    Model to represent hospital registration details with password confirmation
    """
    # Unique Hospital Identifier
    hosp_ID = models.IntegerField(
        unique=True, 
        primary_key=True,
        verbose_name="Hospital Unique ID"
    )

    # Hospital Basic Information
    hosp_name = models.CharField(
        max_length=255, 
        validators=[MinLengthValidator(2)],
        verbose_name="Hospital Name"
    )

    hosp_email = models.EmailField(
        unique=True, 
        validators=[EmailValidator()],
        verbose_name="Hospital Email"
    )

    hosp_contact_no = models.CharField(
        max_length=20, 
        validators=[MinLengthValidator(10)],
        verbose_name="Contact Number"
    )

    image_url = models.URLField(
        null=True, 
        blank=True, 
        verbose_name="Hospital Logo URL"
    )

    # Location Details
    hosp_lat = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        verbose_name="Latitude"
    )

    hosp_log = models.DecimalField(
        max_digits=9, 
        decimal_places=6, 
        verbose_name="Longitude"
    )

    hosp_address = models.TextField(
        verbose_name="Complete Address"
    )

    # Bed Capacity
    hosp_no_of_beds = models.PositiveIntegerField(
        verbose_name="Number of Beds"
    )

    # Authentication
    hosp_password = models.CharField(
        max_length=255, 
        verbose_name="Password"
    )

    # Transient field for password confirmation (not stored in database)
    _confirm_password = None

    # Timestamp Fields
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Registration Date"
    )

    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name="Last Updated"
    )

    def clean(self):
        """
        Custom validation method
        """
        # Validation for number of beds
        if self.hosp_no_of_beds <= 0:
            raise ValidationError("Number of beds must be a positive integer")
        
        # Password confirmation validation
        if self._confirm_password is not None:
            if self.hosp_password != self._confirm_password:
                raise ValidationError({
                    '_confirm_password': "Passwords do not match."
                })

    def set_confirm_password(self, confirm_password):
        """
        Method to set the confirmation password for validation
        """
        self._confirm_password = confirm_password

    def check_password(self, raw_password):
        """
        Simple password matching method
        """
        return self.hosp_password == raw_password

    def save(self, *args, **kwargs):
        """
        Validate the model before saving
        """
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.hosp_name} (ID: {self.hosp_ID})"

    class Meta:
        verbose_name = "Hospital"
        verbose_name_plural = "Hospitals"
        ordering = ['-created_at']