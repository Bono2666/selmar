from collections.abc import Iterable
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from crum import get_current_user
from decimal import Decimal
from re import sub


class User(AbstractUser):
    is_active = models.BooleanField(default=True)
    user_id = models.CharField(max_length=50, primary_key=True)
    username = models.CharField(max_length=50)
    position = models.ForeignKey(
        'Position', on_delete=models.CASCADE, null=True)
    entry_date = models.DateTimeField(null=True)
    entry_by = models.CharField(max_length=50, null=True)
    update_date = models.DateTimeField(null=True)
    update_by = models.CharField(max_length=50, null=True)

    def save(self, *args, **kwargs):
        if not self.entry_date:
            self.entry_date = timezone.now()
            self.entry_by = get_current_user().user_id
        self.update_date = timezone.now()
        self.update_by = get_current_user().user_id
        super(User, self).save(*args, **kwargs)

    USERNAME_FIELD = 'user_id'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username


class Distributor(models.Model):
    distributor_id = models.CharField(max_length=50, primary_key=True)
    distributor_name = models.CharField(max_length=50)
    sap_code = models.CharField(max_length=50, null=True)
    entry_date = models.DateTimeField(null=True)
    entry_by = models.CharField(max_length=50, null=True)
    update_date = models.DateTimeField(null=True)
    update_by = models.CharField(max_length=50, null=True)

    def save(self, *args, **kwargs):
        self.distributor_id = self.distributor_id.upper()
        if not self.entry_date:
            self.entry_date = timezone.now()
            self.entry_by = get_current_user().user_id
        self.update_date = timezone.now()
        self.update_by = get_current_user().user_id
        super(Distributor, self).save(*args, **kwargs)

    def __str__(self):
        return self.distributor_name


class Channel(models.Model):
    channel_id = models.CharField(max_length=5, primary_key=True)
    channel_name = models.CharField(max_length=50)
    entry_date = models.DateTimeField(null=True)
    entry_by = models.CharField(max_length=50, null=True)
    update_date = models.DateTimeField(null=True)
    update_by = models.CharField(max_length=50, null=True)

    def save(self, *args, **kwargs):
        self.channel_id = self.channel_id.upper()
        if not self.entry_date:
            self.entry_date = timezone.now()
            self.entry_by = get_current_user().user_id
        self.update_date = timezone.now()
        self.update_by = get_current_user().user_id
        super(Channel, self).save(*args, **kwargs)

    def __str__(self):
        return self.channel_id + ' - ' + self.channel_name


class AreaSales(models.Model):
    area_id = models.CharField(max_length=50, primary_key=True)
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
            self.entry_by = get_current_user().user_id
        self.update_date = timezone.now()
        self.update_by = get_current_user().user_id
        super(AreaSales, self).save(*args, **kwargs)

    def __str__(self):
        return self.area_name

    def get_area_sales_children(self):
        return self.areasalesdetail_set.all()


class AreaChannel(models.Model):
    area_id = models.CharField(max_length=50, primary_key=True)
    entry_date = models.DateTimeField(null=True)
    entry_by = models.CharField(max_length=50, null=True)
    update_date = models.DateTimeField(null=True)
    update_by = models.CharField(max_length=50, null=True)

    def save(self, *args, **kwargs):
        if not self.entry_date:
            self.entry_date = timezone.now()
            self.entry_by = get_current_user().user_id
        self.update_date = timezone.now()
        self.update_by = get_current_user().user_id
        super(AreaChannel, self).save(*args, **kwargs)


class AreaSalesDetail(models.Model):
    area = models.ForeignKey(AreaSales, on_delete=models.CASCADE)
    distributor = models.ForeignKey(Distributor, on_delete=models.CASCADE)
    entry_date = models.DateTimeField(null=True)
    entry_by = models.CharField(max_length=50, null=True)
    update_date = models.DateTimeField(null=True)
    update_by = models.CharField(max_length=50, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['area', 'distributor'], name='unique_area_distributor')
        ]

    def save(self, *args, **kwargs):
        if not self.entry_date:
            self.entry_date = timezone.now()
            self.entry_by = get_current_user().user_id
        self.update_date = timezone.now()
        self.update_by = get_current_user().user_id
        super(AreaSalesDetail, self).save(*args, **kwargs)

    def __str__(self):
        return self.distributor_name


