from rest_framework import viewsets, permissions
from .models import Project, Contributor
from .serializers import ProjectSerializer, ContributorSerializer
from .permissions import IsProjectContributor, IsProjectAuthorOrReadOnly

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectContributor, IsProjectAuthorOrReadOnly]

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
    permission_classes = [permissions.IsAuthenticated]

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
