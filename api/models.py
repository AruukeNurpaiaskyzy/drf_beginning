from django.db import models

# Create your models here.
from django.contrib.auth.models import User

class Todo(models.Model):
    title = models.CharField(max_length =200)
    description = models.TextField(blank = True)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='todos')

    def __str__ (self):
        return self.title
    