class AreaChannelDetail(models.Model):
    area = models.ForeignKey(AreaChannel, on_delete=models.CASCADE)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    status = models.BooleanField(default=False)
    entry_date = models.DateTimeField(null=True)
    entry_by = models.CharField(max_length=50, null=True)
    update_date = models.DateTimeField(null=True)
    update_by = models.CharField(max_length=50, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['area', 'channel'], name='unique_area_channel')
        ]

    def save(self, *args, **kwargs):
        if not self.entry_date:
            self.entry_date = timezone.now()
            self.entry_by = get_current_user().user_id
        self.update_date = timezone.now()
        self.update_by = get_current_user().user_id
        super(AreaChannelDetail, self).save(*args, **kwargs)

    def __str__(self):
        return self.area_id


class AreaUser(models.Model):
    area = models.ForeignKey(AreaSales, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    entry_date = models.DateTimeField(null=True)
    entry_by = models.CharField(max_length=50, null=True)
    update_date = models.DateTimeField(null=True)
    update_by = models.CharField(max_length=50, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['area', 'user'], name='unique_area_user')
        ]

    def save(self, *args, **kwargs):
        if not self.entry_date:
            self.entry_date = timezone.now()
            self.entry_by = get_current_user().user_id
        self.update_date = timezone.now()
        self.update_by = get_current_user().user_id
        super(AreaUser, self).save(*args, **kwargs)

    def __str__(self):
        return self.area_id


class Position(models.Model):
    position_id = models.CharField(
        max_length=3, primary_key=True, help_text='Max 3 digits Position shortname.')
    position_name = models.CharField(max_length=50)
    entry_date = models.DateTimeField(null=True)
    entry_by = models.CharField(max_length=50, null=True)
    update_date = models.DateTimeField(null=True)
    update_by = models.CharField(max_length=50, null=True)

    def save(self, *args, **kwargs):
        self.position_id = self.position_id.upper()
        if not self.entry_date:
            self.entry_date = timezone.now()
            self.entry_by = get_current_user().user_id
        self.update_date = timezone.now()
        self.update_by = get_current_user().user_id
        super(Position, self).save(*args, **kwargs)

    def __str__(self):
        return self.position_name


class Menu(models.Model):
    menu_id = models.CharField(max_length=50, primary_key=True)
    menu_name = models.CharField(max_length=50)
    menu_remark = models.CharField(max_length=200, null=True, blank=True)
    entry_date = models.DateTimeField(null=True)
    entry_by = models.CharField(max_length=50, null=True)
    update_date = models.DateTimeField(null=True)
    update_by = models.CharField(max_length=50, null=True)

    def save(self, *args, **kwargs):
        self.menu_id = self.menu_id.upper()
        if not self.entry_date:
            self.entry_date = timezone.now()
            self.entry_by = get_current_user().user_id
        self.update_date = timezone.now()
        self.update_by = get_current_user().user_id
        super(Menu, self).save(*args, **kwargs)

    def __str__(self):
        return self.menu_name


class Auth(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    add = models.BooleanField(default=False)
    edit = models.BooleanField(default=False)
    delete = models.BooleanField(default=False)
    entry_date = models.DateTimeField(null=True)
    entry_by = models.CharField(max_length=50, null=True)
    update_date = models.DateTimeField(null=True)
    update_by = models.CharField(max_length=50, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'menu'], name='unique_user_menu')
        ]

    def save(self, *args, **kwargs):
        if not self.entry_date:
            self.entry_date = timezone.now()
            self.entry_by = get_current_user().user_id
        self.update_date = timezone.now()
        self.update_by = get_current_user().user_id
        super(Auth, self).save(*args, **kwargs)

    def __str__(self):
        return self.menu.menu_name


