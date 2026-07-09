from rest_framework import serializers
from .models import Project, Contributor, Issue, Comment


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer for the Project model.

    Converts Project instances to/from JSON for the API.
    The 'author' and 'created_time' fields are read-only because they are
    automatically set server-side (author = logged-in user, time = now).
    """

    class Meta:
        model = Project
        fields = ["id", "name", "description", "type", "author", "created_time"]
        # 'author' is set automatically in perform_create()
        # 'created_time' is auto-stamped by Django
        read_only_fields = ["author", "created_time"]


class ContributorSerializer(serializers.ModelSerializer):
    """
    Serializer for the Contributor model.

    Converts Contributor instances to/from JSON for the API.
    Relations (user, project) are returned as primary key IDs to keep
    the response lightweight and avoid deep nesting (Green Code).
    """

    class Meta:
        model = Contributor
        fields = ["id", "user", "project", "created_time"]
        # 'created_time' is automatically set on creation
        read_only_fields = ["created_time"]


class IssueSerializer(serializers.ModelSerializer):
    """
    Serializer for the Issue model.

    Converts Issue instances to/from JSON for the API.
    Includes custom validation to ensure the assignee (if provided)
    is already a contributor of the target project.
    """

    class Meta:
        model = Issue
        fields = [
            "id",
            "name",
            "description",
            "project",
            "author",
            "assignee",
            "priority",
            "tag",
            "status",
            "created_time",
        ]
        # 'author' is set automatically from the JWT token
        # 'created_time' is auto-stamped by Django
        read_only_fields = ["author", "created_time"]

    def validate(self, data):
        """
        Validate that the assignee is a contributor of the target project.

        This check runs on both creation and partial update (PATCH).
        On partial updates, the project may not be in the incoming data,
        so we fall back to the existing instance's project.

        Args:
            data (dict): The deserialized field values from the request.

        Returns:
            dict: The validated data if all checks pass.

        Raises:
            ValidationError: If the assignee is not a contributor of the project.
        """
        assignee = data.get("assignee")
        project = data.get("project")

        # On partial update (PATCH), 'project' may not be in the payload.
        # Fall back to the existing project from the current instance.
        if not project and self.instance:
            project = self.instance.project

        # Only validate if both assignee and project are available
        if assignee and project:
            is_contributor = Contributor.objects.filter(
                user=assignee, project=project
            ).exists()
            if not is_contributor:
                raise serializers.ValidationError(
                    {
                        "assignee": (
                            "The assigned user must be a contributor of this project."
                        )
                    }
                )

        return data


class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for the Comment model.

    Converts Comment instances to/from JSON for the API.
    The UUID is auto-generated and used as the URL lookup field.
    The 'author' is set server-side from the JWT token.
    """

    class Meta:
        model = Comment
        fields = ["uuid", "description", "issue", "author", "created_time"]
        # 'uuid' is auto-generated; 'author' is set in perform_create()
        # 'created_time' is auto-stamped by Django
        read_only_fields = ["uuid", "author", "created_time"]
