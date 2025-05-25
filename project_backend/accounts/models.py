from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    user_name = models.CharField(max_length=20)
    nickname = models.CharField(max_length=20, unique=True)  # 게시글 등에서 보여줄 표시 이름
    profile_img = models.ImageField(upload_to='images/', default='images/default_profile.png')
    age = models.IntegerField(default=0)
    gender = models.IntegerField(blank=True, null=True)
    e_mail = models.CharField(max_length=100)
    salary = models.IntegerField(default=0)

    def __str__(self):
        return self.nickname  # admin 등에서 보여질 기본 이름
