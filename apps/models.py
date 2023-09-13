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


class Cabang(models.Model):
    nama = models.CharField(max_length=50)
    alamat = models.CharField(max_length=150)
    kota = models.CharField(max_length=50)
    kecamatan = models.CharField(max_length=50)
    telp = PhoneNumberField(unique=False)
    manager = models.CharField(max_length=50)
    rekening_1 = models.CharField(max_length=50)
    atas_nama_1 = models.CharField(max_length=50)
    bank_1 = models.CharField(max_length=50)
    rekening_2 = models.CharField(max_length=50)
    atas_nama_2 = models.CharField(max_length=50)
    bank_2 = models.CharField(max_length=50)


class Paket(models.Model):
    nama = models.CharField(max_length=50)


class KategoriItem(models.Model):
    nama = models.CharField(max_length=50)


class Item(models.Model):
    nama = models.CharField(max_length=50)
    kategori = models.ForeignKey(
        KategoriItem, on_delete=models.CASCADE, related_name='item_kategori')
