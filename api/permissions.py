from rest_framework import permissions
from .models import Contributor, Project


class IsProjectContributor(permissions.BasePermission):
    """
    Object-level permission that grants access only to project contributors.

    This permission is applied to Project, Issue, and Comment resources.
    It resolves the parent project from the object being accessed and then
    checks whether the requesting user has a Contributor record for that project.

    - has_permission: Ensures the user is authenticated at the view level.
    - has_object_permission: Ensures the user is a contributor of the object's project.
    """

    def has_permission(self, request, view):
        """
        Allow access only to authenticated users (view-level check).

        Args:
            request: The incoming HTTP request.
            view: The view being accessed.

        Returns:
            bool: True if the user is authenticated, False otherwise.
        """
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        """
        Allow access only if the user is a contributor of the object's project.

        Resolves the project from the object:
        - If the object IS a Project, use it directly.
        - If the object HAS a 'project' attribute (e.g. Issue), use that.
        - If the object HAS an 'issue' attribute (e.g. Comment), traverse to project.

        Args:
            request: The incoming HTTP request.
            view: The view being accessed.
            obj: The model instance being accessed (Project, Issue, or Comment).

        Returns:
            bool: True if the user is a contributor of the resolved project.
        """
        # Direct Project access
        if isinstance(obj, Project):
            project = obj
        # Issue has a direct ForeignKey to Project
        elif hasattr(obj, "project"):
            project = obj.project
        # Comment links to Issue which links to Project
        elif hasattr(obj, "issue"):
            project = obj.issue.project
        else:
            # Unknown resource type — deny access
            return False

        # Check if the requesting user has a Contributor record for this project
        return Contributor.objects.filter(user=request.user, project=project).exists()


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Object-level permission that enforces author-only write access.

    All authenticated users (contributors) may perform safe (read-only) requests
    such as GET, HEAD, and OPTIONS. However, only the author of a resource
    (Project, Issue, or Comment) may modify or delete it.

    This permission is combined with IsProjectContributor in the views.
    """

    def has_object_permission(self, request, view, obj):
        """
        Allow read access to everyone; restrict write access to the author.

        Args:
            request: The incoming HTTP request.
            view: The view being accessed.
            obj: The model instance being accessed.

        Returns:
            bool: True if the request is read-only OR the user is the resource author.
        """
        # SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS') — always allowed for contributors
        if request.method in permissions.SAFE_METHODS:
            return True

        # For write operations (POST, PUT, PATCH, DELETE), check authorship
        if hasattr(obj, "author"):
            return obj.author == request.user

        # If the object has no 'author' field, deny write access by default
        return False


class IsProjectAuthor(permissions.BasePermission):
    """
    Object-level permission that restricts contributor management to the project author.

    Only the author of a project can add or remove contributors.
    This permission is applied exclusively to the ContributorViewSet.

    - has_permission: Ensures the user is authenticated at the view level.
    - has_object_permission: Ensures the requesting user is the project's author.
    """

    def has_permission(self, request, view):
        """
        Allow access only to authenticated users (view-level check).

        Args:
            request: The incoming HTTP request.
            view: The view being accessed.

        Returns:
            bool: True if the user is authenticated, False otherwise.
        """
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        """
        Allow access only if the requesting user is the author of the project.

        Args:
            request: The incoming HTTP request.
            view: The view being accessed.
            obj: The Contributor instance being accessed.

        Returns:
            bool: True if the user is the author of the associated project.
        """
        # Contributor objects have a 'project' FK with an 'author' FK
        if hasattr(obj, "project"):
            return obj.project.author == request.user
        return False
