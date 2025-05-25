from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    nickname = models.CharField(max_length=50, unique=True)
    age = models.IntegerField(null=True, blank=True)
    salary = models.IntegerField(null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)

    def __str__(self):
        return self.username
