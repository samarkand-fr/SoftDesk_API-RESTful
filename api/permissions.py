from rest_framework import permissions
from .models import Contributor, Project

class IsProjectContributor(permissions.BasePermission):
    """
    Permission d'objet personnalisée : autorise l'accès uniquement si l'utilisateur
    est un contributeur du projet.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

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

class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Permission d'objet personnalisée : seul l'auteur d'une ressource (Project, Issue, Comment) 
    peut la modifier ou la supprimer.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if hasattr(obj, 'author'):
            return obj.author == request.user
            
        return False

class IsProjectAuthor(permissions.BasePermission):
    """
    Permission d'objet personnalisée : seul l'auteur du projet peut gérer les contributeurs.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'project'):
            return obj.project.author == request.user
        return False
