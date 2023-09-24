import os
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    is_active = models.BooleanField(default=True)
    user_id = models.CharField(max_length=5, unique=True)
    
    def save(self, *args, **kwargs):
        self.user_id = self.user_id.upper()
        super(User, self).save(*args, **kwargs)