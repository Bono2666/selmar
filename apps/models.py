from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from crum import get_current_user


class User(AbstractUser):
    is_active = models.BooleanField(default=True)
    user_id = models.CharField(max_length=5, primary_key=True)
    position = models.ForeignKey('Position', on_delete=models.CASCADE, null=True)
    entry_date = models.DateTimeField(null=True)
    entry_by = models.CharField(max_length=50, null=True)
    update_date = models.DateTimeField(null=True)
    update_by = models.CharField(max_length=50, null=True)

    def save(self, *args, **kwargs):
        self.user_id = self.user_id.upper()
        if not self.entry_date:
            self.entry_date = timezone.now()
            self.entry_by = get_current_user().username
        self.update_date = timezone.now()
        self.update_by = get_current_user().username
        super(User, self).save(*args, **kwargs)


class Distributor(models.Model):
    distributor_id = models.CharField(max_length=5, primary_key=True)
    distributor_name = models.CharField(max_length=50)
    entry_date = models.DateTimeField(null=True)
    entry_by = models.CharField(max_length=50, null=True)
    update_date = models.DateTimeField(null=True)
    update_by = models.CharField(max_length=50, null=True)

    def save(self, *args, **kwargs):
        self.distributor_id = self.distributor_id.upper()
        if not self.entry_date:
            self.entry_date = timezone.now()
            self.entry_by = get_current_user().username
        self.update_date = timezone.now()
        self.update_by = get_current_user().username
        super(Distributor, self).save(*args, **kwargs)

    def __str__(self):
        return self.distributor_name
    

class AreaSales(models.Model):
    area_id = models.CharField(max_length=5, primary_key=True)
    area_name = models.CharField(max_length=50)
    manager = models.CharField(max_length=50)
    entry_date = models.DateTimeField(null=True)
    entry_by = models.CharField(max_length=50, null=True)
    update_date = models.DateTimeField(null=True)
    update_by = models.CharField(max_length=50, null=True)

    def save(self, *args, **kwargs):
        self.area_id = self.area_id.upper()
        if not self.entry_date:
            self.entry_date = timezone.now()
            self.entry_by = get_current_user().username
        self.update_date = timezone.now()
        self.update_by = get_current_user().username
        super(AreaSales, self).save(*args, **kwargs)

    def __str__(self):
        return self.area_name
    
    def get_area_sales_children(self):
        return self.areasalesdetail_set.all()
    

class AreaSalesDetail(models.Model):
    area = models.ForeignKey(AreaSales, on_delete=models.CASCADE)
    distributor = models.ForeignKey(Distributor, on_delete=models.CASCADE)
    entry_date = models.DateTimeField(null=True)
    entry_by = models.CharField(max_length=50, null=True)
    update_date = models.DateTimeField(null=True)
    update_by = models.CharField(max_length=50, null=True)

    def save(self, *args, **kwargs):
        if not self.entry_date:
            self.entry_date = timezone.now()
            self.entry_by = get_current_user().username
        self.update_date = timezone.now()
        self.update_by = get_current_user().username
        super(AreaSalesDetail, self).save(*args, **kwargs)
        
    def __str__(self):
        return self.distributor_name
    

class Position(models.Model):
    position_id = models.CharField(max_length=5, primary_key=True)
    position_name = models.CharField(max_length=50)
    entry_date = models.DateTimeField(null=True)
    entry_by = models.CharField(max_length=50, null=True)
    update_date = models.DateTimeField(null=True)
    update_by = models.CharField(max_length=50, null=True)


    def save(self, *args, **kwargs):
        self.position_id = self.position_id.upper()
        if not self.entry_date:
            self.entry_date = timezone.now()
            self.entry_by = get_current_user().username
        self.update_date = timezone.now()
        self.update_by = get_current_user().username
        super(Position, self).save(*args, **kwargs)

    def __str__(self):
        return self.position_name
    