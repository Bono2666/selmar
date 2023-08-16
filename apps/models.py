import os
from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField


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
    role = models.CharField(
        max_length=20, choices=Role.choices, default=base_role)


class Setup(models.Model):
    logo = models.ImageField(upload_to='setup/')
    alamat = models.CharField(max_length=100)
    kota = models.CharField(max_length=50)
    kecamatan = models.CharField(max_length=50)
    slogan = models.CharField(max_length=50)
    telp = PhoneNumberField(unique=False)
    website = models.CharField(max_length=50)
    note = models.CharField(max_length=50)
    signature = models.ImageField(upload_to='setup/')
    signature_name = models.CharField(max_length=50)
    signature_title = models.CharField(max_length=50)
    waktu_pengiriman = models.CharField(max_length=50)
    waktu_masakan_siap = models.CharField(max_length=50)
    question_1 = models.CharField(max_length=100)
    question_2 = models.CharField(max_length=100)
    question_3 = models.CharField(max_length=100)