class Budget(models.Model):
    budget_id = models.CharField(max_length=50, primary_key=True)
    budget_year = models.CharField(max_length=4)
    budget_month = models.CharField(max_length=2)
    budget_area = models.ForeignKey(AreaSales, on_delete=models.CASCADE)
    budget_distributor = models.ForeignKey(
        Distributor, on_delete=models.CASCADE)
    budget_amount = models.DecimalField(
        max_digits=10, decimal_places=2)
    budget_upping = models.DecimalField(
        max_digits=10, decimal_places=2)
    budget_total = models.DecimalField(
        max_digits=10, decimal_places=2)
    budget_status = models.CharField(max_length=15)
    entry_date = models.DateTimeField(null=True)
    entry_by = models.CharField(max_length=50, null=True)
    update_date = models.DateTimeField(null=True)
    update_by = models.CharField(max_length=50, null=True)

    def save(self, *args, **kwargs):
        if not self.budget_id:
            self.budget_id = 'UBS/' + self.budget_area.area_id + '/' + \
                self.budget_distributor.distributor_id + '/' + \
                self.budget_month + '/' + self.budget_year
        self.budget_amount = Decimal(
            sub(r'[^\d.]', '', str(self.budget_amount)))
        self.budget_upping = Decimal(
            sub(r'[^\d.]', '', str(self.budget_upping)))
        self.budget_total = self.budget_amount + self.budget_upping
        if not self.entry_date:
            self.entry_date = timezone.now()
            self.entry_by = get_current_user().user_id
        self.update_date = timezone.now()
        self.update_by = get_current_user().user_id
        super(Budget, self).save(*args, **kwargs)

    def __str__(self):
        return self.budget_id


class BudgetDetail(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
    budget_channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    budget_percent = models.DecimalField(
        max_digits=3, decimal_places=0, default=0)
    budget_amount = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    budget_upping = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    budget_total = models.DecimalField(max_digits=10, decimal_places=2)
    budget_proposed = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    budget_program = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    budget_claim = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    budget_balance = models.DecimalField(max_digits=10, decimal_places=2)
    entry_date = models.DateTimeField(null=True)
    entry_by = models.CharField(max_length=50, null=True)
    update_date = models.DateTimeField(null=True)
    update_by = models.CharField(max_length=50, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['budget', 'budget_channel'], name='unique_budget_channel')
        ]

    def save(self, *args, **kwargs):
        self.budget_total = self.budget_amount + self.budget_upping
        self.budget_balance = self.budget_total - self.budget_proposed
        if not self.entry_date:
            self.entry_date = timezone.now()
            self.entry_by = get_current_user().user_id
        self.update_date = timezone.now()
        self.update_by = get_current_user().user_id
        super(BudgetDetail, self).save(*args, **kwargs)


class UploadLog(models.Model):
    document = models.CharField(max_length=50)
    document_id = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    entry_date = models.DateTimeField(null=True)
    entry_by = models.CharField(max_length=50, null=True)
    update_date = models.DateTimeField(null=True)
    update_by = models.CharField(max_length=50, null=True)

    def save(self, *args, **kwargs):
        if not self.entry_date:
            self.entry_date = timezone.now()
            self.entry_by = get_current_user().user_id
        self.update_date = timezone.now()
        self.update_by = get_current_user().user_id
        super(UploadLog, self).save(*args, **kwargs)


class BudgetRelease(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
    budget_approval_id = models.CharField(max_length=50, null=True)
    budget_approval_name = models.CharField(max_length=50, null=True)
    budget_approval_email = models.CharField(max_length=50, null=True)
    budget_approval_position = models.CharField(max_length=50, null=True)
    budget_approval_date = models.DateTimeField(null=True)
    budget_approval_status = models.CharField(max_length=1, default='N')
    upping_note = models.CharField(max_length=200, null=True)
    percentage_note = models.CharField(max_length=200, null=True)
    return_note = models.CharField(max_length=200, null=True)
    sequence = models.IntegerField(default=0)
    entry_date = models.DateTimeField(null=True)
    entry_by = models.CharField(max_length=50, null=True)
    update_date = models.DateTimeField(null=True)
    update_by = models.CharField(max_length=50, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['budget', 'budget_approval_id'], name='unique_budget_approval')
        ]

    def save(self, *args, **kwargs):
        if not self.entry_date:
            self.entry_date = timezone.now()
            self.entry_by = get_current_user().user_id
        self.update_date = timezone.now()
        self.update_by = get_current_user().user_id
        super(BudgetRelease, self).save(*args, **kwargs)


class BudgetApproval(models.Model):
    area = models.ForeignKey(AreaSales, on_delete=models.CASCADE)
    approver = models.ForeignKey(User, on_delete=models.CASCADE)
    sequence = models.IntegerField(default=0)
    position = models.ForeignKey(Position, on_delete=models.CASCADE, null=True)
    entry_date = models.DateTimeField(null=True)
    entry_by = models.CharField(max_length=50, null=True)
    update_date = models.DateTimeField(null=True)
    update_by = models.CharField(max_length=50, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['area', 'approver'], name='unique_area_approver')
        ]

    def save(self, *args, **kwargs):
        if not self.entry_date:
            self.entry_date = timezone.now()
            self.entry_by = get_current_user().user_id
        self.update_date = timezone.now()
        self.update_by = get_current_user().user_id
        super(BudgetApproval, self).save(*args, **kwargs)

    def __str__(self):
        return self.area.area_name


