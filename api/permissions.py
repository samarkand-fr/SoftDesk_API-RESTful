from rest_framework import permissions
from .models import Contributor, Project

class IsProjectContributor(permissions.BasePermission):
    """
    Permission d'objet personnalisée : autorise l'accès uniquement si l'utilisateur
    est un contributeur du projet.
    """
    def has_object_permission(self, request, view, obj):
        # Si c'est un Project
        if isinstance(obj, Project):
            project = obj
        # Si c'est une autre ressource liée à un projet (ex: Issue, Comment)
        elif hasattr(obj, 'project'):
            project = obj.project
        else:
            return False
            
        return Contributor.objects.filter(user=request.user, project=project).exists()

class IsProjectAuthorOrReadOnly(permissions.BasePermission):
    """
    Permission d'objet personnalisée : seul l'auteur d'un projet peut le modifier/supprimer.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if isinstance(obj, Project):
            return obj.author == request.user
            
        return False
