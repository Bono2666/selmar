from django.contrib.auth.models import AbstractUser
from django.db import models


class Hero(models.Model):
    image = models.ImageField(upload_to='hero/')
    title = models.CharField(max_length=50)


class User(AbstractUser):
    is_active = models.BooleanField(default=True)

    class Role(models.TextChoices):
        ADMIN = "Admin", 'Admin'
        CS = "Customer Service", 'Customer Service'
        SUPERVISOR = "Supervisor", 'Supervisor'

    base_role = Role.CS
    role = models.CharField(max_length=20, choices=Role.choices, default=base_role)
