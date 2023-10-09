from django.db import models
from django.contrib.auth.models import User

# Base class for all feed activities
class Activity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-last_modified"]
