from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Custom User model extending Django's built-in AbstractUser.

    Adds GDPR-specific fields to collect user consent and verify
    the minimum age required for data processing (15 years old).

    Fields:
        age (int): The user's age. Must be 15 or older to register
            (GDPR compliance).
        can_be_contacted (bool): Whether the user consents to being contacted.
        can_data_be_shared (bool): Whether the user consents to data sharing.
    """

    # GDPR field: used to verify that the user is old enough to give consent
    age = models.PositiveIntegerField(null=True, blank=True)

    # GDPR consent field: explicit opt-in for contact by the platform
    can_be_contacted = models.BooleanField(default=False)

    # GDPR consent field: explicit opt-in for data sharing with third parties
    can_data_be_shared = models.BooleanField(default=False)
