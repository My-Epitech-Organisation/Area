from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class ServiceToken(models.Model):
    """
    Stores OAuth2 tokens for a user connected to an external service.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    service_name = models.CharField(max_length=100)
    access_token = models.TextField()
    refresh_token = models.TextField(blank=True, null=True)
    expires_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s token for {self.service_name}"

    class Meta:
        unique_together = ('user', 'service_name')
