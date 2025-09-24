from django.db import models


class AppUser(models.Model):
	email = models.EmailField(unique=True)
	name = models.CharField(max_length=255)
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	def __str__(self):
		return f"{self.name} <{self.email}>"
