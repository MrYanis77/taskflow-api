from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Task, TaskLink, Attachment, Project

class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ["id", "image", "uploaded_at"]
   
class TaskLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskLink
        fields = ["id", "src", "dst", "link_type"]

class TaskSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source="owner.username")
    reporter = serializers.SlugRelatedField(slug_field="username", queryset=User.objects.all(), allow_null=True, required=False)
    children_count = serializers.IntegerField(read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Task
        fields = "__all__"
   
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["children_count"] = instance.children.count()
        return data


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = "__all__"