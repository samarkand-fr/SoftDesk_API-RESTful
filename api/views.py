from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Project, Contributor, Issue, Comment
from .serializers import ProjectSerializer, ContributorSerializer, IssueSerializer, CommentSerializer
from .permissions import IsProjectContributor, IsAuthorOrReadOnly, IsProjectAuthor

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectContributor, IsAuthorOrReadOnly]

    def get_queryset(self):
        """
        Un utilisateur ne peut voir que les projets sur lesquels il est contributeur.
        """
        user = self.request.user
        return Project.objects.filter(contributors__user=user)

    def perform_create(self, serializer):
        """
        L'auteur du projet est automatiquement l'utilisateur connecté.
        Celui-ci devient automatiquement contributeur de son projet.
        """
        project = serializer.save(author=self.request.user)
        Contributor.objects.create(user=self.request.user, project=project)


class ContributorViewSet(viewsets.ModelViewSet):
    serializer_class = ContributorSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectAuthor]

    def get_queryset(self):
        """
        On ne liste que les contributeurs liés aux projets dont l'utilisateur fait partie.
        """
        user = self.request.user
        queryset = Contributor.objects.filter(project__contributors__user=user).distinct()
        
        # Filtre optionnel par projet : /api/contributors/?project=1
        project_id = self.request.query_params.get('project')
        if project_id is not None:
            queryset = queryset.filter(project_id=project_id)
            
        return queryset


class IssueViewSet(viewsets.ModelViewSet):
    serializer_class = IssueSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectContributor, IsAuthorOrReadOnly]

    def get_queryset(self):
        """
        Un utilisateur ne peut voir que les issues des projets sur lesquels il est contributeur.
        """
        user = self.request.user
        queryset = Issue.objects.filter(project__contributors__user=user).distinct()
        
        project_id = self.request.query_params.get('project')
        if project_id is not None:
            queryset = queryset.filter(project_id=project_id)
            
        return queryset

    def perform_create(self, serializer):
        """
        L'auteur de l'issue est automatiquement l'utilisateur connecté.
        Vérification stricte : il faut être contributeur du projet.
        """
        project = serializer.validated_data.get('project')
        if not Contributor.objects.filter(user=self.request.user, project=project).exists():
            raise PermissionDenied("Vous devez être contributeur du projet pour créer une issue.")
        serializer.save(author=self.request.user)


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectContributor, IsAuthorOrReadOnly]
    lookup_field = 'uuid'

    def get_queryset(self):
        """
        Un utilisateur ne peut voir que les commentaires des issues des projets 
        sur lesquels il est contributeur.
        """
        user = self.request.user
        queryset = Comment.objects.filter(issue__project__contributors__user=user).distinct()
        
        issue_id = self.request.query_params.get('issue')
        if issue_id is not None:
            queryset = queryset.filter(issue_id=issue_id)
            
        return queryset

    def perform_create(self, serializer):
        """
        L'auteur du commentaire est automatiquement l'utilisateur connecté.
        Vérification stricte : il faut être contributeur du projet parent.
        """
        issue = serializer.validated_data.get('issue')
        project = issue.project
        if not Contributor.objects.filter(user=self.request.user, project=project).exists():
            raise PermissionDenied("Vous devez être contributeur du projet pour commenter.")
        serializer.save(author=self.request.user)