class Closing(models.Model):
    document = models.CharField(max_length=50, primary_key=True)
    year_closed = models.CharField(max_length=4)
    month_closed = models.CharField(max_length=2)
    year_open = models.CharField(max_length=4)
    month_open = models.CharField(max_length=2)
    entry_date = models.DateTimeField(null=True)
    entry_by = models.CharField(max_length=50, null=True)
    update_date = models.DateTimeField(null=True)
    update_by = models.CharField(max_length=50, null=True)

    def save(self, *args, **kwargs):
        self.document = self.document.upper()
        if not self.entry_date:
            self.entry_date = timezone.now()
            self.entry_by = get_current_user().user_id
        self.update_date = timezone.now()
        self.update_by = get_current_user().user_id
        super(Closing, self).save(*args, **kwargs)


class Division(models.Model):
    division_id = models.BigAutoField(primary_key=True)
    division_name = models.CharField(max_length=50)
    entry_date = models.DateTimeField(null=True)
    entry_by = models.CharField(max_length=50, null=True)
    update_date = models.DateTimeField(null=True, blank=True)
    update_by = models.CharField(max_length=50, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.entry_date:
            self.entry_date = timezone.now()
            self.entry_by = get_current_user().user_id
        self.update_date = timezone.now()
        self.update_by = get_current_user().user_id
        super(Division, self).save(*args, **kwargs)


class Proposal(models.Model):
    proposal_id = models.CharField(max_length=50, primary_key=True)
    proposal_date = models.DateTimeField(null=True)
    type = models.CharField(max_length=1, default='B')
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
    channel = models.CharField(max_length=5)
    division = models.ForeignKey(Division, on_delete=models.CASCADE)
    program_name = models.CharField(max_length=200)
    products = models.TextField()
    area = models.CharField(max_length=50)
    period_start = models.DateTimeField(null=True)
    period_from = models.DateTimeField(null=True)
    duration = models.IntegerField(default=0)
    objectives = models.TextField()
    mechanism = models.TextField()
    remarks = models.CharField(max_length=200, null=True)
    attachment = models.CharField(max_length=200, null=True)
    total_cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    status = models.CharField(max_length=15, default='DRAFT')
    seq_number = models.IntegerField(default=0)
    entry_date = models.DateTimeField(null=True)
    entry_by = models.CharField(max_length=50, null=True)
    update_date = models.DateTimeField(null=True, blank=True)
    update_by = models.CharField(max_length=50, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.duration = (self.period_from - self.period_start).days + 1
        if not self.entry_date:
            self.entry_date = timezone.now()
            self.entry_by = get_current_user().username
        self.update_date = timezone.now()
        self.update_by = get_current_user().username
        super(Proposal, self).save(*args, **kwargs)


class IncrementalSales(models.Model):
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE)
    product = models.CharField(max_length=50)
    swop_carton = models.IntegerField(default=0)
    swop_nom = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    swp_carton = models.IntegerField(default=0)
    swp_nom = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    entry_date = models.DateTimeField(null=True)
    entry_by = models.CharField(max_length=50, null=True)
    update_date = models.DateTimeField(null=True, blank=True)
    update_by = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['proposal', 'product'], name='unique_proposal_product')
        ]

    def save(self, *args, **kwargs):
        if not self.entry_date:
            self.entry_date = timezone.now()
            self.entry_by = get_current_user().username
        self.update_date = timezone.now()
        self.update_by = get_current_user().username
        super(IncrementalSales, self).save(*args, **kwargs)


class ProjectedCost(models.Model):
    proposal = models.ForeignKey(Proposal, on_delete=models.CASCADE)
    activities = models.CharField(max_length=200)
    cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    entry_date = models.DateTimeField(null=True)
    entry_by = models.CharField(max_length=50, null=True)
    update_date = models.DateTimeField(null=True, blank=True)
    update_by = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['proposal', 'activities'], name='unique_proposal_activities')
        ]

    def save(self, *args, **kwargs):
        if not self.entry_date:
            self.entry_date = timezone.now()
            self.entry_by = get_current_user().username
        self.update_date = timezone.now()
        self.update_by = get_current_user().username
        super(ProjectedCost, self).save(*args, **kwargs)
