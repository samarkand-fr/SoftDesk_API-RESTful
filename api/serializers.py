from rest_framework import serializers
from .models import Project, Contributor, Issue, Comment

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'description', 'type', 'author', 'created_time']
        read_only_fields = ['author', 'created_time']

class ContributorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contributor
        fields = ['id', 'user', 'project', 'created_time']
        read_only_fields = ['created_time']

class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issue
        fields = ['id', 'name', 'description', 'project', 'author', 'assignee', 'priority', 'tag', 'status', 'created_time']
        read_only_fields = ['author', 'created_time']

    def validate(self, data):
        """
        Vérifier que l'assigné est bien un contributeur du projet concerné.
        """
        assignee = data.get('assignee')
        project = data.get('project')
        
        # En cas de mise à jour partielle, project peut ne pas être dans les data, on le récupère de l'instance
        if not project and self.instance:
            project = self.instance.project
            
        if assignee and project:
            if not Contributor.objects.filter(user=assignee, project=project).exists():
                raise serializers.ValidationError({"assignee": "L'utilisateur assigné doit être un contributeur de ce projet."})
                
        return data

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['uuid', 'description', 'issue', 'author', 'created_time']
        read_only_fields = ['uuid', 'author', 'created_time']
