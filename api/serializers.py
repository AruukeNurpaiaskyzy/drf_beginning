from rest_framework import serializers
from .models import Todo
from django.contrib.auth.models import User

class TodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Todo
        fields = ['id', 'title', 'description', 'completed', 'created_at', 'user']
        read_only_fields = ['id', 'created_at', 'user']
    class UserSerializer(serializers.ModelSerializer):
        class Meta:
            model  = User
            fields = ['id', 'username', 'email']