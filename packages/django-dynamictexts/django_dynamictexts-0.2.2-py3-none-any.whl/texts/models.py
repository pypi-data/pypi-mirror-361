from django.db import models

# Create your models here.

class DynamicText(models.Model):
    key = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    content = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.key
