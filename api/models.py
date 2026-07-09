import uuid
from django.db import models
from django.conf import settings


class Project(models.Model):
    """
    Represents a software project in the SoftDesk application.

    A project is the top-level resource. It is created by a user (the author),
    who automatically becomes its first contributor. Only contributors can access
    a project and its related issues and comments.

    Fields:
        name (str): The display name of the project.
        description (str): A detailed description of the project.
        type (str): The technology type (back-end, front-end, iOS, Android).
        author (User): The user who created the project (FK, CASCADE on delete).
        created_time (datetime): Auto-set timestamp when the project is created.
    """

    # Allowed project type choices
    TYPE_CHOICES = [
        ("back-end", "Back-end"),
        ("front-end", "Front-end"),
        ("iOS", "iOS"),
        ("Android", "Android"),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField()

    # The type of project, restricted to the defined choices above
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)

    # The user who created the project. Deleting a user cascades to their projects.
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="authored_projects",
    )

    # Automatically set to the current datetime when the object is first created
    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return the project name as its string representation."""
        return self.name


class Contributor(models.Model):
    """
    Intermediate model linking a User to a Project.

    This join table defines the contributor relationship. Only users listed
    here can access the project, its issues, and its comments.
    A unique constraint prevents the same user from being added twice.

    Fields:
        user (User): The contributing user (FK, CASCADE on delete).
        project (Project): The project being contributed to (FK, CASCADE on delete).
        created_time (datetime): Auto-set timestamp when the contribution is recorded.
    """

    # The user who is a contributor on this project
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="contributions"
    )

    # The project this user is contributing to
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="contributors"
    )

    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Prevent a user from being added as a contributor more than once per project
        unique_together = ("user", "project")

    def __str__(self):
        """Return a readable string showing the user-project link."""
        return f"{self.user.username} -> {self.project.name}"


class Issue(models.Model):
    """
    Represents a task, bug report, or feature request within a project.

    Issues can only be created by contributors of the parent project.
    They can be assigned to other contributors. Only the author of an issue
    can update or delete it; all contributors can read it.

    Fields:
        name (str): A short title for the issue.
        description (str): A detailed description of the issue.
        project (Project): The parent project (FK, CASCADE on delete).
        author (User): The user who created the issue (FK, CASCADE on delete).
        assignee (User): An optional contributor assigned to resolve the issue.
        priority (str): Importance level — LOW, MEDIUM, or HIGH.
        tag (str): Nature of the issue — BUG, FEATURE, or TASK.
        status (str): Current progress — To Do, In Progress, or Finished.
        created_time (datetime): Auto-set timestamp at creation.
    """

    # Priority levels for the issue
    PRIORITY_CHOICES = [
        ("LOW", "Low"),
        ("MEDIUM", "Medium"),
        ("HIGH", "High"),
    ]

    # Tag / category of the issue
    TAG_CHOICES = [
        ("BUG", "Bug"),
        ("FEATURE", "Feature"),
        ("TASK", "Task"),
    ]

    # Workflow status of the issue
    STATUS_CHOICES = [
        ("To Do", "To Do"),
        ("In Progress", "In Progress"),
        ("Finished", "Finished"),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField()

    # Parent project — deleting a project removes all its issues
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="issues"
    )

    # User who created the issue — deleting a user removes their issues
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="authored_issues",
    )

    # Optional assignee — must be a contributor of the project
    # SET_NULL so the issue is not deleted if the assignee leaves
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_issues",
    )

    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    tag = models.CharField(max_length=20, choices=TAG_CHOICES)

    # Default status when an issue is created is "To Do"
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="To Do")

    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return the issue name as its string representation."""
        return self.name


class Comment(models.Model):
    """
    Represents a comment posted on a specific issue.

    Comments are visible to all contributors of the parent project.
    Only the comment's author can update or delete it.
    Each comment is uniquely identified by a UUID (used as the URL lookup field).

    Fields:
        uuid (UUID): Auto-generated unique identifier, used in URLs.
        description (str): The text content of the comment.
        issue (Issue): The issue this comment is attached to (FK, CASCADE on delete).
        author (User): The user who wrote the comment (FK, CASCADE on delete).
        created_time (datetime): Auto-set timestamp at creation.
    """

    # UUID is used instead of a plain integer ID for better security and uniqueness
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    description = models.TextField()

    # Parent issue — deleting an issue removes all its comments
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name="comments")

    # Author — deleting a user removes their comments (GDPR: right to be forgotten)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="authored_comments",
    )

    created_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return a readable string showing the comment UUID and its author."""
        return f"Comment {self.uuid} by {self.author.username}"
