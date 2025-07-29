from django.db import models

# Create your models here.

class DynamicText(models.Model):
    key = models.CharField(max_length=100, unique=True)
    title = models.CharField(max_length=255)
    content = models.TextField()

    def __str__(self):
        return self.key
