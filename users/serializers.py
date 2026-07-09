from rest_framework import serializers
from django.contrib.auth import get_user_model

# Use the custom User model defined in AUTH_USER_MODEL (users.User)
User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for the custom User model.

    Handles user registration (create) and profile updates (update).
    The password field is write-only for security: it will never be
    returned in API responses.

    GDPR compliance is enforced via the validate_age() method,
    which ensures users are at least 15 years old before registering.
    """

    class Meta:
        model = User
        fields = (
            "id",
            "username",
            "password",
            "age",
            "can_be_contacted",
            "can_data_be_shared",
        )
        extra_kwargs = {
            # Password is write-only: never exposed in GET responses
            "password": {"write_only": True}
        }

    def validate_age(self, value):
        """
        Validate that the user's age meets the GDPR minimum consent age.

        Per GDPR regulations applied in this project, a user must be at
        least 15 years old to register and provide personal data consent.

        Args:
            value (int): The age value provided by the user during registration.

        Returns:
            int: The validated age if it meets the minimum requirement.

        Raises:
            ValidationError: If the provided age is below 15.
        """
        if value is not None and value < 15:
            raise serializers.ValidationError(
                "You must be at least 15 years old to register."
            )
        return value

    def create(self, validated_data):
        """
        Create and return a new User instance with a hashed password.

        Uses Django's create_user() method instead of create() to ensure
        the password is properly hashed before being stored in the database.

        Args:
            validated_data (dict): The validated field values from the request.

        Returns:
            User: The newly created user instance.
        """
        # create_user() handles password hashing automatically
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        """
        Update and return an existing User instance.

        If a new password is provided, it is extracted and set using
        Django's set_password() method to ensure it is properly hashed.
        All other fields are updated using the default ModelSerializer logic.

        Args:
            instance (User): The existing User instance to update.
            validated_data (dict): The validated field values from the request.

        Returns:
            User: The updated user instance.
        """
        if "password" in validated_data:
            # Pop the password from the data and hash it before saving
            password = validated_data.pop("password")
            instance.set_password(password)

        # Delegate the remaining fields update to the parent class
        return super().update(instance, validated_data)
