from django.db import models
from django.contrib.auth.models import User

class Service(models.Model):
    """
    Represents an available external service (e.g., GitHub, Gmail).
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Action(models.Model):
    """
    Represents a possible trigger from a service.
    """
    service = models.ForeignKey(Service, related_name='actions', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return f"{self.service.name}: {self.name}"

class Reaction(models.Model):
    """
    Represents a possible reaction to perform on a service.
    """
    service = models.ForeignKey(Service, related_name='reactions', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return f"{self.service.name}: {self.name}"

class Area(models.Model):
    """
    Represents a user-defined automation linking an Action to a Reaction.
    """
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    action = models.ForeignKey(Action, on_delete=models.CASCADE)
    reaction = models.ForeignKey(Reaction, on_delete=models.CASCADE)
    action_config = models.JSONField(default=dict, blank=True)
    reaction_config = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"'{self.name}' for {self.owner.username}"
