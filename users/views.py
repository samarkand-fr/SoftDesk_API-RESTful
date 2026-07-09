from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model
from .serializers import UserSerializer

# Use the custom User model defined in settings.AUTH_USER_MODEL
User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing User accounts.

    Provides full CRUD operations for user management.
    Registration (POST) is open to everyone (no authentication required),
    while all other operations (read, update, delete) require a valid JWT token.

    This design allows new users to register freely while protecting
    existing account data from unauthorized access.

    GDPR note:
        - Deleting a user (DELETE) triggers a CASCADE on all their related
          data (projects, issues, comments), ensuring the right to be forgotten.
        - The password is never returned in responses (write-only in the serializer).
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        """
        Dynamically assign permissions based on the requested action.

        - 'create' (POST /users/): Open to everyone — this is the registration endpoint.
        - All other actions (list, retrieve, update, destroy): Require authentication.

        Returns:
            list: A list of instantiated permission objects for the current action.
        """
        if self.action == "create":
            # Registration is public — no token required
            permission_classes = [AllowAny]
        else:
            # All other actions require a valid JWT token
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]
