from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Project, Contributor, Issue, Comment
from .serializers import (
    ProjectSerializer,
    ContributorSerializer,
    IssueSerializer,
    CommentSerializer,
)
from .permissions import IsProjectContributor, IsAuthorOrReadOnly, IsProjectAuthor


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Projects.

    Provides full CRUD operations (list, create, retrieve, update, destroy).
    Access is restricted to authenticated users who are contributors of the project.
    Only the project's author can update or delete it.

    Permissions:
        - IsAuthenticated: Must be logged in (JWT token required).
        - IsProjectContributor: Must be a contributor of the project.
        - IsAuthorOrReadOnly: Only the author can write; contributors can only read.
    """

    serializer_class = ProjectSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsProjectContributor,
        IsAuthorOrReadOnly,
    ]

    def get_queryset(self):
        """
        Return only the projects where the requesting user is a contributor.

        Uses select_related('author') to avoid the N+1 query problem:
        the author is fetched in a single SQL JOIN instead of one extra
        query per project (Green Code optimization).

        Returns:
            QuerySet: Filtered and optimized Project queryset.
        """
        user = self.request.user
        # Filter projects to only those the user contributes to,
        # and join the author table in a single query to avoid N+1
        return (
            Project.objects.filter(contributors__user=user)
            .select_related("author")
            .distinct()
        )

    def perform_create(self, serializer):
        """
        Create a new Project and automatically add the creator as a contributor.

        The 'author' field is injected from the JWT token (not from the request body).
        A Contributor record is also created to ensure the author can access
        their own project immediately.

        Args:
            serializer: The validated ProjectSerializer instance ready to save.
        """
        # Save the project with the current user as the author
        project = serializer.save(author=self.request.user)

        # Automatically make the creator a contributor of their own project
        Contributor.objects.create(user=self.request.user, project=project)


class ContributorViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Contributors on a project.

    Provides full CRUD operations for contributor management.
    Only the author of a project can add or remove contributors.
    Supports optional filtering by project ID via query parameter: ?project=<id>

    Permissions:
        - IsAuthenticated: Must be logged in (JWT token required).
        - IsProjectAuthor: Only the project's author can manage contributors.
    """

    serializer_class = ContributorSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectAuthor]

    def get_queryset(self):
        """
        Return contributors from projects where the requesting user is a member.

        Uses select_related('user', 'project') to resolve both FK relations
        in a single query, avoiding N+1 issues (Green Code optimization).

        Supports optional query parameter:
            ?project=<id> — filter contributors for a specific project.

        Returns:
            QuerySet: Filtered and optimized Contributor queryset.
        """
        user = self.request.user

        # Only show contributors from projects the user is part of,
        # and join user + project tables in a single query
        queryset = (
            Contributor.objects.filter(project__contributors__user=user)
            .select_related("user", "project")
            .distinct()
        )

        # Optional query param to narrow results to a specific project
        project_id = self.request.query_params.get("project")
        if project_id is not None:
            queryset = queryset.filter(project_id=project_id)

        return queryset


class IssueViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Issues within a project.

    Provides full CRUD operations for issues.
    Only contributors of the parent project can view issues.
    Only the author of an issue can update or delete it.
    Supports optional filtering by project ID via query parameter: ?project=<id>

    Permissions:
        - IsAuthenticated: Must be logged in (JWT token required).
        - IsProjectContributor: Must be a contributor of the parent project.
        - IsAuthorOrReadOnly: Only the author can write; contributors can only read.
    """

    serializer_class = IssueSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsProjectContributor,
        IsAuthorOrReadOnly,
    ]

    def get_queryset(self):
        """
        Return only the issues from projects where the requesting user is a contributor.

        Uses select_related('project', 'author', 'assignee') to join all FK relations
        in a single SQL query, preventing N+1 database hits (Green Code optimization).

        Supports optional query parameter:
            ?project=<id> — filter issues for a specific project.

        Returns:
            QuerySet: Filtered and optimized Issue queryset.
        """
        user = self.request.user

        # Scope issues to projects the user contributes to,
        # and resolve FK relations (project, author, assignee) via a JOIN
        queryset = (
            Issue.objects.filter(project__contributors__user=user)
            .select_related("project", "author", "assignee")
            .distinct()
        )

        # Optional query param to narrow results to a specific project
        project_id = self.request.query_params.get("project")
        if project_id is not None:
            queryset = queryset.filter(project_id=project_id)

        return queryset

    def perform_create(self, serializer):
        """
        Create a new Issue and enforce contributor-only access at write time.

        The 'author' is injected from the JWT token (not from the request body).
        An explicit check ensures the requesting user is a contributor of the
        target project before saving, as a secondary security guard.

        Args:
            serializer: The validated IssueSerializer instance ready to save.

        Raises:
            PermissionDenied: If the user is not a contributor of the project.
        """
        project = serializer.validated_data.get("project")

        # Secondary guard: confirm the user is a contributor of the target project
        if not Contributor.objects.filter(
            user=self.request.user, project=project
        ).exists():
            raise PermissionDenied(
                "You must be a contributor of this project to create an issue."
            )

        # Save the issue with the current user as the author
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Comments on issues.

    Provides full CRUD operations for comments.
    Only contributors of the parent project can view comments.
    Only the author of a comment can update or delete it.
    Comments are identified by their UUID (instead of integer PK) in the URL.
    Supports optional filtering by issue ID via query parameter: ?issue=<id>

    Permissions:
        - IsAuthenticated: Must be logged in (JWT token required).
        - IsProjectContributor: Must be a contributor of the parent project.
        - IsAuthorOrReadOnly: Only the author can write; contributors can only read.
    """

    serializer_class = CommentSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        IsProjectContributor,
        IsAuthorOrReadOnly,
    ]

    # Use UUID as the URL lookup field instead of the default integer PK
    lookup_field = "uuid"

    def get_queryset(self):
        """
        Return only the comments from issues in projects where the user
        is a contributor.

        Uses select_related('issue', 'author') to resolve FK relations in a single
        SQL JOIN, preventing N+1 database hits (Green Code optimization).

        Supports optional query parameter:
            ?issue=<id> — filter comments for a specific issue.

        Returns:
            QuerySet: Filtered and optimized Comment queryset.
        """
        user = self.request.user

        # Traverse: Comment → Issue → Project → Contributor to scope access correctly
        # and resolve the FK relations (issue, author) via a JOIN
        queryset = (
            Comment.objects.filter(issue__project__contributors__user=user)
            .select_related("issue", "author")
            .distinct()
        )

        # Optional query param to narrow results to a specific issue
        issue_id = self.request.query_params.get("issue")
        if issue_id is not None:
            queryset = queryset.filter(issue_id=issue_id)

        return queryset

    def perform_create(self, serializer):
        """
        Create a new Comment and enforce contributor-only access at write time.

        The 'author' is injected from the JWT token (not from the request body).
        An explicit check ensures the requesting user is a contributor of the parent
        project before saving, as a secondary security guard.

        Args:
            serializer: The validated CommentSerializer instance ready to save.

        Raises:
            PermissionDenied: If the user is not a contributor of the project.
        """
        issue = serializer.validated_data.get("issue")

        # Traverse issue → project to find the parent project for the contributor check
        project = issue.project

        # Secondary guard: confirm the user is a contributor of the parent project
        if not Contributor.objects.filter(
            user=self.request.user, project=project
        ).exists():
            raise PermissionDenied(
                "You must be a contributor of this project to post a comment."
            )

        # Save the comment with the current user as the author
        serializer.save(author=self.request.user)
