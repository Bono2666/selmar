from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.db import connection, IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.forms.models import modelformset_factory
from apps.forms import *
from apps.mail import send_email
from apps.models import *
from authentication.decorators import role_required
from tablib import Dataset
from django.utils import timezone
import xlwt
from django.http import HttpResponse
import xlsxwriter
from django.db.models import Sum, Max, Min, Count, OuterRef, Value, IntegerField
from . import host
from reportlab.pdfgen import canvas
from django.http import FileResponse
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import landscape, A4
# from PyPDF2 import PdfMerger
from django.conf import settings
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.utils.text import Truncator
import os
from datetime import date
from django.db.models import F
from django.db.models import Prefetch
from django.db.models.functions import Length, Concat, Cast
import pandas as pd
from datetime import timedelta
from apps.notifications import *


@login_required(login_url='/login/')
def home(request):
    message = WelcomeMessage.objects.all().first()
    # with connection.cursor() as cursor:
    #     cursor.execute(
    #         "SELECT budget_id, channel FROM apps_proposal GROUP BY budget_id, channel")
    #     proposals = cursor.fetchall()

    # for proposal in proposals:
    #     budget_detail = BudgetDetail.objects.get(
    #         budget=proposal[0], budget_channel=proposal[1])
    #     sum_cost = Proposal.objects.filter(budget=proposal[0], channel=proposal[1]).exclude(status__in=['REJECTED']).aggregate(Sum('total_cost'))[
    #         'total_cost__sum'] if Proposal.objects.filter(budget=proposal[0], channel=proposal[1]).exclude(status__in=['REJECTED']).exists() else 0
    #     budget_detail.budget_proposed = sum_cost
    #     budget_detail.save()
    #     sum_balance = BudgetDetail.objects.filter(budget=proposal[0]).aggregate(Sum('budget_balance'))[
    #         'budget_balance__sum'] if BudgetDetail.objects.filter(budget=proposal[0]).exists() else 0
    #     budget = Budget.objects.get(budget_id=proposal[0])
    #     budget.budget_balance = sum_balance
    #     budget.save()

    # UPDATE 'EBU' BALANCE
    # detail = BudgetDetail.objects.filter(
    #     budget__budget_distributor_id='EBU', budget_channel_id='OP')
    # for i in detail:
    #     if int(i.budget.budget_month) > 1:
    #         i.budget_amount = balance
    #         i.budget_total = i.budget_amount + i.budget_upping + \
    #             i.budget_transfer_plus - i.budget_transfer_minus
    #         i.budget_balance = i.budget_total - i.budget_proposed + i.budget_remaining
    #         i.save()
    #         print(i.budget_balance, i.budget)

    #         budget = Budget.objects.get(budget_id=i.budget_id)
    #         budget.budget_amount = BudgetDetail.objects.filter(
    #             budget=i.budget_id).aggregate(Sum('budget_amount'))['budget_amount__sum']
    #         budget.budget_total = BudgetDetail.objects.filter(
    #             budget=i.budget_id).aggregate(Sum('budget_total'))['budget_total__sum']
    #         budget.budget_balance = BudgetDetail.objects.filter(
    #             budget=i.budget_id).aggregate(Sum('budget_balance'))['budget_balance__sum']
    #         budget.save()

    #     balance = i.budget_balance

    # UPDATE 'EBE' BALANCE
    # detail = BudgetDetail.objects.filter(
    #     budget__budget_distributor_id='EBE', budget_channel_id='GT')
    # for i in detail:
    #     if int(i.budget.budget_month) > 2:
    #         i.budget_amount = balance
    #         i.budget_total = i.budget_amount + i.budget_upping + \
    #             i.budget_transfer_plus - i.budget_transfer_minus
    #         i.budget_balance = i.budget_total - i.budget_proposed + i.budget_remaining
    #         i.save()
    #         print(i.budget_balance, i.budget)

    #         budget = Budget.objects.get(budget_id=i.budget_id)
    #         budget.budget_amount = BudgetDetail.objects.filter(
    #             budget=i.budget_id).aggregate(Sum('budget_amount'))['budget_amount__sum']
    #         budget.budget_total = BudgetDetail.objects.filter(
    #             budget=i.budget_id).aggregate(Sum('budget_total'))['budget_total__sum']
    #         budget.budget_balance = BudgetDetail.objects.filter(
    #             budget=i.budget_id).aggregate(Sum('budget_balance'))['budget_balance__sum']
    #         budget.save()

    #     balance = i.budget_balance

    context = {
        'message': message,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'index',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
    }

    # if request.user.user_id == 'abdullah':
    return render(request, 'home/index.html', context)
    # else:
    #     return render(request, 'home/under_maintain.html')


def under_maintain(request):
    return render(request, 'home/under_maintain.html')


@login_required(login_url='/login/')
@role_required(allowed_roles='USER')
def user_index(request):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT user_id, username, email, position_name FROM apps_user INNER JOIN apps_position ON apps_user.position_id = apps_position.position_id")
        users = cursor.fetchall()

    context = {
        'data': users,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'user',
        'group_segment': 'master',
        'crud': 'index',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='USER') if not request.user.is_superuser else Auth.objects.all(),
    }

    return render(request, 'home/user_index.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='USER')
def user_add(request):
    position = Position.objects.all()
    if request.POST:
        form = FormUser(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            if not settings.DEBUG:
                user = User.objects.get(user_id=form.instance.user_id)
                if user.signature:
                    my_file = user.signature
                    filename = '../../www/' + host.folder + '/apps/media/' + my_file.name
                    with open(filename, 'wb+') as temp_file:
                        for chunk in my_file.chunks():
                            temp_file.write(chunk)

            return HttpResponseRedirect(reverse('user-view', args=[form.instance.user_id, ]))
        else:
            message = form.errors
            context = {
                'form': form,
                'position': position,
                'budget_notif': budget_notification(request),
                'proposal_notif': proposal_notification(request),
                'program_notif': program_notification(request),
                'claim_notif': claim_notification(request),
                'cl_notif': cl_notification(request),
                'segment': 'user',
                'group_segment': 'master',
                'crud': 'add',
                'message': message,
                'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
                'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='USER') if not request.user.is_superuser else Auth.objects.all(),
            }
            return render(request, 'home/user_add.html', context)
    else:
        form = FormUser()
        context = {
            'form': form,
            'position': position,
            'budget_notif': budget_notification(request),
            'proposal_notif': proposal_notification(request),
            'program_notif': program_notification(request),
            'claim_notif': claim_notification(request),
            'cl_notif': cl_notification(request),
            'segment': 'user',
            'group_segment': 'master',
            'crud': 'add',
            'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
            'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='USER') if not request.user.is_superuser else Auth.objects.all(),
        }
        return render(request, 'home/user_add.html', context)


# View User
@login_required(login_url='/login/')
@role_required(allowed_roles='USER')
def user_view(request, _id):
    users = User.objects.get(user_id=_id)
    auth = Auth.objects.filter(user_id=_id)
    area = AreaUser.objects.filter(user_id=_id)
    form = FormUserView(instance=users)
    position = Position.objects.all()
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT apps_menu.menu_id, menu_name, q_auth.menu_id FROM apps_menu LEFT JOIN (SELECT * FROM apps_auth WHERE user_id = '" + str(_id) + "') AS q_auth ON apps_menu.menu_id = q_auth.menu_id WHERE q_auth.menu_id IS NULL")
        menu = cursor.fetchall()
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT apps_areasales.area_id, area_name, q_area.area_id FROM apps_areasales LEFT JOIN (SELECT * FROM apps_areauser WHERE user_id = '" + str(_id) + "') AS q_area ON apps_areasales.area_id = q_area.area_id WHERE q_area.area_id IS NULL")
        item_area = cursor.fetchall()

    if request.POST:
        check = request.POST.getlist('checks[]')
        for i in menu:
            if str(i[0]) in check:
                try:
                    auth = Auth(user_id=_id, menu_id=i[0])
                    auth.save()
                except IntegrityError:
                    continue
            else:
                Auth.objects.filter(user_id=_id, menu_id=i[0]).delete()

        return HttpResponseRedirect(reverse('user-view', args=[_id, ]))

    context = {
        'form': form,
        'formAuth': form,
        'data': users,
        'auth': auth,
        'menu': menu,
        'area': area,
        'item_area': item_area,
        'positions': position,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'user',
        'group_segment': 'master',
        'tab': 'auth',
        'crud': 'view',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='USER') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/user_view.html', context)


# View User Area
@login_required(login_url='/login/')
@role_required(allowed_roles='USER')
def user_area_view(request, _id):
    users = User.objects.get(user_id=_id)
    auth = Auth.objects.filter(user_id=_id)
    area = AreaUser.objects.filter(user_id=_id)
    form = FormUserView(instance=users)
    position = Position.objects.all()
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT apps_menu.menu_id, menu_name, q_auth.menu_id FROM apps_menu LEFT JOIN (SELECT * FROM apps_auth WHERE user_id = '" + str(_id) + "') AS q_auth ON apps_menu.menu_id = q_auth.menu_id WHERE q_auth.menu_id IS NULL")
        menu = cursor.fetchall()
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT apps_areasales.area_id, area_name, q_area.area_id FROM apps_areasales LEFT JOIN (SELECT * FROM apps_areauser WHERE user_id = '" + str(_id) + "') AS q_area ON apps_areasales.area_id = q_area.area_id WHERE q_area.area_id IS NULL")
        item_area = cursor.fetchall()

    if request.POST:
        area_check = request.POST.getlist('area[]')
        for i in item_area:
            if str(i[0]) in area_check:
                try:
                    area = AreaUser(user_id=_id, area_id=i[0])
                    area.save()
                except IntegrityError:
                    continue
            else:
                AreaUser.objects.filter(user_id=_id, area_id=i[0]).delete()

        return HttpResponseRedirect(reverse('user-area-view', args=[_id, ]))

    context = {
        'form': form,
        'formAuth': form,
        'data': users,
        'auth': auth,
        'menu': menu,
        'area': area,
        'item_area': item_area,
        'positions': position,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'user',
        'group_segment': 'master',
        'tab': 'area',
        'crud': 'view',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='USER') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/user_view.html', context)


# Update Auth
@login_required(login_url='/login/')
@role_required(allowed_roles='USER')
def auth_update(request, _id, _menu):
    auth = Auth.objects.get(user=_id, menu=_menu)

    if request.POST:
        auth.add = 1 if request.POST.get('add') else 0
        auth.edit = 1 if request.POST.get('edit') else 0
        auth.delete = 1 if request.POST.get('delete') else 0
        auth.submit = 1 if request.POST.get('submit') else 0
        auth.save()

        return HttpResponseRedirect(reverse('user-view', args=[_id, ]))

    return render(request, 'home/user_view.html')


# Delete Auth
@login_required(login_url='/login/')
@role_required(allowed_roles='USER')
def auth_delete(request, _id, _menu):
    auth = Auth.objects.filter(user=_id, menu=_menu)

    auth.delete()
    return HttpResponseRedirect(reverse('user-view', args=[_id, ]))


# Delete AreaUser
@login_required(login_url='/login/')
@role_required(allowed_roles='USER')
def area_user_delete(request, _id, _area):
    area = AreaUser.objects.filter(user=_id, area=_area)

    area.delete()
    return HttpResponseRedirect(reverse('user-area-view', args=[_id, ]))


@login_required(login_url='/login/')
@role_required(allowed_roles='USER')
def remove_signature(request, _id):
    users = User.objects.get(user_id=_id)
    users.signature = None
    users.save()
    return HttpResponseRedirect(reverse('user-view', args=[_id, ]))


# Update User
@login_required(login_url='/login/')
@role_required(allowed_roles='USER')
def user_update(request, _id):
    users = User.objects.get(user_id=_id)
    position = Position.objects.all()
    auth = Auth.objects.filter(user_id=_id)
    area = AreaUser.objects.filter(user_id=_id)

    if request.POST:
        form = FormUserUpdate(request.POST, request.FILES, instance=users)
        if form.is_valid():
            form.save()
            if not settings.DEBUG:
                if users.signature:
                    my_file = users.signature
                    filename = '../../www/' + host.folder + '/apps/media/' + my_file.name
                    with open(filename, 'wb+') as temp_file:
                        for chunk in my_file.chunks():
                            temp_file.write(chunk)
            return HttpResponseRedirect(reverse('user-view', args=[_id, ]))
    else:
        form = FormUserUpdate(instance=users)

    message = form.errors
    context = {
        'form': form,
        'data': users,
        'positions': position,
        'auth': auth,
        'area': area,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'user',
        'group_segment': 'master',
        'crud': 'update',
        'tab': 'auth',
        'message': message,
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='USER') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/user_view.html', context)


# Delete User
@login_required(login_url='/login/')
@role_required(allowed_roles='USER')
def user_delete(request, _id):
    users = User.objects.get(user_id=_id)

    users.delete()
    return HttpResponseRedirect(reverse('user-index'))


@login_required(login_url='/login/')
def change_password(request):
    if request.POST:
        form = FormChangePassword(data=request.POST, user=request.user)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return HttpResponseRedirect(reverse('home'))
    else:
        form = FormChangePassword(user=request.user)

    message = form.errors
    context = {
        'form': form,
        'data': request.user,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'crud': 'update',
        'message': message,
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
    }
    return render(request, 'home/user_change_password.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='USER')
def set_password(request, _id):
    users = User.objects.get(user_id=_id)
    if request.POST:
        form = FormSetPassword(data=request.POST, user=users)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return HttpResponseRedirect(reverse('user-view', args=[_id, ]))
    else:
        form = FormSetPassword(user=users)

    message = form.errors
    context = {
        'form': form,
        'data': users,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'user',
        'group_segment': 'master',
        'crud': 'update',
        'message': message,
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='USER') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/user_set_password.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='DISTRIBUTOR')
def distributor_index(request):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT distributor_id, distributor_name, sap_code FROM apps_distributor")
        distributors = cursor.fetchall()

    context = {
        'data': distributors,
        'segment': 'distributor',
        'group_segment': 'master',
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'crud': 'index',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='DISTRIBUTOR') if not request.user.is_superuser else Auth.objects.all(),
    }

    return render(request, 'home/distributor_index.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='DISTRIBUTOR')
def distributor_add(request):
    if request.POST:
        form = FormDistributor(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('distributor-index'))
        else:
            message = form.errors
            context = {
                'form': form,
                'segment': 'distributor',
                'group_segment': 'master',
                'budget_notif': budget_notification(request),
                'proposal_notif': proposal_notification(request),
                'program_notif': program_notification(request),
                'claim_notif': claim_notification(request),
                'cl_notif': cl_notification(request),
                'crud': 'add',
                'message': message,
                'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
                'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='DISTRIBUTOR') if not request.user.is_superuser else Auth.objects.all(),
            }
            return render(request, 'home/distributor_add.html', context)
    else:
        form = FormDistributor()
        context = {
            'form': form,
            'segment': 'distributor',
            'group_segment': 'master',
            'budget_notif': budget_notification(request),
            'proposal_notif': proposal_notification(request),
            'program_notif': program_notification(request),
            'claim_notif': claim_notification(request),
            'cl_notif': cl_notification(request),
            'crud': 'add',
            'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
            'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='DISTRIBUTOR') if not request.user.is_superuser else Auth.objects.all(),
        }
        return render(request, 'home/distributor_add.html', context)


# View Distributor
@login_required(login_url='/login/')
@role_required(allowed_roles='DISTRIBUTOR')
def distributor_view(request, _id):
    distributors = Distributor.objects.get(distributor_id=_id)
    form = FormDistributorView(instance=distributors)

    context = {
        'form': form,
        'data': distributors,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'distributor',
        'group_segment': 'master',
        'crud': 'view',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='DISTRIBUTOR') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/distributor_view.html', context)


# Update Distributor
@login_required(login_url='/login/')
@role_required(allowed_roles='DISTRIBUTOR')
def distributor_update(request, _id):
    distributors = Distributor.objects.get(distributor_id=_id)
    if request.POST:
        form = FormDistributorUpdate(
            request.POST, request.FILES, instance=distributors)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('distributor-view', args=[_id, ]))
    else:
        form = FormDistributorUpdate(instance=distributors)

    message = form.errors
    context = {
        'form': form,
        'data': distributors,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'distributor',
        'group_segment': 'master',
        'crud': 'update',
        'message': message,
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='DISTRIBUTOR') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/distributor_view.html', context)


# Delete Distributor
@login_required(login_url='/login/')
@role_required(allowed_roles='DISTRIBUTOR')
def distributor_delete(request, _id):
    distributors = Distributor.objects.get(distributor_id=_id)

    distributors.delete()
    return HttpResponseRedirect(reverse('distributor-index'))


@login_required(login_url='/login/')
@role_required(allowed_roles='AREA')
def area_sales_index(request):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT area_id, area_name, username FROM apps_areasales LEFT JOIN apps_user ON apps_areasales.manager = apps_user.user_id")
        area_sales = cursor.fetchall()

    context = {
        'data': area_sales,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'area_sales',
        'group_segment': 'master',
        'crud': 'index',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='AREA') if not request.user.is_superuser else Auth.objects.all(),
    }

    return render(request, 'home/area_sales_index.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='AREA')
def area_sales_add(request):
    AreaSalesDetailFormSet = modelformset_factory(
        AreaSalesDetail, form=FormAreaSalesDetail, extra=0, can_delete=True, can_delete_extra=True)
    distributor = Distributor.objects.all()
    manager = User.objects.filter(position_id='ASM')

    if request.POST:
        form = FormAreaSales(request.POST, request.FILES)
        formset = AreaSalesDetailFormSet(
            request.POST, queryset=AreaSalesDetail.objects.none())

        if form.is_valid():
            new = form.save(commit=False)
            new.area_id = form.cleaned_data.get('area_id').replace(' ', '')
            new.save()
            return HttpResponseRedirect(reverse('area-sales-view', args=[form.instance.area_id, ]))
        # if all([form.is_valid(), formset.is_valid()]):
        #     try:
        #         parent = form.save(commit=False)
        #         parent.save()
        #         for form in formset:
        #             if form.cleaned_data.get('distributor') is None:
        #                 if form.cleaned_data.get('DELETE'):
        #                     continue
        #                 else:
        #                     continue
        #             else:
        #                 if form.cleaned_data.get('DELETE'):
        #                     form.instance.delete()
        #                     continue

        #             child = form.save(commit=False)
        #             child.area = parent
        #             child.save()
        #         return HttpResponseRedirect(reverse('area-sales-index'))
        #     except Exception:
        #         return HttpResponseRedirect(reverse('area-sales-index'))
        else:
            message = form.errors
            context = {
                'form': form,
                'manager': manager,
                'budget_notif': budget_notification(request),
                'proposal_notif': proposal_notification(request),
                'program_notif': program_notification(request),
                'claim_notif': claim_notification(request),
                'cl_notif': cl_notification(request),
                'segment': 'area_sales',
                'group_segment': 'master',
                'crud': 'add',
                'message': message,
                'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
                'distributors': distributor,
                'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='AREA') if not request.user.is_superuser else Auth.objects.all(),
            }
            return render(request, 'home/area_sales_add.html', context)
    else:
        form = FormAreaSales()
        formset = AreaSalesDetailFormSet(
            queryset=AreaSalesDetail.objects.none())

        message = form.errors
        context = {
            'form': form,
            'manager': manager,
            'formset': formset,
            'budget_notif': budget_notification(request),
            'proposal_notif': proposal_notification(request),
            'program_notif': program_notification(request),
            'claim_notif': claim_notification(request),
            'cl_notif': cl_notification(request),
            'segment': 'area_sales',
            'group_segment': 'master',
            'crud': 'add',
            'message': message,
            'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
            'distributors': distributor,
            'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='AREA') if not request.user.is_superuser else Auth.objects.all(),
        }
        return render(request, 'home/area_sales_add.html', context)


# View Area Sales
@login_required(login_url='/login/')
@role_required(allowed_roles='AREA')
def area_sales_view(request, _id):
    area_sales = AreaSales.objects.get(area_id=_id)
    AreaSalesDetailFormSet = modelformset_factory(
        AreaSalesDetail, form=FormAreaSalesDetailView, extra=0)
    qs = area_sales.areasalesdetail_set.all()
    form = FormAreaSalesView(instance=area_sales)
    formset = AreaSalesDetailFormSet(queryset=qs)
    detail = AreaSalesDetail.objects.filter(area_id=_id)
    managers = User.objects.filter(position_id='ASM')
    # distributor = Distributor.objects.all()
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT apps_distributor.distributor_id, distributor_name, q_distributor.distributor_id FROM apps_distributor LEFT JOIN (SELECT * FROM apps_areasalesdetail WHERE area_id = '" + str(_id) + "') AS q_distributor ON apps_distributor.distributor_id = q_distributor.distributor_id WHERE q_distributor.distributor_id IS NULL")
        distributor = cursor.fetchall()
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT area_id, area_name, username FROM apps_areasales INNER JOIN apps_user ON apps_areasales.manager = apps_user.user_id WHERE area_id = '" + str(_id) + "'")
        areas = cursor.fetchall()

    if request.POST:
        check = request.POST.getlist('checks[]')
        for i in distributor:
            if str(i[0]) in check:
                try:
                    detail = AreaSalesDetail(area_id=_id, distributor_id=i[0])
                    detail.save()
                except IntegrityError:
                    continue
            else:
                AreaSalesDetail.objects.filter(
                    area_id=_id, distributor_id=i[0]).delete()
        return HttpResponseRedirect(reverse('area-sales-view', args=[_id, ]))

    context = {
        'form': form,
        'formset': formset,
        'data': area_sales,
        'areas': areas,
        'detail': detail,
        'managers': managers,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'area_sales',
        'group_segment': 'master',
        'crud': 'view',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'distributors': distributor,
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='AREA') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/area_sales_view.html', context)


# Update Area Sales
@login_required(login_url='/login/')
@role_required(allowed_roles='AREA')
def area_sales_update(request, _id):
    area_sales = AreaSales.objects.get(area_id=_id)
    AreaSalesDetailFormSet = modelformset_factory(
        AreaSalesDetail, form=FormAreaSalesDetail, extra=0, can_delete=True, can_delete_extra=True)
    qs = area_sales.areasalesdetail_set.all()
    distributor = Distributor.objects.all()
    detail = AreaSalesDetail.objects.filter(area_id=_id)
    managers = User.objects.filter(position_id='ASM')

    if request.POST:
        form = FormAreaSalesUpdate(
            request.POST, request.FILES, instance=area_sales)
        formset = AreaSalesDetailFormSet(request.POST, queryset=qs)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('area-sales-view', args=[_id, ]))
        # if all([form.is_valid(), formset.is_valid()]):
        #     try:
        #         parent = form.save(commit=False)
        #         parent.save()
        #         for form in formset:
        #             if form.cleaned_data.get('distributor') is None:
        #                 if form.cleaned_data.get('DELETE'):
        #                     continue
        #                 else:
        #                     continue
        #             else:
        #                 if form.cleaned_data.get('DELETE'):
        #                     form.instance.delete()
        #                     continue

        #             child = form.save(commit=False)
        #             child.area = parent
        #             child.save()
        #         return HttpResponseRedirect(reverse('area-sales-view', args=[_id, ]))
        #     except Exception:
        #         return HttpResponseRedirect(reverse('area-sales-view', args=[_id, ]))
    else:
        form = FormAreaSalesUpdate(instance=area_sales)
        formset = AreaSalesDetailFormSet(queryset=qs)

    message = form.errors
    context = {
        'form': form,
        'formset': formset,
        'data': area_sales,
        'detail': detail,
        'managers': managers,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'area_sales',
        'group_segment': 'master',
        'crud': 'update',
        'message': message,
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'distributors': distributor,
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='AREA') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/area_sales_view.html', context)


# Delete Area Sales
@login_required(login_url='/login/')
@role_required(allowed_roles='AREA')
def area_sales_delete(request, _id):
    area_sales = AreaSales.objects.get(area_id=_id)

    area_sales.delete()
    return HttpResponseRedirect(reverse('area-sales-index'))


@login_required(login_url='/login/')
@role_required(allowed_roles='AREA')
def area_sales_detail_delete(request, _id, _distributor):
    area_sales_detail = AreaSalesDetail.objects.get(
        area_id=_id, distributor_id=_distributor)

    area_sales_detail.delete()
    return HttpResponseRedirect(reverse('area-sales-view', args=[_id, ]))


@login_required(login_url='/login/')
@role_required(allowed_roles='AREA-CHANNEL')
def area_channel_index(request):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT apps_areachannel.area_id, apps_areasales.area_name, apps_user.username FROM apps_areachannel INNER JOIN apps_areasales ON apps_areachannel.area_id = apps_areasales.area_id INNER JOIN apps_user ON apps_areasales.manager = apps_user.user_id")
        area_channels = cursor.fetchall()

    context = {
        'data': area_channels,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'area_channel',
        'group_segment': 'master',
        'crud': 'index',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(
            user_id=request.user.user_id, menu_id='AREA-CHANNEL') if not request.user.is_superuser else Auth.objects.all(),
    }

    return render(request, 'home/area_channel_index.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='AREA-CHANNEL')
def area_channel_add(request):
    channel = Channel.objects.all()
    areas = AreaSales.objects.all()
    if request.POST:
        form = FormAreaChannel(request.POST, request.FILES)
        if form.is_valid():
            parent = form.save(commit=False)
            parent.save()
            for i in channel:
                child = AreaChannelDetail(
                    area=parent, channel=i, status=0)
                child.save()
            return HttpResponseRedirect(reverse('area-channel-view', args=[form.instance.area_id, ]))
        else:
            message = form.errors
            context = {
                'form': form,
                'areas': areas,
                'budget_notif': budget_notification(request),
                'proposal_notif': proposal_notification(request),
                'program_notif': program_notification(request),
                'claim_notif': claim_notification(request),
                'cl_notif': cl_notification(request),
                'segment': 'area_channel',
                'group_segment': 'master',
                'crud': 'add',
                'message': message,
                'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
                'btn': Auth.objects.get(
                    user_id=request.user.user_id, menu_id='AREA-CHANNEL') if not request.user.is_superuser else Auth.objects.all(),
            }
            return render(request, 'home/area_channel_add.html', context)
    else:
        form = FormAreaChannel()
        context = {
            'form': form,
            'areas': areas,
            'budget_notif': budget_notification(request),
            'proposal_notif': proposal_notification(request),
            'program_notif': program_notification(request),
            'claim_notif': claim_notification(request),
            'cl_notif': cl_notification(request),
            'segment': 'area_channel',
            'group_segment': 'master',
            'crud': 'add',
            'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
            'btn': Auth.objects.get(
                user_id=request.user.user_id, menu_id='AREA-CHANNEL') if not request.user.is_superuser else Auth.objects.all(),
        }
        return render(request, 'home/area_channel_add.html', context)


# View Area Channel
@login_required(login_url='/login/')
@role_required(allowed_roles='AREA-CHANNEL')
def area_channel_view(request, _id):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT apps_areachannel.area_id, apps_areasales.area_name, apps_user.username FROM apps_areachannel INNER JOIN apps_areasales ON apps_areachannel.area_id = apps_areasales.area_id INNER JOIN apps_user ON apps_areasales.manager = apps_user.user_id WHERE apps_areachannel.area_id = '" + str(_id) + "'")
        area_channels = cursor.fetchone()

    detail = AreaChannelDetail.objects.filter(area=_id)

    context = {
        'data': area_channels,
        'detail': detail,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'area_channel',
        'group_segment': 'master',
        'crud': 'view',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(
            user_id=request.user.user_id, menu_id='AREA-CHANNEL') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/area_channel_view.html', context)


# Delete Area Channel
@login_required(login_url='/login/')
@role_required(allowed_roles='AREA-CHANNEL')
def area_channel_delete(request, _id):
    area_channels = AreaChannel.objects.get(area_id=_id)

    area_channels.delete()
    return HttpResponseRedirect(reverse('area-channel-index'))


# Update Area Channel Detail
@login_required(login_url='/login/')
@role_required(allowed_roles='AREA-CHANNEL')
def area_channel_detail_update(request, _id, _channel):
    area_channels = AreaChannelDetail.objects.get(area=_id, channel=_channel)

    if request.POST:
        area_channels.status = 1 if request.POST.get('status') else 0
        area_channels.save()

        return HttpResponseRedirect(reverse('area-channel-view', args=[_id, ]))

    return render(request, 'home/area_channel_view.html')


@login_required(login_url='/login/')
@role_required(allowed_roles='POSITION')
def position_add(request):
    if request.POST:
        form = FormPosition(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('position-index'))
        else:
            message = form.errors
            context = {
                'form': form,
                'budget_notif': budget_notification(request),
                'proposal_notif': proposal_notification(request),
                'program_notif': program_notification(request),
                'claim_notif': claim_notification(request),
                'cl_notif': cl_notification(request),
                'segment': 'position',
                'group_segment': 'master',
                'crud': 'add',
                'message': message,
                'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
                'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='POSITION') if not request.user.is_superuser else Auth.objects.all(),
            }
            return render(request, 'home/position_add.html', context)
    else:
        form = FormPosition()
        context = {
            'form': form,
            'budget_notif': budget_notification(request),
            'proposal_notif': proposal_notification(request),
            'program_notif': program_notification(request),
            'claim_notif': claim_notification(request),
            'cl_notif': cl_notification(request),
            'segment': 'position',
            'group_segment': 'master',
            'crud': 'add',
            'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
            'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='POSITION') if not request.user.is_superuser else Auth.objects.all(),
        }
        return render(request, 'home/position_add.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='POSITION')
def position_index(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT position_id, position_name FROM apps_position")
        positions = cursor.fetchall()

    context = {
        'data': positions,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'position',
        'group_segment': 'master',
        'crud': 'index',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='POSITION') if not request.user.is_superuser else Auth.objects.all(),
    }

    return render(request, 'home/position_index.html', context)


# Update Position
@login_required(login_url='/login/')
@role_required(allowed_roles='POSITION')
def position_update(request, _id):
    positions = Position.objects.get(position_id=_id)
    if request.POST:
        form = FormPositionUpdate(
            request.POST, request.FILES, instance=positions)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('position-view', args=[_id, ]))
    else:
        form = FormPositionUpdate(instance=positions)

    message = form.errors
    context = {
        'form': form,
        'data': positions,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'position',
        'group_segment': 'master',
        'crud': 'update',
        'message': message,
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='POSITION') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/position_view.html', context)


# Delete Position
@login_required(login_url='/login/')
@role_required(allowed_roles='POSITION')
def position_delete(request, _id):
    positions = Position.objects.get(position_id=_id)

    positions.delete()
    return HttpResponseRedirect(reverse('position-index'))


@login_required(login_url='/login/')
@role_required(allowed_roles='POSITION')
def position_view(request, _id):
    positions = Position.objects.get(position_id=_id)
    form = FormPositionView(instance=positions)

    context = {
        'form': form,
        'data': positions,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'position',
        'group_segment': 'master',
        'crud': 'view',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='POSITION') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/position_view.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='MENU')
def menu_add(request):
    if request.POST:
        form = FormMenu(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('menu-index'))
        else:
            message = form.errors
            context = {
                'form': form,
                'budget_notif': budget_notification(request),
                'proposal_notif': proposal_notification(request),
                'program_notif': program_notification(request),
                'claim_notif': claim_notification(request),
                'cl_notif': cl_notification(request),
                'segment': 'menu',
                'group_segment': 'master',
                'crud': 'add',
                'message': message,
                'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
                'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='MENU') if not request.user.is_superuser else Auth.objects.all(),
            }
            return render(request, 'home/menu_add.html', context)
    else:
        form = FormMenu()
        context = {
            'form': form,
            'budget_notif': budget_notification(request),
            'proposal_notif': proposal_notification(request),
            'program_notif': program_notification(request),
            'claim_notif': claim_notification(request),
            'cl_notif': cl_notification(request),
            'segment': 'menu',
            'group_segment': 'master',
            'crud': 'add',
            'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
            'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='MENU') if not request.user.is_superuser else Auth.objects.all(),
        }
        return render(request, 'home/menu_add.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='MENU')
def menu_index(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT menu_id, menu_name, menu_remark FROM apps_menu")
        menus = cursor.fetchall()

    context = {
        'data': menus,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'menu',
        'group_segment': 'master',
        'crud': 'index',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='MENU') if not request.user.is_superuser else Auth.objects.all(),
    }

    return render(request, 'home/menu_index.html', context)


# Update Menu
@login_required(login_url='/login/')
@role_required(allowed_roles='MENU')
def menu_update(request, _id):
    menus = Menu.objects.get(menu_id=_id)
    if request.POST:
        form = FormMenuUpdate(request.POST, request.FILES, instance=menus)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('menu-view', args=[_id, ]))
    else:
        form = FormMenuUpdate(instance=menus)

    message = form.errors
    context = {
        'form': form,
        'data': menus,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'menu',
        'group_segment': 'master',
        'crud': 'update',
        'message': message,
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='MENU') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/menu_view.html', context)


# Delete Menu
@login_required(login_url='/login/')
@role_required(allowed_roles='MENU')
def menu_delete(request, _id):
    menus = Menu.objects.get(menu_id=_id)

    menus.delete()
    return HttpResponseRedirect(reverse('menu-index'))


@login_required(login_url='/login/')
@role_required(allowed_roles='MENU')
def menu_view(request, _id):
    menus = Menu.objects.get(menu_id=_id)
    form = FormMenuView(instance=menus)

    context = {
        'form': form,
        'data': menus,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'menu',
        'group_segment': 'master',
        'crud': 'view',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='MENU') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/menu_view.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='CHANNEL')
def channel_add(request):
    if request.POST:
        form = FormChannel(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('channel-index'))
        else:
            message = form.errors
            context = {
                'form': form,
                'budget_notif': budget_notification(request),
                'proposal_notif': proposal_notification(request),
                'program_notif': program_notification(request),
                'claim_notif': claim_notification(request),
                'cl_notif': cl_notification(request),
                'segment': 'channel',
                'group_segment': 'master',
                'crud': 'add',
                'message': message,
                'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
                'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='CHANNEL') if not request.user.is_superuser else Auth.objects.all(),
            }
            return render(request, 'home/channel_add.html', context)
    else:
        form = FormChannel()
        context = {
            'form': form,
            'budget_notif': budget_notification(request),
            'proposal_notif': proposal_notification(request),
            'program_notif': program_notification(request),
            'claim_notif': claim_notification(request),
            'cl_notif': cl_notification(request),
            'segment': 'channel',
            'group_segment': 'master',
            'crud': 'add',
            'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
            'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='CHANNEL') if not request.user.is_superuser else Auth.objects.all(),
        }
        return render(request, 'home/channel_add.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='CHANNEL')
def channel_index(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT channel_id, channel_name FROM apps_channel")
        channels = cursor.fetchall()

    context = {
        'data': channels,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'channel',
        'group_segment': 'master',
        'crud': 'index',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='CHANNEL') if not request.user.is_superuser else Auth.objects.all(),
    }

    return render(request, 'home/channel_index.html', context)


# Update Channel
@login_required(login_url='/login/')
@role_required(allowed_roles='CHANNEL')
def channel_update(request, _id):
    channels = Channel.objects.get(channel_id=_id)
    if request.POST:
        form = FormChannelUpdate(
            request.POST, request.FILES, instance=channels)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('channel-view', args=[_id, ]))
    else:
        form = FormChannelUpdate(instance=channels)

    message = form.errors
    context = {
        'form': form,
        'data': channels,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'channel',
        'group_segment': 'master',
        'crud': 'update',
        'message': message,
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='CHANNEL') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/channel_view.html', context)


# Delete Channel
@login_required(login_url='/login/')
@role_required(allowed_roles='CHANNEL')
def channel_delete(request, _id):
    channels = Channel.objects.get(channel_id=_id)

    channels.delete()
    return HttpResponseRedirect(reverse('channel-index'))


@login_required(login_url='/login/')
@role_required(allowed_roles='CHANNEL')
def channel_view(request, _id):
    channels = Channel.objects.get(channel_id=_id)
    form = FormChannelView(instance=channels)

    context = {
        'form': form,
        'data': channels,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'channel',
        'group_segment': 'master',
        'crud': 'view',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='CHANNEL') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/channel_view.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='BUDGET')
def budget_add(request, _area):
    period = Closing.objects.all()
    closing = 'True'
    closing_period = 'True'
    message = ''
    area = AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', 'area__area_name')
    selected_area = _area
    name = AreaSales.objects.get(
        area_id=selected_area) if selected_area != 'NONE' else None
    distributor = Distributor.objects.filter(
        distributor_id__in=AreaSalesDetail.objects.filter(
            area_id=selected_area).values_list('distributor_id', flat=True)
    ).exclude(
        distributor_id__in=Budget.objects.filter(
            budget_area=selected_area,
            budget_month='{:02d}'.format(
                int(Closing.objects.get(document='BUDGET').month_open)),
            budget_year=Closing.objects.get(document='BUDGET').year_open
        ).values_list('budget_distributor_id', flat=True)
    )
    open_period = Closing.objects.get(document='BUDGET')
    month = '{:02d}'.format(int(request.POST.get('budget_month'))) if request.POST.get(
        'budget_month') else '{:02d}'.format(int(open_period.month_open))
    no_save = False
    if _area != 'NONE':
        approvers = BudgetApproval.objects.filter(
            area_id=_area).order_by('sequence')
        if approvers.count() == 0:
            message = "No budget's approver found for this area."
            no_save = True

    if period.count() == 0:
        closing_period = 'False'
    else:
        # if period[0].month_open == str(datetime.datetime.now().month) and period[0].year_open == str(datetime.datetime.now().year):
        if request.POST:
            form = FormBudget(request.POST, request.FILES)
            if form.is_valid():
                _id = 'UBS/' + \
                    request.POST.get('budget_area') + '/' + \
                    request.POST.get('budget_distributor') + '/' + \
                    month + '/' + request.POST.get('budget_year')
                try:
                    budget = Budget.objects.get(budget_id=_id)
                    if budget:
                        message = 'Budget already exist'
                except Budget.DoesNotExist:
                    parent = form.save(commit=False)
                    if parent.budget_amount == 0:
                        message = 'Beginning Budget is required'
                    else:
                        parent.budget_id = _id
                        parent.budget_balance = int(request.POST.get(
                            'budget_amount'))
                        parent.budget_status = 'DRAFT'
                        parent.budget_new = True
                        area = parent.budget_area.area_id
                        parent.save()
                        with connection.cursor() as cursor:
                            cursor.execute(
                                "SELECT channel_id FROM apps_areachanneldetail WHERE area_id = '" + str(area) + "' AND status = 1")
                            area_channels = cursor.fetchall()
                            for i in area_channels:
                                child = BudgetDetail(
                                    budget=parent, budget_channel_id=i[0])
                                child.save()

                        for j in approvers:
                            release = BudgetRelease(
                                budget=parent, budget_approval_id=j.approver_id, budget_approval_name=j.approver.username, budget_approval_email=j.approver.email, budget_approval_position=j.approver.position.position_name, sequence=j.sequence)
                            release.save()

                        email = User.objects.filter(
                            position_id='TMM', areauser__area_id=_area).values_list('email', flat=True)
                        recipient_list = list(email)
                        subject = 'Budget Percentages Input'
                        _message = 'Dear All,\n\nPlease note that Budget No. ' + _id + ' needs to be inputted as a budget percentage for each channel.\n\nClick the following link to upload some budget percentage at once.\n' + host.url + 'budget_upload/\n\nOr click the following link to change this budget channel percentage only.\n' + \
                            host.url + 'budget/view/draft/' + _id + '/NONE/' + '\n\nThank you.'
                        send_email(subject, _message, recipient_list)

                        return HttpResponseRedirect(reverse('budget-view', args=['draft', parent.budget_id, 'NONE']))
        # else:
        #     closing = 'False'

    form = FormBudget(
        initial={'budget_year': open_period.year_open, 'budget_month': month, 'budget_amount': 0, 'budget_upping': 0, 'budget_total': 0})

    msg = form.errors
    context = {
        'msg': msg,
        'message': message,
        'form': form,
        'area': area,
        'distributor': distributor,
        'selected_area': selected_area,
        'closing': closing,
        'closing_period': closing_period,
        'name': name,
        'no_save': no_save,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'budget',
        'group_segment': 'budget',
        'crud': 'add',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='BUDGET') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/budget_add.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='BUDGET')
def budget_index(request, _tab):
    drafts = Budget.objects.filter(budget_status='DRAFT', budget_area__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-budget_year', '-budget_month').all
    draft_count = Budget.objects.filter(budget_status='DRAFT', budget_area__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-budget_year', '-budget_month').count
    inapprovals = Budget.objects.filter(budget_status='IN APPROVAL', budget_area__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-budget_year', '-budget_month').values_list('budget_id', 'budget_distributor__distributor_name', 'budget_amount', 'budget_upping', 'budget_total', BudgetRelease.objects.filter(budget_id=OuterRef('budget_id'), budget_approval_status='N').order_by('sequence').values('budget_approval_name')[:1])
    inapprovals_count = Budget.objects.filter(budget_status='IN APPROVAL', budget_area__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-budget_year', '-budget_month').count
    opens = Budget.objects.filter(budget_status='OPEN', budget_area__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-budget_year', '-budget_month').all
    opens_count = Budget.objects.filter(budget_status='OPEN', budget_area__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-budget_year', '-budget_month').count

    context = {
        'drafts': drafts,
        'drafts_count': draft_count,
        'inapprovals': inapprovals,
        'inapprovals_count': inapprovals_count,
        'opens': opens,
        'opens_count': opens_count,
        'tab': _tab,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'budget',
        'group_segment': 'budget',
        'crud': 'index',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='BUDGET') if not request.user.is_superuser else Auth.objects.all(),
    }

    return render(request, 'home/budget_index.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='BUDGET-ARCHIVE')
def budget_archive_index(request):
    closed_budgets = Budget.objects.filter(budget_status='CLOSED', budget_area__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-budget_year', '-budget_month').all

    context = {
        'closed_budgets': closed_budgets,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'budget_archive',
        'group_segment': 'budget',
        'crud': 'archive',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='BUDGET-ARCHIVE') if not request.user.is_superuser else Auth.objects.all(),
    }

    return render(request, 'home/budget_archive.html', context)


# Update Budget
@login_required(login_url='/login/')
@role_required(allowed_roles='BUDGET')
def budget_update(request, _tab, _id):
    budgets = Budget.objects.get(budget_id=_id)
    budget_detail = BudgetDetail.objects.filter(budget_id=_id)
    total_beginning = BudgetDetail.objects.filter(
        budget_id=_id).aggregate(total=Sum('budget_amount'))['total']
    total_upping = BudgetDetail.objects.filter(
        budget_id=_id).aggregate(total=Sum('budget_upping'))['total']
    total_total = BudgetDetail.objects.filter(
        budget_id=_id).aggregate(total=Sum('budget_total'))['total']
    total_transfer_minus = BudgetDetail.objects.filter(budget_id=_id).aggregate(
        total=Sum('budget_transfer_minus'))['total']
    total_transfer_plus = BudgetDetail.objects.filter(budget_id=_id).aggregate(
        total=Sum('budget_transfer_plus'))['total']
    total_proposed = BudgetDetail.objects.filter(budget_id=_id).aggregate(
        total=Sum('budget_proposed'))['total']
    total_remaining = BudgetDetail.objects.filter(budget_id=_id).aggregate(
        total=Sum('budget_remaining'))['total']
    total_balance = BudgetDetail.objects.filter(
        budget_id=_id).aggregate(total=Sum('budget_balance'))['total']

    if request.POST:
        form = FormNewBudgetUpdate(
            request.POST, request.FILES, instance=budgets) if budgets.budget_new else FormBudgetUpdate(request.POST, request.FILES, instance=budgets)
        if form.is_valid():
            update = form.save(commit=False)
            update.budget_year = budgets.budget_year
            update.budget_month = budgets.budget_month
            update.save()

            for i in budget_detail:
                i.budget_amount = (i.budget_percent/100) * \
                    budgets.budget_amount if budgets.budget_new else i.budget_amount
                i.budget_upping = (i.budget_percent/100) * \
                    budgets.budget_upping
                i.save()

            budgets.budget_balance = BudgetDetail.objects.filter(
                budget_id=_id).aggregate(Sum('budget_balance'))['budget_balance__sum']
            budgets.save()

            if budgets.budget_status == 'DRAFT':
                email = User.objects.filter(
                    position_id='TMM', areauser__area_id=budgets.budget_area).values_list('email', flat=True)
                recipient_list = list(email)
                subject = 'Budget Percentages Input'
                message = 'Dear All,\n\nPlease note that Budget No. ' + _id + ' needs to be inputted as a budget percentage for each channel.\n\nClick the following link to upload some budget percentage at once.\n' + host.url + 'budget_upload/' + '\n\nOr click the following link to change this budget channel percentage only.\n' + \
                    host.url + 'budget/view/draft/' + _id + '/NONE/' + '\n\nThank you.'
                send_email(subject, message, recipient_list)

            return HttpResponseRedirect(reverse('budget-view', args=[_tab, _id, 'NONE']))
    else:
        form = FormNewBudgetUpdate(instance=budgets) if budgets.budget_new else FormBudgetUpdate(
            instance=budgets)

    YEAR_CHOICES = []
    for r in range((datetime.datetime.now().year-1), (datetime.datetime.now().year+2)):
        YEAR_CHOICES.append(str(r))

    MONTH_CHOICES = []
    for r in range(1, 13):
        MONTH_CHOICES.append(str(r))

    try:
        auth_percent = Auth.objects.get(
            user_id=request.user.user_id, menu_id='BUDGET-PERCENTAGE')
    except Auth.DoesNotExist:
        auth_percent = None

    message = form.errors
    context = {
        'form': form,
        'data': budgets,
        'year': YEAR_CHOICES,
        'month': MONTH_CHOICES,
        'budget_detail': budget_detail,
        'total_beginning': total_beginning,
        'total_upping': total_upping,
        'total_total': total_total,
        'total_balance': total_balance,
        'total_transfer_minus': total_transfer_minus,
        'total_transfer_plus': total_transfer_plus,
        'total_proposed': total_proposed,
        'total_remaining': total_remaining,
        'total_balance': total_balance,
        'new': budgets.budget_new,
        'tab': _tab,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'budget',
        'group_segment': 'budget',
        'crud': 'update',
        'message': message if message else 'NONE',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='BUDGET') if not request.user.is_superuser else Auth.objects.all(),
        'btn_percent': auth_percent if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/budget_view.html', context)


# Delete Budget
@login_required(login_url='/login/')
@role_required(allowed_roles='BUDGET')
def budget_delete(request, _tab, _id):
    budgets = Budget.objects.get(budget_id=_id)

    budgets.delete()
    return HttpResponseRedirect(reverse('budget-index', args=[_tab, ]))


@login_required(login_url='/login/')
@role_required(allowed_roles='BUDGET')
def budget_view(request, _tab, _id, _msg):
    budget = Budget.objects.get(budget_id=_id)
    budget.budget_amount = '{:,}'.format(budget.budget_amount)
    budget.budget_upping = '{:,}'.format(budget.budget_upping)
    budget.budget_total = '{:,}'.format(budget.budget_total)
    form = FormBudgetView(instance=budget)
    total_beginning = BudgetDetail.objects.filter(
        budget_id=_id).aggregate(total=Sum('budget_amount'))['total']
    total_upping = BudgetDetail.objects.filter(
        budget_id=_id).aggregate(total=Sum('budget_upping'))['total']
    total_total = BudgetDetail.objects.filter(
        budget_id=_id).aggregate(total=Sum('budget_total'))['total']
    total_transfer_minus = BudgetDetail.objects.filter(budget_id=_id).aggregate(
        total=Sum('budget_transfer_minus'))['total']
    total_transfer_plus = BudgetDetail.objects.filter(budget_id=_id).aggregate(
        total=Sum('budget_transfer_plus'))['total']
    total_proposed = BudgetDetail.objects.filter(budget_id=_id).aggregate(
        total=Sum('budget_proposed'))['total']
    total_remaining = BudgetDetail.objects.filter(budget_id=_id).aggregate(
        total=Sum('budget_remaining'))['total']
    total_balance = BudgetDetail.objects.filter(
        budget_id=_id).aggregate(total=Sum('budget_balance'))['total']

    budget_detail = BudgetDetail.objects.filter(budget_id=_id)
    hundreds = 0
    for i in budget_detail:
        hundreds += int(i.budget_percent)

        i.budget_amount = '{:,}'.format(i.budget_amount)
        i.budget_upping = '{:,}'.format(i.budget_upping)
        i.budget_total = '{:,}'.format(i.budget_total)
        i.budget_balance = '{:,}'.format(i.budget_balance)

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT apps_channel.channel_id, channel_name, q_channel.budget_channel_id FROM apps_channel LEFT JOIN (SELECT * FROM apps_budgetdetail WHERE budget_id = '" + str(_id) + "') AS q_channel ON apps_channel.channel_id = q_channel.budget_channel_id WHERE q_channel.budget_channel_id IS NULL")
        channel = cursor.fetchall()

    approval = BudgetRelease.objects.filter(budget_id=_id).order_by('sequence')

    YEAR_CHOICES = []
    for r in range((datetime.datetime.now().year-1), (datetime.datetime.now().year+2)):
        YEAR_CHOICES.append(str(r))

    MONTH_CHOICES = []
    for r in range(1, 13):
        MONTH_CHOICES.append(str(r))

    try:
        auth_percent = Auth.objects.get(
            user_id=request.user.user_id, menu_id='BUDGET-PERCENTAGE')
    except Auth.DoesNotExist:
        auth_percent = None

    context = {
        'form': form,
        'data': budget,
        'hundreds': hundreds,
        'total_beginning': total_beginning,
        'total_upping': total_upping,
        'total_total': total_total,
        'total_balance': total_balance,
        'total_transfer_minus': total_transfer_minus,
        'total_transfer_plus': total_transfer_plus,
        'total_proposed': total_proposed,
        'total_remaining': total_remaining,
        'status': budget.budget_status,
        'year': YEAR_CHOICES,
        'month': MONTH_CHOICES,
        'budget_detail': budget_detail,
        'approval': approval,
        'message': 'NONE' if _msg == 'NONE' else 'Total budget percentage you entered is not 100%',
        'tab': _tab,
        'channel': channel,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'budget_archive' if _tab == 'closed' else 'budget',
        'group_segment': 'budget',
        'crud': 'view',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='BUDGET') if not request.user.is_superuser else Auth.objects.all(),
        'btn_percent': auth_percent if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/budget_view.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='BUDGET')
def budget_detail_update(request, _tab, _id):
    budget = Budget.objects.get(budget_id=_id)
    detail = BudgetDetail.objects.filter(budget_id=_id)
    msg = 'NONE'
    if request.POST:
        hundreds = 0
        for i in detail:
            i.budget_percent = request.POST.get(
                'budget_percent_'+str(i.budget_channel_id))
            hundreds += int(i.budget_percent)
        if hundreds == 100:
            for i in detail:
                if budget.budget_new:
                    i.budget_amount = (Decimal(
                        int(i.budget_percent)/100) * budget.budget_amount)
                i.budget_upping = Decimal(
                    int(i.budget_percent)/100) * budget.budget_upping
                i.save()

            budget.budget_balance = BudgetDetail.objects.filter(
                budget_id=_id).aggregate(Sum('budget_balance'))['budget_balance__sum']
            budget.save()
        else:
            msg = 'Total budget percentage you entered is not 100%'

    return HttpResponseRedirect(reverse('budget-view', args=[_tab, _id, msg, ]))


@login_required(login_url='/login/')
@role_required(allowed_roles='BUDGET')
def budget_submit(request, _id):
    budget = Budget.objects.get(budget_id=_id)
    budget.budget_status = 'IN APPROVAL'
    budget.save()

    email = BudgetRelease.objects.filter(
        budget_id=_id).order_by('sequence').values_list('budget_approval_email', flat=True)
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT username FROM apps_budgetrelease INNER JOIN apps_user ON apps_budgetrelease.budget_approval_id = apps_user.user_id WHERE budget_id = '" + str(_id) + "' AND budget_approval_status = 'N' ORDER BY sequence LIMIT 1")
        approver = cursor.fetchone()

    subject = 'Budget Approval'
    message = 'Dear ' + approver[0] + ',\n\nYou have a new budget to approve. Please check your budget release list.\n\n' + \
        'Click this link to approve, revise or return this budget.\n' + host.url + 'budget_release/view/' + str(_id) + '/NONE/0/' + \
        '\n\nThank you.'
    send_email(subject, message, [email[0]])

    return HttpResponseRedirect(reverse('budget-index', args=['inapproval', ]))


@login_required(login_url='/login/')
@role_required(allowed_roles='BUDGET-PERCENTAGE')
def budget_upload(request):
    channels = Channel.objects.all()
    success = 0
    failed = 0
    errors = []
    recipients = []
    is_send = False
    if request.POST:
        UploadLog.objects.filter(document='BUDGET').delete()
        dataset = Dataset()
        new_budget_percent = request.FILES['budget_file']
        imported_data = dataset.load(new_budget_percent.read(), format='xlsx')
        for data in imported_data:
            col = 5
            hundreds = 0
            try:
                budget = Budget.objects.get(budget_id=data[4])
                if budget.budget_status == 'DRAFT':
                    i = col
                    for channel in channels:
                        try:
                            BudgetDetail.objects.get(
                                budget_id=data[4], budget_channel_id=channel.channel_id)
                            hundreds += data[i]
                        except BudgetDetail.DoesNotExist:
                            pass
                        i += 1

                    if hundreds == 100:
                        for channel in channels:
                            try:
                                rec = BudgetDetail.objects.get(
                                    budget_id=data[4], budget_channel_id=channel.channel_id)
                                rec.budget_percent = data[col]
                                if budget.budget_new:
                                    rec.budget_amount = (Decimal(
                                        int(data[col])/100) * budget.budget_amount)
                                rec.budget_upping = Decimal(
                                    int(data[col])/100) * budget.budget_upping
                                rec.save()
                                success += 1
                                budget.budget_status = 'IN APPROVAL'
                                budget.save()

                                is_send = True
                                email = BudgetRelease.objects.filter(
                                    budget_id=data[4]).order_by('sequence').values_list('budget_approval_email', flat=True)
                                with connection.cursor() as cursor:
                                    cursor.execute(
                                        "SELECT username FROM apps_budgetrelease INNER JOIN apps_user ON apps_budgetrelease.budget_approval_id = apps_user.user_id WHERE budget_id = '" + str(data[4]) + "' AND budget_approval_status = 'N' ORDER BY sequence LIMIT 1")
                                    approver = cursor.fetchone()
                                recipients.append((approver[0], email[0]))

                            except BudgetDetail.DoesNotExist:
                                pass
                            col += 1

                            budget.budget_balance = BudgetDetail.objects.filter(
                                budget_id=data[4]).aggregate(Sum('budget_balance'))['budget_balance__sum']
                            budget.save()
                    else:
                        failed += 1
                        errors.append(
                            'Budget No. ' + data[4] + ' percentage is not 100%.')
                        log = UploadLog(
                            document='BUDGET', document_id=data[4], description='Budget No. ' + data[4] + ' percentage is not 100%.')
                        log.save()
                else:
                    failed += 1
                    errors.append(
                        'Budget No. ' + data[4] + ' is not in DRAFT status.')
                    log = UploadLog(
                        document='BUDGET', document_id=data[4], description='Budget No. ' + data[4] + ' is not in DRAFT status.')
                    log.save()
            except Budget.DoesNotExist:
                failed += 1
                errors.append('Budget No. ' + data[4] + ' could not be found.')
                log = UploadLog(
                    document='BUDGET', document_id=data[4], description='Budget No. ' + data[4] + ' could not be found.')
                log.save()

        context = {
            'success': success,
            'failed': failed,
            'errors': errors,
            'total': imported_data.height,
            'budget_notif': budget_notification(request),
            'proposal_notif': proposal_notification(request),
            'program_notif': program_notification(request),
            'claim_notif': claim_notification(request),
            'cl_notif': cl_notification(request),
            'segment': 'budget_upload',
            'group_segment': 'budget',
            'crud': 'upload',
            'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
            'btn': Auth.objects.all(),
        }

        if is_send:
            recipient_list = list(dict.fromkeys(recipients))
            for mail_to in recipient_list:
                subject = 'Budget Approval'
                message = 'Dear ' + mail_to[0] + ',\n\nYou have some budgets to approve. Please check your dashboard.\n\n' + \
                    'Click this link to approve, revise or return the budgets.\n' + host.url + 'budget_release/' + \
                    '\n\nThank you.'
                send_email(subject, message, [mail_to[1]])

        return render(request, 'home/budget_uploadlog.html', context)

    context = {
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'budget_upload',
        'group_segment': 'budget',
        'crud': 'upload',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.all(),
    }
    return render(request, 'home/budget_upload.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='BUDGET-PERCENTAGE')
def export_uploadlog(request):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="Upload-Log-' + \
        str(datetime.datetime.now()) + '.xls"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Upload Log')
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['Budget No.', 'Description']
    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style)
    font_style = xlwt.XFStyle()

    rows = UploadLog.objects.filter(document='BUDGET').values_list(
        'document_id', 'description')
    for row in rows:
        row_num += 1
        for col_num in range(len(row)):
            ws.write(row_num, col_num, row[col_num], font_style)

    wb.save(response)
    return response


@login_required(login_url='/login/')
@role_required(allowed_roles='BUDGET-PERCENTAGE')
def export_budget_to_excel(request):
    channel = 'True'
    channel_ids = Channel.objects.values_list('channel_id', flat=True)
    if channel_ids.count() == 0:
        channel = 'False'
        return render(request, 'home/budget_upload  .html', {'channel': channel})

    # Retrieve budget data from the database
    budget_data = Budget.objects.filter(budget_status='DRAFT')

    # Create a new Excel workbook and add a worksheet
    workbook = xlsxwriter.Workbook('Budget_Data.xlsx')
    worksheet = workbook.add_worksheet('Budget Data')

    # Define column headers
    headers = ['Year', 'Month',
               'Area', 'Distributor', 'Budget ID']
    headers.extend([f"{channel_id} (%)" for channel_id in channel_ids])
    headers.append('Check')

    # Define cell formats
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#7eaa55',
        'font_color': 'white',
        'border': 1,
        'align': 'center',
    })
    cell_format = workbook.add_format({'border': 1, 'bg_color': '#e5eedc'})
    center = workbook.add_format(
        {'align': 'center', 'border': 1, 'bg_color': '#e5eedc'})
    cell_unlock = workbook.add_format(
        {'border': 1, 'bg_color': '#ffffff', 'locked': False})

    # Set column width
    worksheet.set_column(3, 3, 9)
    worksheet.set_column(4, 4, 24)

    # Write column headers to the worksheet
    for col_index, header in enumerate(headers):
        worksheet.write(0, col_index, header, header_format)

    # Write budget data to the worksheet
    for row_index, budget in enumerate(budget_data, start=1):
        worksheet.write(row_index, 0, budget.budget_year, center)
        worksheet.write(row_index, 1, budget.budget_month, center)
        worksheet.write(row_index, 2, budget.budget_area_id, cell_format)
        worksheet.write(
            row_index, 3, budget.budget_distributor_id, cell_format)
        worksheet.write(row_index, 4, budget.budget_id, cell_format)

        # Write channel data to the worksheet
        for col_index, channel_id in enumerate(channel_ids, start=5):
            try:
                budget_detail = BudgetDetail.objects.get(
                    budget_id=budget.budget_id, budget_channel_id=channel_id)
                worksheet.write(row_index, col_index,
                                budget_detail.budget_percent, cell_unlock)
            except BudgetDetail.DoesNotExist:
                worksheet.write(row_index, col_index, 0, cell_format)

        # Write formula for the 'Check' column
        formula = f"SUM({xlsxwriter.utility.xl_range(row_index, 5, row_index, 4 + len(channel_ids))})"
        worksheet.write_formula(
            row_index, 5 + len(channel_ids), formula, cell_format)

        # Apply conditional formatting for 'Check' column
        check_cell = xlsxwriter.utility.xl_rowcol_to_cell(
            row_index, 5 + len(channel_ids))
        format_red = workbook.add_format({'bg_color': 'red', 'border': 1})
        worksheet.conditional_format(
            check_cell, {'type': 'cell', 'criteria': '!=', 'value': 100, 'format': format_red})

    # Protect the worksheet
    worksheet.protect()

    workbook.close()

    # Return the Excel file as a response
    with open('Budget_Data.xlsx', 'rb') as file:
        response = HttpResponse(file.read(
        ), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=Budget_Data.xlsx'
        return response


@login_required(login_url='/login/')
@role_required(allowed_roles='TRANSFER')
def budget_transfer_index(request, _tab):
    drafts = BudgetTransfer.objects.filter(status='DRAFT', area_id__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-date').all
    draft_count = BudgetTransfer.objects.filter(status='DRAFT', area_id__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-date').count
    inapprovals = BudgetTransfer.objects.filter(status='IN APPROVAL', area_id__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-date').all
    inapprovals_count = BudgetTransfer.objects.filter(status='IN APPROVAL', area_id__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-date').count
    approved = BudgetTransfer.objects.filter(area_id__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-date').all
    approved_count = BudgetTransfer.objects.filter(status='OPEN', area_id__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-date').count

    context = {
        'drafts': drafts,
        'drafts_count': draft_count,
        'inapprovals': inapprovals,
        'inapprovals_count': inapprovals_count,
        'approved': approved,
        'approved_count': approved_count,
        'tab': _tab,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'transfer',
        'group_segment': 'transfer',
        'crud': 'index',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='TRANSFER') if not request.user.is_superuser else Auth.objects.all(),
    }

    return render(request, 'home/budget_transfer_index.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='TRANSFER')
def budget_transfer_add(request, _area, _distributor, _channel, _message):
    selected_area = _area
    selected_distributor = _distributor
    selected_channel = _channel
    area = AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', 'area__area_name')
    distributor = Budget.objects.filter(
        budget_status__in=['OPEN', 'DRAFT'], budget_area=selected_area).values_list('budget_distributor_id', 'budget_distributor__distributor_name', 'budget_id') if selected_area != '0' else None
    channel = BudgetDetail.objects.filter(budget_id=Budget.objects.get(budget_distributor_id=selected_distributor, budget_area=selected_area, budget_status__in=['OPEN', 'DRAFT']).budget_id,
                                          budget_balance__gt=0).values_list('budget_channel_id', 'budget_channel__channel_name', 'budget_balance') if selected_distributor != '0' else None
    channel_to = BudgetDetail.objects.filter(budget_id=Budget.objects.get(budget_distributor_id=selected_distributor, budget_area=selected_area, budget_status__in=['OPEN', 'DRAFT']).budget_id).exclude(
        budget_channel_id=selected_channel).values_list('budget_channel_id', 'budget_channel__channel_name') if selected_channel != '0' else None
    budget_balance = BudgetDetail.objects.get(budget_id=Budget.objects.get(budget_distributor_id=selected_distributor, budget_area=selected_area,
                                              budget_status__in=['OPEN', 'DRAFT']).budget_id, budget_channel_id=selected_channel).budget_balance if selected_channel != '0' else None
    period = Closing.objects.get(document='BUDGET')
    no_save = False

    # if selected_area != '0':
    #     approvers = BudgetTransferMatrix.objects.filter(
    #         area_id=_area).order_by('sequence')
    # if approvers.count() == 0:
    #     message = "No budget transfer's approver found for this area."
    #     no_save = True

    try:
        _no = BudgetTransfer.objects.filter(
            date__year=datetime.datetime.now().year).latest('seq_number')
    except BudgetTransfer.DoesNotExist:
        _no = None
    if _no is None:
        format_no = '{:04d}'.format(1)
    else:
        format_no = '{:04d}'.format(_no.seq_number + 1)

    if request.POST:
        form = FormBudgetTransfer(request.POST, request.FILES)
        if form.is_valid():
            if date.fromisoformat(request.POST.get('date')).month != int(period.month_open) or date.fromisoformat(request.POST.get('date')).year != int(period.year_open):
                message = 'Transfer date is not in the current period.'.replace(
                    '25', '')
                no_save = True

                return HttpResponseRedirect(reverse('budget-transfer-add', args=[selected_area, selected_distributor, selected_channel, message]))
            else:
                if form.cleaned_data['amount'] <= 0 or form.cleaned_data['amount'] > budget_balance:
                    message = 'Transfer amount is greater than the budget balance or less than or equal to 0.'.replace(
                        '25', '')
                    no_save = True

                    return HttpResponseRedirect(reverse('budget-transfer-add', args=[selected_area, selected_distributor, selected_channel, message]))
                else:
                    _id = 'TRF-6' + format_no + '/' + selected_area + '/' + \
                        selected_distributor + '/' + \
                        '{:02d}'.format(int(period.month_open)) + \
                        '/' + period.year_open
                    draft = form.save(commit=False)
                    draft.transfer_id = _id
                    draft.date = date.fromisoformat(request.POST.get('date'))
                    draft.seq_number = _no.seq_number + 1 if _no else 1
                    draft.area_id = selected_area
                    draft.distributor_id = selected_distributor
                    draft.channel_from_id = selected_channel
                    draft.channel_to_id = request.POST.get('channel_to')
                    draft.save()

                    period = Closing.objects.get(document='BUDGET')

                    transfer_from = BudgetTransfer.objects.filter(
                        area_id=selected_area, distributor_id=selected_distributor, channel_from_id=selected_channel, date__year=period.year_open, date__month=period.month_open).aggregate(Sum('amount'))['amount__sum']
                    budget_detail = BudgetDetail.objects.get(budget_id=Budget.objects.get(budget_area_id=selected_area,
                                                                                          budget_distributor_id=selected_distributor, budget_status__in=['OPEN', 'DRAFT']).budget_id, budget_channel_id=selected_channel)
                    budget_detail.budget_transfer_minus = transfer_from if transfer_from else 0
                    budget_detail.save()

                    transfer_to = BudgetTransfer.objects.filter(
                        area_id=selected_area, distributor_id=selected_distributor, channel_to_id=draft.channel_to_id, date__year=period.year_open, date__month=period.month_open).aggregate(Sum('amount'))['amount__sum']
                    channel_to = BudgetDetail.objects.get(budget_id=Budget.objects.get(budget_area_id=selected_area,
                                                                                       budget_distributor_id=selected_distributor, budget_status__in=['OPEN', 'DRAFT']).budget_id, budget_channel_id=draft.channel_to_id)
                    channel_to.budget_transfer_plus = transfer_to if transfer_to else 0
                    channel_to.save()

                    return HttpResponseRedirect(reverse('budget-transfer-index', args=['draft', ]))
    else:
        form = FormBudgetTransfer(
            initial={'date': datetime.datetime.now().date()})

    # msg = form.errors
    context = {
        # 'msg': msg,
        'form': form,
        'selected_area': selected_area,
        'selected_distributor': selected_distributor,
        'selected_channel': selected_channel,
        'area': area,
        'distributor': distributor,
        'channel': channel,
        'channel_to': channel_to,
        'budget_balance': budget_balance,
        'message': _message,
        'no_save': no_save,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'transfer',
        'group_segment': 'transfer',
        'crud': 'add',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='TRANSFER') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/budget_transfer_add.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='TRANSFER')
def budget_transfer_view(request, _tab, _id):
    transfer = BudgetTransfer.objects.get(transfer_id=_id)
    amount = transfer.amount
    transfer.amount = '{:,}'.format(transfer.amount)
    form = FormBudgetTransferView(instance=transfer)
    approval = BudgetTransferRelease.objects.filter(
        transfer_id=_id).order_by('sequence')
    channel = BudgetDetail.objects.filter(budget__budget_distributor_id=transfer.distributor, budget__budget_area=transfer.area, budget__budget_status__in=['OPEN', 'DRAFT'],
                                          budget_balance__gt=0).values_list('budget_channel_id', 'budget_channel__channel_name', 'budget_balance')
    channel_to = BudgetDetail.objects.filter(budget__budget_distributor_id=transfer.distributor_id, budget__budget_area=transfer.area_id, budget__budget_status__in=['OPEN', 'DRAFT']).exclude(
        budget_channel_id=transfer.channel_from).values_list('budget_channel_id', 'budget_channel__channel_name')
    budget_balance = BudgetDetail.objects.get(budget__budget_distributor_id=transfer.distributor, budget__budget_area=transfer.area,
                                              budget__budget_status__in=['OPEN', 'DRAFT'], budget_channel_id=transfer.channel_from).budget_balance if channel else 0
    selected_channel = transfer.channel_from_id
    message = '0'

    context = {
        'form': form,
        'data': transfer,
        'channel': channel,
        'channel_to': channel_to,
        'selected_channel': selected_channel,
        'budget_balance': budget_balance + amount,
        'tab': _tab,
        'status': transfer.status,
        'message': message,
        'approval': approval,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'transfer',
        'group_segment': 'transfer',
        'crud': 'view',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='TRANSFER') if not request.user.is_superuser else Auth.objects.all(),
    }

    return render(request, 'home/budget_transfer_view.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='TRANSFER')
def budget_transfer_update(request, _id, _area, _distributor, _channel, _message):
    selected_area = _area
    selected_distributor = _distributor
    selected_channel = _channel
    transfer = BudgetTransfer.objects.get(transfer_id=_id)
    channel = BudgetDetail.objects.filter(budget_id=Budget.objects.get(budget_distributor_id=transfer.distributor, budget_area=transfer.area, budget_status__in=['OPEN', 'DRAFT']).budget_id,
                                          budget_balance__gt=0).values_list('budget_channel_id', 'budget_channel__channel_name', 'budget_balance')
    channel_to = BudgetDetail.objects.filter(budget_id=Budget.objects.get(budget_distributor_id=transfer.distributor_id, budget_area=transfer.area_id, budget_status__in=['OPEN', 'DRAFT']).budget_id).exclude(
        budget_channel_id=_channel).values_list('budget_channel_id', 'budget_channel__channel_name')
    budget_balance = BudgetDetail.objects.get(budget_id=Budget.objects.get(budget_area_id=selected_area,
                                                                           budget_distributor_id=selected_distributor, budget_status__in=['OPEN', 'DRAFT']).budget_id, budget_channel_id=selected_channel).budget_balance if selected_channel != '0' else None
    amount = transfer.amount if _channel == transfer.channel_from_id else 0
    period = Closing.objects.get(document='BUDGET')
    no_save = False

    if request.POST:
        form = FormBudgetTransferUpdate(
            request.POST, request.FILES, instance=transfer)
        if form.is_valid():
            if date.fromisoformat(request.POST.get('date')).month != int(period.month_open) or date.fromisoformat(request.POST.get('date')).year != int(period.year_open):
                message = 'Transfer date is not in the current period.'.replace(
                    '25', '')
                no_save = True

                return HttpResponseRedirect(reverse('budget-transfer-update', args=[_id, selected_area, selected_distributor, selected_channel, message]))
            else:
                if form.cleaned_data['amount'] <= 0 or form.cleaned_data['amount'] > budget_balance:
                    message = 'Transfer amount is greater than the budget balance or less than or equal to 0.'.replace(
                        '25', '')
                    no_save = True

                    return HttpResponseRedirect(reverse('budget-transfer-update', args=[_id, selected_area, selected_distributor, selected_channel, message]))
                else:
                    period = Closing.objects.get(document='BUDGET')

                    update = form.save(commit=False)
                    update.channel_from_id = selected_channel
                    update.channel_to_id = request.POST.get('channel_to')
                    update.save()

                    all_channel = BudgetDetail.objects.filter(budget_id=Budget.objects.get(
                        budget_distributor_id=transfer.distributor, budget_area=transfer.area, budget_status__in=['OPEN', 'DRAFT']).budget_id)
                    for i in all_channel:
                        transfer_from = BudgetTransfer.objects.filter(
                            area_id=selected_area, distributor_id=selected_distributor, channel_from_id=i.budget_channel_id, date__year=period.year_open, date__month=period.month_open).aggregate(Sum('amount'))['amount__sum']
                        budget_detail = BudgetDetail.objects.get(budget_id=Budget.objects.get(budget_area_id=selected_area,
                                                                                              budget_distributor_id=selected_distributor, budget_status__in=['OPEN', 'DRAFT']).budget_id, budget_channel_id=i.budget_channel_id)
                        budget_detail.budget_transfer_minus = transfer_from if transfer_from else 0
                        budget_detail.save()

                        transfer_to = BudgetTransfer.objects.filter(
                            area_id=selected_area, distributor_id=selected_distributor, channel_to_id=i.budget_channel_id, date__year=period.year_open, date__month=period.month_open).aggregate(Sum('amount'))['amount__sum']
                        channel_to = BudgetDetail.objects.get(budget_id=Budget.objects.get(budget_area_id=selected_area,
                                                                                           budget_distributor_id=selected_distributor, budget_status__in=['OPEN', 'DRAFT']).budget_id, budget_channel_id=i.budget_channel_id)
                        channel_to.budget_transfer_plus = transfer_to if transfer_to else 0
                        channel_to.save()

                    return HttpResponseRedirect(reverse('budget-transfer-view', args=['draft', _id]))
    else:
        form = FormBudgetTransferUpdate(instance=transfer)

    msg = form.errors
    context = {
        'form': form,
        'data': transfer,
        'selected_area': selected_area,
        'selected_distributor': selected_distributor,
        'selected_channel': selected_channel,
        'channel': channel,
        'channel_to': channel_to,
        'budget_balance': budget_balance + amount,
        'msg': msg,
        'message': _message,
        'no_save': no_save,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'transfer',
        'group_segment': 'transfer',
        'crud': 'update',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='TRANSFER') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/budget_transfer_view.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='TRANSFER')
def budget_transfer_delete(request, _id):
    transfer = BudgetTransfer.objects.get(transfer_id=_id)
    transfer.delete()

    period = Closing.objects.get(document='BUDGET')

    transfer_from = BudgetTransfer.objects.filter(
        area_id=transfer.area, distributor_id=transfer.distributor, channel_from_id=transfer.channel_from, date__year=period.year_open, date__month=period.month_open).aggregate(Sum('amount'))['amount__sum']
    budget_detail = BudgetDetail.objects.get(budget_id=Budget.objects.get(budget_area_id=transfer.area,
                                                                          budget_distributor_id=transfer.distributor, budget_status__in=['OPEN', 'DRAFT']).budget_id, budget_channel_id=transfer.channel_from)
    budget_detail.budget_transfer_minus = transfer_from if transfer_from else 0
    budget_detail.save()

    transfer_to = BudgetTransfer.objects.filter(
        area_id=transfer.area, distributor_id=transfer.distributor, channel_to_id=transfer.channel_to_id, date__year=period.year_open, date__month=period.month_open).aggregate(Sum('amount'))['amount__sum']
    channel_to = BudgetDetail.objects.get(budget_id=Budget.objects.get(budget_area_id=transfer.area,
                                                                       budget_distributor_id=transfer.distributor, budget_status__in=['OPEN', 'DRAFT']).budget_id, budget_channel_id=transfer.channel_to_id)
    channel_to.budget_transfer_plus = transfer_to if transfer_to else 0
    channel_to.save()

    return HttpResponseRedirect(reverse('budget-transfer-index', args=['draft', ]))


@login_required(login_url='/login/')
@role_required(allowed_roles='TRANSFER')
def budget_transfer_submit(request, _id):
    transfer = BudgetTransfer.objects.get(transfer_id=_id)
    transfer.status = 'IN APPROVAL'
    transfer.save()

    approvers = BudgetTransferMatrix.objects.filter(
        area_id=transfer.area_id).order_by('sequence')
    for approver in approvers:
        BudgetTransferRelease.objects.create(
            transfer_id=_id, sequence=approver.sequence, transfer_approval_id=approver.approver_id, transfer_approval_name=approver.approver__username, transfer_approval_email=approver.approver__email, transfer_approval_position=approver.approver__position__position_name)

    email = BudgetTransferRelease.objects.filter(
        transfer_id=_id).order_by('sequence').values_list('transfer_approval_email', flat=True)
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT username FROM apps_budgettransferrelease INNER JOIN apps_user ON apps_budgettransferrelease.transfer_approval_id = apps_user.user_id WHERE transfer_id = '" + str(_id) + "' AND transfer_approval_status = 'N' ORDER BY sequence LIMIT 1")
        approver = cursor.fetchone()

    subject = 'Budget Transfer Approval'
    message = 'Dear ' + approver[0] + ',\n\nYou have a new budget transfer to approve. Please check your budget transfer release list.\n\n' + \
        'Click this link to approve, revise or return this budget transfer.\n' + host.url + 'budget_transfer_release/view/' + str(_id) + '/0/' + \
        '\n\nThank you.'
    send_email(subject, message, list(email))

    return HttpResponseRedirect(reverse('budget-transfer-index', args=['inapproval', ]))


@login_required(login_url='/login/')
@role_required(allowed_roles='TRANSFER-RELEASE')
def budget_transfer_release_index(request):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT apps_budgettransfer.transfer_id, apps_budgettransfer.date, apps_budgettransfer.area, apps_distributor.distributor_name, apps_budgettransfer.amount, apps_budgettransfer.status, apps_budgettransferrelease.sequence FROM apps_distributor INNER JOIN apps_budgettransfer ON apps_distributor.distributor_id = apps_budgettransfer.distributor_id INNER JOIN apps_budgettransferrelease ON apps_budgettransfer.transfer_id = apps_budgettransferrelease.transfer_id INNER JOIN (SELECT transfer_id, MIN(sequence) AS seq FROM apps_budgettransferrelease WHERE transfer_approval_status = 'N' GROUP BY transfer_id ORDER BY sequence ASC) AS q_group ON apps_budgettransferrelease.transfer_id = q_group.transfer_id AND apps_budgettransferrelease.sequence = q_group.seq WHERE (apps_budgettransfer.status = 'IN APPROVAL') AND apps_budgettransferrelease.transfer_approval_id = '" + str(request.user.user_id) + "'")
        release = cursor.fetchall()

    context = {
        'data': release,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'transfer_release',
        'group_segment': 'transfer',
        'crud': 'index',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='TRANSFER-RELEASE') if not request.user.is_superuser else Auth.objects.all(),
    }

    return render(request, 'home/budget_transfer_release_index.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='TRANSFER-RELEASE')
def budget_transfer_release_view(request, _id, _is_revise):
    transfer = BudgetTransfer.objects.get(transfer_id=_id)
    form = FormBudgetTransferView(instance=transfer)
    approval = BudgetTransferRelease.objects.filter(
        transfer_id=_id).order_by('sequence')

    approved = BudgetTransferRelease.objects.get(
        transfer_id=_id, transfer_approval_id=request.user.user_id).transfer_approval_status

    context = {
        'form': form,
        'data': transfer,
        'approval': approval,
        'is_revise': _is_revise,
        'approved': approved,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'transfer_release',
        'group_segment': 'transfer',
        'crud': 'view',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='TRANSFER-RELEASE') if not request.user.is_superuser else Auth.objects.all(),
    }

    return render(request, 'home/budget_transfer_release_view.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='TRANSFER-RELEASE')
def budget_transfer_release_approve(request, _id):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT transfer_id, MAX(sequence) AS seq FROM apps_budgettransferrelease GROUP BY transfer_id HAVING transfer_id = '" + str(_id) + "'")
        max_seq = cursor.fetchone()

    release = BudgetTransferRelease.objects.get(
        transfer_id=_id, transfer_approval_id=request.user.user_id)
    release.transfer_approval_status = 'Y'
    release.transfer_approval_date = timezone.now()
    release.save()

    transfer = BudgetTransfer.objects.get(transfer_id=_id)
    if release.sequence == max_seq[0][1]:
        transfer.status = 'OPEN'
    else:
        transfer.status = 'IN APPROVAL'

    transfer.save()

    email = BudgetTransferRelease.objects.filter(transfer_id=_id, transfer_approval_status='N').order_by(
        'sequence').values_list('transfer_approval_email', flat=True)
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT transfer_approval_name FROM apps_budgettransferrelease WHERE transfer_id = '" + str(_id) + "' AND transfer_approval_status = 'N' ORDER BY sequence LIMIT 1")
        approver = cursor.fetchone()

    subject = 'Budget Transfer Approval'
    message = 'Dear ' + approver[0] + ',\n\nYou have a new budget transfer to approve. Please check your budget transfer release list.\n\n' + \
        'Click this link to approve, revise or return this budget transfer.\n' + host.url + 'budget_transfer_release/view/' + str(_id) + '/0/' + \
        '\n\nThank you.'
    send_email(subject, message, [email[0]])

    return HttpResponseRedirect(reverse('budget-transfer-release-index'))


@login_required(login_url='/login/')
@role_required(allowed_roles='TRANSFER-RELEASE')
def budget_transfer_release_return(request, _id):
    recipients = []

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT transfer_id, email FROM apps_budgettransfer INNER JOIN apps_user ON apps_budgettransfer.entry_by = apps_user.user_id WHERE transfer_id = '" + str(_id) + "'")
        entry_mail = cursor.fetchone()
        recipients.append(entry_mail[1])

        cursor.execute(
            "SELECT transfer_id, email FROM apps_budgettransfer INNER JOIN apps_user ON apps_budgettransfer.update_by = apps_user.user_id WHERE transfer_id = '" + str(_id) + "'")
        update_mail = cursor.fetchone()
        recipients.append(update_mail[1])

        cursor.execute(
            "SELECT transfer_id, transfer_approval_email FROM apps_budgettransferrelease WHERE transfer_id = '" + str(_id) + "' AND transfer_approval_status = 'Y'")
        approver_mail = cursor.fetchall()
        for mail in approver_mail:
            recipients.append(mail[1])

    try:
        release = BudgetTransferRelease.objects.filter(
            transfer_id=_id, transfer_approval_status='Y')
        for r in release:
            r.transfer_approval_status = 'N'
            r.transfer_approval_date = None
            r.update_note = ''
            r.save()
    except BudgetTransferRelease.DoesNotExist:
        pass

    note = BudgetTransferRelease.objects.get(
        transfer_id=_id, transfer_approval_id=request.user.user_id)
    note.return_note = request.POST.get('return_note')
    note.save()

    transfer = BudgetTransfer.objects.get(transfer_id=_id)
    transfer.status = 'DRAFT'
    transfer.save()

    subject = 'Budget Transfer Return'
    message = 'Dear All, \n\nBudget Transfer No. ' + str(_id) + ' has been returned.\n\nNote: ' + \
        request.POST.get('return_note') + '\n\nClick this link to revise this budget transfer.\n' + host.url + 'budget_transfer/view/draft/' + str(_id) + \
        '\n\nThank you.'
    recipient_list = list(dict.fromkeys(recipients))
    send_email(subject, message, recipient_list)

    return HttpResponseRedirect(reverse('budget-transfer-release-index'))


@login_required(login_url='/login/')
@role_required(allowed_roles='TRANSFER-APPROVAL')
def budget_transfer_matrix_index(request):
    areas = AreaSales.objects.all()

    context = {
        'data': areas,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'transfer_approval',
        'group_segment': 'approval',
        'crud': 'index',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='TRANSFER-APPROVAL') if not request.user.is_superuser else Auth.objects.all(),
    }

    return render(request, 'home/budget_transfer_matrix_index.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='TRANSFER-APPROVAL')
def budget_transfer_matrix_view(request, _area):
    area = AreaSales.objects.get(area_id=_area)
    approvers = BudgetTransferMatrix.objects.filter(area_id=_area)
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT user_id, username, position_name, q_transferapprover.approver_id FROM apps_user INNER JOIN apps_position ON apps_user.position_id = apps_position.position_id LEFT JOIN (SELECT * FROM apps_budgettransfermatrix WHERE area_id = '" + str(_area) + "') AS q_transferapprover ON apps_user.user_id = q_transferapprover.approver_id WHERE q_transferapprover.approver_id IS NULL")
        users = cursor.fetchall()

    if request.POST:
        check = request.POST.getlist('checks[]')
        for i in users:
            if str(i[0]) in check:
                try:
                    approver = BudgetTransferMatrix(
                        area_id=_area, approver_id=i[0])
                    approver.save()
                except IntegrityError:
                    continue
            else:
                BudgetTransferMatrix.objects.filter(
                    area_id=_area, approver_id=i[0]).delete()

        return HttpResponseRedirect(reverse('budget-transfer-matrix-view', args=[_area]))

    context = {
        'data': area,
        'users': users,
        'approvers': approvers,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'transfer_approval',
        'group_segment': 'approval',
        'crud': 'view',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='TRANSFER-APPROVAL') if not request.user.is_superuser else Auth.objects.all(),
    }

    return render(request, 'home/budget_transfer_matrix_view.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='TRANSFER-APPROVAL')
def budget_transfer_matrix_update(request, _area, _id):
    approvers = BudgetTransferMatrix.objects.get(
        area_id=_area, approver_id=_id)

    if request.POST:
        approvers.sequence = int(request.POST.get('sequence'))
        approvers.save()

        return HttpResponseRedirect(reverse('budget-transfer-matrix-view', args=[_area]))

    return render(request, 'home/budget_transfer_matrix_view.html')


@login_required(login_url='/login/')
@role_required(allowed_roles='TRANSFER-APPROVAL')
def budget_transfer_matrix_delete(request, _area, _id):
    approvers = BudgetTransferMatrix.objects.get(
        area_id=_area, approver_id=_id)
    approvers.delete()

    return HttpResponseRedirect(reverse('budget-transfer-matrix-view', args=[_area]))


@login_required(login_url='/login/')
@role_required(allowed_roles='BUDGET-RELEASE')
def budget_release_index(request):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT apps_budget.budget_id, apps_distributor.distributor_name, apps_budget.budget_amount, apps_budget.budget_upping, apps_budget.budget_total, apps_budget.budget_status, apps_budgetrelease.sequence FROM apps_distributor INNER JOIN apps_budget ON apps_distributor.distributor_id = apps_budget.budget_distributor_id INNER JOIN apps_budgetrelease ON apps_budget.budget_id = apps_budgetrelease.budget_id INNER JOIN (SELECT budget_id, MIN(sequence) AS seq FROM apps_budgetrelease WHERE budget_approval_status = 'N' GROUP BY budget_id ORDER BY sequence ASC) AS q_group ON apps_budgetrelease.budget_id = q_group.budget_id AND apps_budgetrelease.sequence = q_group.seq WHERE (apps_budget.budget_status = 'IN APPROVAL') AND apps_budgetrelease.budget_approval_id = '" + str(request.user.user_id) + "'")
        release = cursor.fetchall()

    context = {
        'data': release,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'budget_release',
        'group_segment': 'budget',
        'crud': 'index',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='BUDGET-RELEASE') if not request.user.is_superuser else Auth.objects.all(),
    }

    return render(request, 'home/budget_release_index.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='PROPOSAL-RELEASE')
def proposal_release_index(request):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT apps_proposal.proposal_id, apps_proposal.proposal_date, apps_proposal.channel, apps_division.division_name, apps_proposal.total_cost, apps_proposal.status, apps_proposal.reference, apps_proposalrelease.sequence FROM apps_division INNER JOIN apps_proposal ON apps_division.division_id = apps_proposal.division_id INNER JOIN apps_proposalrelease ON apps_proposal.proposal_id = apps_proposalrelease.proposal_id INNER JOIN (SELECT proposal_id, MIN(sequence) AS seq FROM apps_proposalrelease WHERE proposal_approval_status = 'N' GROUP BY proposal_id ORDER BY sequence ASC) AS q_group ON apps_proposalrelease.proposal_id = q_group.proposal_id AND apps_proposalrelease.sequence = q_group.seq WHERE (apps_proposal.status = 'PENDING' OR apps_proposal.status = 'IN APPROVAL') AND apps_proposalrelease.proposal_approval_id = '" + str(request.user.user_id) + "'")
        release = cursor.fetchall()

    context = {
        'data': release,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'proposal_release',
        'group_segment': 'proposal',
        'crud': 'index',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list(
            'menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id,
                                menu_id='PROPOSAL-RELEASE') if not request.user.is_superuser else Auth.objects.all(),
    }

    return render(request, 'home/proposal_release_index.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='BUDGET-RELEASE')
def budget_release_view(request, _id, _msg, _is_revise):
    budget = Budget.objects.get(budget_id=_id)
    budget.budget_amount = '{:,}'.format(budget.budget_amount)
    budget.budget_upping = '{:,}'.format(budget.budget_upping)
    budget.budget_total = '{:,}'.format(budget.budget_total)
    form = FormBudgetView(instance=budget)
    total_beginning = BudgetDetail.objects.filter(
        budget_id=_id).aggregate(total=Sum('budget_amount'))['total']
    total_upping = BudgetDetail.objects.filter(
        budget_id=_id).aggregate(total=Sum('budget_upping'))['total']
    total_total = BudgetDetail.objects.filter(
        budget_id=_id).aggregate(total=Sum('budget_total'))['total']
    total_transfer_minus = BudgetDetail.objects.filter(budget_id=_id).aggregate(
        total=Sum('budget_transfer_minus'))['total']
    total_transfer_plus = BudgetDetail.objects.filter(budget_id=_id).aggregate(
        total=Sum('budget_transfer_plus'))['total']
    total_proposed = BudgetDetail.objects.filter(budget_id=_id).aggregate(
        total=Sum('budget_proposed'))['total']
    total_remaining = BudgetDetail.objects.filter(budget_id=_id).aggregate(
        total=Sum('budget_remaining'))['total']
    total_balance = BudgetDetail.objects.filter(
        budget_id=_id).aggregate(total=Sum('budget_balance'))['total']

    budget_detail = BudgetDetail.objects.filter(budget_id=_id)
    for detail in budget_detail:
        detail.budget_amount = '{:,}'.format(detail.budget_amount)
        detail.budget_upping = '{:,}'.format(detail.budget_upping)
        detail.budget_total = '{:,}'.format(detail.budget_total)
        detail.budget_balance = '{:,}'.format(detail.budget_balance)
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT apps_channel.channel_id, channel_name, q_channel.budget_channel_id FROM apps_channel LEFT JOIN (SELECT * FROM apps_budgetdetail WHERE budget_id = '" + str(_id) + "') AS q_channel ON apps_channel.channel_id = q_channel.budget_channel_id WHERE q_channel.budget_channel_id IS NULL")
        channel = cursor.fetchall()

    YEAR_CHOICES = []
    for r in range((datetime.datetime.now().year-1), (datetime.datetime.now().year+2)):
        YEAR_CHOICES.append(str(r))

    MONTH_CHOICES = []
    for r in range(1, 13):
        MONTH_CHOICES.append(str(r))

    approved = BudgetRelease.objects.get(
        budget_id=_id, budget_approval_id=request.user.user_id).budget_approval_status

    context = {
        'form': form,
        'data': budget,
        'total_beginning': total_beginning,
        'total_upping': total_upping,
        'total_total': total_total,
        'total_balance': total_balance,
        'total_transfer_minus': total_transfer_minus,
        'total_transfer_plus': total_transfer_plus,
        'total_proposed': total_proposed,
        'total_remaining': total_remaining,
        'year': YEAR_CHOICES,
        'month': MONTH_CHOICES,
        'budget_detail': budget_detail,
        'message': 'NONE' if _msg == 'NONE' else 'Total budget percentage you entered is not 100%',
        'channel': channel,
        'is_revise': _is_revise,
        'approved': approved,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'budget_release',
        'group_segment': 'budget',
        'crud': 'view',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='BUDGET-RELEASE') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/budget_release_view.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='PROPOSAL-RELEASE')
def proposal_release_view(request, _id, _sub_id, _act, _msg, _is_revise):
    proposal = Proposal.objects.get(proposal_id=_id)
    budget = BudgetDetail.objects.get(
        budget=proposal.budget, budget_channel=proposal.channel)
    available = budget.budget_amount + budget.budget_transfer_plus - \
        budget.budget_transfer_minus - budget.budget_proposed + budget.budget_remaining
    form = FormProposalView(instance=proposal)
    divs = Division.objects.all()
    refs = Proposal.objects.filter(status='OPEN', area=proposal.area, budget__budget_distributor_id=proposal.budget.budget_distributor_id,
                                   channel=proposal.channel).exclude(proposal_id=_id).order_by('-proposal_date')
    form_attachment = FormProposalAttachment()
    attachment = ProposalAttachment.objects.filter(proposal_id=_id)
    form_incremental = FormIncrementalSales()
    incremental = IncrementalSales.objects.filter(proposal_id=_id)
    total = IncrementalSales.objects.filter(proposal_id=_id).aggregate(
        swop_carton__sum=Sum('swop_carton'),
        swop_nom__sum=Sum('swop_nom'),
        swp_carton__sum=Sum('swp_carton'),
        swp_nom__sum=Sum('swp_nom'),
        incrp_carton__sum=Sum('incrp_carton'),
        incrp_nom__sum=Sum('incrp_nom'),
    )
    incpst_carton = (total['incrp_carton__sum'] / total['swop_carton__sum']
                     ) * 100 if total['swop_carton__sum'] else 0
    incpst_nom = (total['incrp_nom__sum'] / total['swop_nom__sum']
                  ) * 100 if total['swop_nom__sum'] else 0
    form_cost = FormProjectedCost()
    cost = ProjectedCost.objects.filter(proposal_id=_id)
    total_cost = ProjectedCost.objects.filter(
        proposal_id=_id).aggregate(Sum('cost'))
    add_cost = True if budget.budget_balance > 0 else False
    approved = ProposalRelease.objects.get(
        proposal_id=_id, proposal_approval_id=request.user.user_id).proposal_approval_status
    period = Closing.objects.get(document='BUDGET')
    diff_period = False

    if proposal.budget.budget_month != '{:02d}'.format(int(period.month_open)) or proposal.budget.budget_year != period.year_open:
        diff_period = True

    context = {
        'form': form,
        'available': available,
        'divs': divs,
        'refs': refs,
        'formAttachment': form_attachment,
        'attachment': attachment,
        'formInc': form_incremental,
        'incremental': incremental,
        'data': proposal,
        'budget': budget,
        'formCost': form_cost,
        'cost': cost,
        'total': total,
        'incpst_carton': incpst_carton,
        'incpst_nom': incpst_nom,
        'total_inc': total['incrp_nom__sum'] if total['incrp_nom__sum'] else 0,
        'total_cost': total_cost['cost__sum'] if total_cost['cost__sum'] else 0,
        'diff_period': diff_period,
        'sub_id': _sub_id,
        'action': _act,
        'message': _msg,
        'approved': approved,
        'is_revise': _is_revise,
        'status': proposal.status,
        'add_cost': add_cost,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'proposal_release',
        'group_segment': 'proposal',
        'crud': 'view',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='PROPOSAL-RELEASE') if not request.user.is_superuser else Auth.objects.all(),
        'btn_release': ProposalRelease.objects.get(proposal_id=_id, proposal_approval_id=request.user.user_id),
    }
    return render(request, 'home/proposal_release_view.html', context)


# Update Budget
@login_required(login_url='/login/')
@role_required(allowed_roles='BUDGET-RELEASE')
def budget_release_update(request, _id):
    budgets = Budget.objects.get(budget_id=_id)
    budget_detail = BudgetDetail.objects.filter(budget_id=_id)
    amount_before = budgets.budget_amount
    upping_before = budgets.budget_upping
    notes_before = budgets.budget_notes
    total_beginning = BudgetDetail.objects.filter(
        budget_id=_id).aggregate(total=Sum('budget_amount'))['total']
    total_upping = BudgetDetail.objects.filter(
        budget_id=_id).aggregate(total=Sum('budget_upping'))['total']
    total_total = BudgetDetail.objects.filter(
        budget_id=_id).aggregate(total=Sum('budget_total'))['total']
    total_transfer_minus = BudgetDetail.objects.filter(budget_id=_id).aggregate(
        total=Sum('budget_transfer_minus'))['total']
    total_transfer_plus = BudgetDetail.objects.filter(budget_id=_id).aggregate(
        total=Sum('budget_transfer_plus'))['total']
    total_proposed = BudgetDetail.objects.filter(budget_id=_id).aggregate(
        total=Sum('budget_proposed'))['total']
    total_remaining = BudgetDetail.objects.filter(budget_id=_id).aggregate(
        total=Sum('budget_remaining'))['total']
    total_balance = BudgetDetail.objects.filter(
        budget_id=_id).aggregate(total=Sum('budget_balance'))['total']

    if request.POST:
        form = FormNewBudgetUpdate(
            request.POST, request.FILES, instance=budgets) if budgets.budget_new else FormBudgetUpdate(request.POST, request.FILES, instance=budgets)
        if form.is_valid():
            update = form.save(commit=False)
            update.budget_year = budgets.budget_year
            update.budget_month = budgets.budget_month
            update.save()

            for i in budget_detail:
                i.budget_amount = (i.budget_percent/100) * \
                    budgets.budget_amount if budgets.budget_new else i.budget_amount
                i.budget_upping = (i.budget_percent/100) * \
                    budgets.budget_upping
                i.save()

            budgets.budget_balance = BudgetDetail.objects.filter(
                budget_id=_id).aggregate(Sum('budget_balance'))['budget_balance__sum']
            budgets.save()

            recipients = []

            release = BudgetRelease.objects.get(
                budget_id=_id, budget_approval_id=request.user.user_id)
            release.upping_note = request.POST.get('upping_note')
            release.save()

            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT budget_id, email FROM apps_budget INNER JOIN apps_user ON apps_budget.entry_by = apps_user.user_id WHERE budget_id = '" + str(_id) + "'")
                entry_mail = cursor.fetchone()
                recipients.append(entry_mail[1])

                cursor.execute(
                    "SELECT budget_id, email FROM apps_budget INNER JOIN apps_user ON apps_budget.update_by = apps_user.user_id WHERE budget_id = '" + str(_id) + "'")
                update_mail = cursor.fetchone()
                recipients.append(update_mail[1])

                cursor.execute(
                    "SELECT budget_id, email FROM apps_budgetdetail INNER JOIN apps_user ON apps_budgetdetail.update_by = apps_user.user_id WHERE budget_id = '" + str(_id) + "'")
                detail_mail = cursor.fetchone()
                recipients.append(detail_mail[1])

                cursor.execute(
                    "SELECT budget_id, budget_approval_email FROM apps_budgetrelease WHERE budget_id = '" + str(_id) + "' AND budget_approval_status = 'Y'")
                approver_mail = cursor.fetchone()
                if approver_mail:
                    recipients.append(approver_mail[1])

            subject = 'Budget Revised'
            message = 'Dear All,\n\nThe following is budget revise for Budget No. ' + \
                str(_id) + ':\n\nBEFORE:\n'
            if update.budget_amount != amount_before:
                message += 'Beginning Balance: ' + \
                    '{:,}'.format(amount_before)
            if update.budget_upping != upping_before:
                message += 'Upping Price: ' + '{:,}'.format(upping_before)
            if update.budget_notes != notes_before:
                message += 'Notes: ' + notes_before
            message += '\n\nAFTER:\n'
            if update.budget_amount != amount_before:
                message += 'Beginning Balance: ' + \
                    '{:,}'.format(update.budget_amount)
            if update.budget_upping != upping_before:
                message += 'Upping Price: ' + \
                    '{:,}'.format(update.budget_upping)
            if update.budget_notes != notes_before:
                message += 'Notes: ' + update.budget_notes
            message += '\n\nNote: ' + str(release.upping_note) + \
                '\n\nClick the following link to view the budget.\n' + host.url + 'budget/view/draft/' + \
                str(_id) + '/NONE/' + \
                '\n\nThank you.'
            recipient_list = list(dict.fromkeys(recipients))
            send_email(subject, message, recipient_list)

            return HttpResponseRedirect(reverse('budget-release-view', args=[_id, 'NONE', 0]))
    else:
        form = FormNewBudgetUpdate(instance=budgets) if budgets.budget_new else FormBudgetUpdate(
            instance=budgets)

    YEAR_CHOICES = []
    for r in range((datetime.datetime.now().year-1), (datetime.datetime.now().year+2)):
        YEAR_CHOICES.append(str(r))

    MONTH_CHOICES = []
    for r in range(1, 13):
        MONTH_CHOICES.append(str(r))

    message = form.errors
    context = {
        'form': form,
        'data': budgets,
        'total_beginning': total_beginning,
        'total_upping': total_upping,
        'total_total': total_total,
        'total_balance': total_balance,
        'total_transfer_minus': total_transfer_minus,
        'total_transfer_plus': total_transfer_plus,
        'total_proposed': total_proposed,
        'total_remaining': total_remaining,
        'year': YEAR_CHOICES,
        'month': MONTH_CHOICES,
        'budget_detail': budget_detail,
        'new': budgets.budget_new,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'budget_release',
        'group_segment': 'budget',
        'crud': 'update',
        'message': message if message else 'NONE',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='BUDGET-RELEASE') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/budget_release_view.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='PROPOSAL-RELEASE')
def proposal_release_update(request, _id):
    proposal = Proposal.objects.get(proposal_id=_id)
    divs = Division.objects.all()
    refs = Proposal.objects.filter(status='OPEN', area=proposal.area, budget__budget_distributor_id=proposal.budget.budget_distributor_id,
                                   channel=proposal.channel).exclude(proposal_id=_id).order_by('-proposal_date')
    attachment = ProposalAttachment.objects.filter(proposal_id=_id)
    incremental = IncrementalSales.objects.filter(proposal_id=_id)
    cost = ProjectedCost.objects.filter(proposal_id=_id)
    total = IncrementalSales.objects.filter(proposal_id=_id).aggregate(
        swop_carton__sum=Sum('swop_carton'),
        swop_nom__sum=Sum('swop_nom'),
        swp_carton__sum=Sum('swp_carton'),
        swp_nom__sum=Sum('swp_nom'),
        incrp_carton__sum=Sum('incrp_carton'),
        incrp_nom__sum=Sum('incrp_nom'),
        incpst_carton__ratio=(
            Sum('incpst_carton') / Sum('swop_carton')) * 100 if Sum('swop_carton') else 0,
        incpst_nom__ratio=(Sum('incpst_nom') / Sum('swop_nom')
                           ) * 100 if Sum('swop_nom') else 0,
    )
    incpst_carton = (total['incrp_carton__sum'] / total['swop_carton__sum']
                     ) * 100 if total['swop_carton__sum'] else 0
    incpst_nom = (total['incrp_nom__sum'] / total['swop_nom__sum']
                  ) * 100 if total['swop_nom__sum'] else 0
    total_cost = ProjectedCost.objects.filter(
        proposal_id=_id).aggregate(Sum('cost'))
    message = '0'
    _prg = proposal.program_name
    _div = proposal.division
    _prod = proposal.products
    _start = proposal.period_start.strftime('%d %b %Y')
    _end = proposal.period_end.strftime('%d %b %Y')
    _bck = proposal.background
    _obj = proposal.objectives
    _mech = proposal.mechanism
    _rem = proposal.remarks
    _add = proposal.reference

    if request.POST:
        form = FormProposalUpdate(
            request.POST, request.FILES, instance=proposal)
        if form.is_valid():
            parent = form.save(commit=False)
            parent.duration = form.cleaned_data['period_end'] - \
                form.cleaned_data['period_start']
            if parent.duration.days < 0:
                message = 'Period end must be greater than period start.'
            else:
                program_name = _prg if form.cleaned_data['program_name'] != _prg else None
                division = _div if form.cleaned_data['division'] != _div else None
                products = _prod if form.cleaned_data['products'] != _prod else None
                start = _start if form.cleaned_data['period_start'].strftime(
                    '%d %b %Y') != _start else None
                end = _end if form.cleaned_data['period_end'].strftime(
                    '%d %b %Y') != _end else None
                background = _bck if form.cleaned_data['background'] != _bck else None
                objectives = _obj if form.cleaned_data['objectives'] != _obj else None
                mechanism = _mech if form.cleaned_data['mechanism'] != _mech else None
                remarks = _rem if form.cleaned_data['remarks'] != _rem else None
                reference = _add if request.POST.get(
                    'reference') != _add else None
                parent.reference = request.POST.get('reference')
                parent.save()

                recipients = []

                release = ProposalRelease.objects.get(
                    proposal_id=_id, proposal_approval_id=request.user.user_id)
                release.revise_note = request.POST.get('revise_note')
                release.save()

                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT proposal_id, email FROM apps_proposal INNER JOIN apps_user ON apps_proposal.entry_by = apps_user.user_id WHERE proposal_id = '" + str(_id) + "'")
                    entry_mail = cursor.fetchone()
                    if entry_mail:
                        recipients.append(entry_mail[1])

                    cursor.execute(
                        "SELECT proposal_id, email FROM apps_proposal INNER JOIN apps_user ON apps_proposal.update_by = apps_user.user_id WHERE proposal_id = '" + str(_id) + "'")
                    update_mail = cursor.fetchone()
                    if update_mail:
                        recipients.append(update_mail[1])

                    cursor.execute(
                        "SELECT proposal_id, email FROM apps_incrementalsales INNER JOIN apps_user ON apps_incrementalsales.update_by = apps_user.user_id WHERE proposal_id = '" + str(_id) + "'")
                    incremental_mail = cursor.fetchone()
                    if incremental_mail:
                        recipients.append(incremental_mail[1])

                    cursor.execute(
                        "SELECT proposal_id, email FROM apps_projectedcost INNER JOIN apps_user ON apps_projectedcost.update_by = apps_user.user_id WHERE proposal_id = '" + str(_id) + "'")
                    cost_mail = cursor.fetchone()
                    if cost_mail:
                        recipients.append(cost_mail[1])

                    cursor.execute(
                        "SELECT proposal_id, proposal_approval_email FROM apps_proposalrelease WHERE proposal_id = '" + str(_id) + "' AND proposal_approval_status = 'Y'")
                    approver_mail = cursor.fetchall()
                    for mail in approver_mail:
                        recipients.append(mail[1])

                subject = 'Proposal Revised'
                msg = 'Dear All,\n\nThe following is revised proposal for Proposal No. ' + \
                    str(_id) + ':\n\nBEFORE\n'
                if program_name:
                    msg += 'Program Name: ' + str(program_name) + '\n'
                if division:
                    msg += 'Division: ' + str(division) + '\n'
                if products:
                    msg += 'Products: ' + str(products) + '\n'
                if start:
                    msg += 'Period Start: ' + start + '\n'
                if end:
                    msg += 'Period End: ' + end + '\n'
                if background:
                    msg += 'Background:\n' + str(background) + '\n'
                if objectives:
                    msg += 'Objectives:\n' + str(objectives) + '\n'
                if mechanism:
                    msg += 'Mechanism:\n' + str(mechanism) + '\n'
                if remarks:
                    msg += 'Remarks: ' + str(remarks) + '\n'
                if reference:
                    msg += 'Reference Proposal: ' + str(reference) + '\n'

                msg += '\nAFTER\n'
                if program_name:
                    msg += 'Program Name: ' + \
                        str(form.cleaned_data['program_name']) + '\n'
                if division:
                    msg += 'Division: ' + \
                        str(form.cleaned_data['division']) + '\n'
                if products:
                    msg += 'Products: ' + \
                        str(form.cleaned_data['products']) + '\n'
                if start:
                    msg += 'Period Start: ' + \
                        form.cleaned_data['period_start'].strftime(
                            '%d %b %Y') + '\n'
                if end:
                    msg += 'Period End: ' + \
                        str(form.cleaned_data['period_end'].strftime(
                            '%d %b %Y')) + '\n'
                if background:
                    msg += 'Background:\n' + \
                        str(form.cleaned_data['background']) + '\n'
                if objectives:
                    msg += 'Objectives:\n' + \
                        str(form.cleaned_data['objectives']) + '\n'
                if mechanism:
                    msg += 'Mechanism:\n' + \
                        str(form.cleaned_data['mechanism']) + '\n'
                if remarks:
                    msg += 'Remarks: ' + \
                        str(form.cleaned_data['remarks']) + '\n'
                if reference:
                    msg += 'Reference Proposal: ' + \
                        str(form.cleaned_data['reference']) + '\n'

                msg += '\nNote: ' + \
                    str(release.revise_note) + '\n\nClick the following link to view the proposal.\n' + host.url + 'proposal/view/inapproval/' + str(_id) + '/0/0/0/' + \
                    '\n\nThank you.'

                recipient_list = list(dict.fromkeys(recipients))
                send_email(subject, msg, recipient_list)

                return HttpResponseRedirect(reverse('proposal-release-view', args=[_id, '0', '0', '0', 0]))
    else:
        form = FormProposalUpdate(instance=proposal)

    msg = form.errors
    context = {
        'form': form,
        'refs': refs,
        'attachment': attachment,
        'incremental': incremental,
        'cost': cost,
        'total': total,
        'incpst_carton': incpst_carton,
        'incpst_nom': incpst_nom,
        'total_inc': total['incrp_nom__sum'] if total['incrp_nom__sum'] else 0,
        'total_cost': total_cost['cost__sum'] if total_cost['cost__sum'] else 0,
        'data': proposal,
        'divs': divs,
        'msg': msg,
        'message': message,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'proposal',
        'group_segment': 'proposal',
        'crud': 'update',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list(
            'menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id,
                                menu_id='PROPOSAL-RELEASE') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/proposal_release_view.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='BUDGET')
def budget_detail_release_update(request, _id):
    budget = Budget.objects.get(budget_id=_id)
    detail = BudgetDetail.objects.filter(budget_id=_id)
    channel_percent_before = []
    for i in detail:
        channel_percent_before.append((i.budget_channel_id, i.budget_percent))

    msg = 'NONE'
    if request.POST:
        hundreds = 0
        for i in detail:
            i.budget_percent = request.POST.get(
                'budget_percent_'+str(i.budget_channel_id))
            hundreds += int(i.budget_percent)
        if hundreds == 100:
            for i in detail:
                if budget.budget_new:
                    i.budget_amount = (Decimal(
                        int(i.budget_percent)/100) * budget.budget_amount)
                i.budget_upping = Decimal(
                    int(i.budget_percent)/100) * budget.budget_upping
                i.save()

            budget.budget_balance = BudgetDetail.objects.filter(
                budget_id=_id).aggregate(Sum('budget_balance'))['budget_balance__sum']
            budget.save()

            recipients = []

            release = BudgetRelease.objects.get(
                budget_id=_id, budget_approval_id=request.user.user_id)
            release.percentage_note = request.POST.get('percentage_note')
            release.save()

            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT budget_id, email FROM apps_budget INNER JOIN apps_user ON apps_budget.entry_by = apps_user.user_id WHERE budget_id = '" + str(_id) + "'")
                entry_mail = cursor.fetchone()
                recipients.append(entry_mail[1])

                cursor.execute(
                    "SELECT budget_id, email FROM apps_budget INNER JOIN apps_user ON apps_budget.update_by = apps_user.user_id WHERE budget_id = '" + str(_id) + "'")
                update_mail = cursor.fetchone()
                recipients.append(update_mail[1])

                cursor.execute(
                    "SELECT budget_id, email FROM apps_budgetdetail INNER JOIN apps_user ON apps_budgetdetail.update_by = apps_user.user_id WHERE budget_id = '" + str(_id) + "'")
                detail_mail = cursor.fetchone()
                recipients.append(detail_mail[1])

                cursor.execute(
                    "SELECT budget_id, budget_approval_email FROM apps_budgetrelease WHERE budget_id = '" + str(_id) + "' AND budget_approval_status = 'Y'")
                approver_mail = cursor.fetchone()
                if approver_mail:
                    recipients.append(approver_mail[1])

            subject = 'Channel Percentage Revised'
            message = 'Dear All,\n\nThe following are channel percentages update for Budget No. ' + \
                str(_id) + ':\n\nBEFORE\n'
            for i in channel_percent_before:
                message += str(i[0]) + ': ' + str(i[1]) + '%\n'
            message += '\nAFTER\n'
            for i in detail:
                message += str(i.budget_channel_id) + ': ' + \
                    str(i.budget_percent) + '%\n'
            message += '\nNote: ' + \
                str(release.percentage_note) + '\n\nClick the following link to view the budget.\n' + host.url + 'budget/view/draft/' + \
                str(_id) + '/NONE/' + \
                '\n\nThank you.'
            recipient_list = list(dict.fromkeys(recipients))
            send_email(subject, message, recipient_list)

            return HttpResponseRedirect(reverse('budget-release-view', args=[_id, 'NONE', 0]))
        else:
            msg = 'Total budget percentage you entered is not 100%'

    return HttpResponseRedirect(reverse('budget-release-view', args=[_id, msg, 1]))


@login_required(login_url='/login/')
@role_required(allowed_roles='PROPOSAL-RELEASE')
def proposal_release_incremental_add(request, _id):
    form = FormIncrementalSales(request.POST, request.FILES)
    proposal = Proposal.objects.get(proposal_id=_id)
    message = '0'
    if form.is_valid():
        try:
            check = IncrementalSales.objects.get(
                proposal_id=_id, product=request.POST.get('product'))
            if check:
                message = 'Product already exist'
        except IncrementalSales.DoesNotExist:
            swop_carton = int(request.POST.get('swop_carton'))
            swp_carton = int(request.POST.get('swp_carton'))
            if swop_carton > swp_carton:
                message = 'Sales With Program must be greater than Sales Without Program'
            else:
                incremental = form.save(commit=False)
                incremental.proposal_id = _id
                incremental.save()
                if incremental.incrp_nom < 0:
                    message = 'Incremental Sales must be greater than 0'
                    incremental.delete()
                else:
                    total_inc = IncrementalSales.objects.filter(proposal_id=_id).aggregate(Sum('incrp_nom'))[
                        'incrp_nom__sum'] if IncrementalSales.objects.filter(proposal_id=_id).exists() else 0
                    total_cost = ProjectedCost.objects.filter(proposal_id=_id).aggregate(Sum('cost'))[
                        'cost__sum'] if ProjectedCost.objects.filter(proposal_id=_id).exists() else 0
                    proposal.roi = (
                        total_cost / total_inc) * 100 if total_inc != 0 else 0
                    proposal.save()

    return HttpResponseRedirect(reverse('proposal-release-view', args=[_id, '0', 'add-item', message, 0]))


@login_required(login_url='/login/')
@role_required(allowed_roles='PROPOSAL-RELEASE')
def proposal_release_incremental_update(request, _id, _product):
    proposal = Proposal.objects.get(proposal_id=_id)
    update = IncrementalSales.objects.get(proposal_id=_id, id=_product)
    message = '0'
    if request.POST:
        swop_carton = int(request.POST.get('swop_carton'))
        swp_carton = int(request.POST.get('swp_carton'))
        if swop_carton > swp_carton:
            message = 'Sales With Program must be greater than Sales Without Program'
        else:
            swop_carton = update.swop_carton
            swp_carton = update.swp_carton
            swop_nom = update.swop_nom
            swp_nom = update.swp_nom
            update.swop_carton = int(request.POST.get('swop_carton'))
            update.swp_carton = int(request.POST.get('swp_carton'))
            update.swop_nom = int(request.POST.get('swop_nom'))
            update.swp_nom = int(request.POST.get('swp_nom'))
            update.save()
            if update.incrp_nom < 0:
                message = 'Incremental Sales must be greater than 0'
                update.swop_carton = swop_carton
                update.swp_carton = swp_carton
                update.swop_nom = swop_nom
                update.swp_nom = swp_nom
                update.save()
            else:
                total_inc = IncrementalSales.objects.filter(
                    proposal_id=_id).aggregate(Sum('incrp_nom'))['incrp_nom__sum'] if IncrementalSales.objects.filter(proposal_id=_id).exists() else 0
                total_cost = ProjectedCost.objects.filter(
                    proposal_id=_id).aggregate(Sum('cost'))['cost__sum'] if ProjectedCost.objects.filter(proposal_id=_id).exists() else 0
                proposal.roi = (total_cost / total_inc) * \
                    100 if total_inc != 0 else 0
                proposal.save()

    return HttpResponseRedirect(reverse('proposal-release-view', args=[_id, _product, 'upd-item', message, 0]))


@login_required(login_url='/login/')
@role_required(allowed_roles='PROPOSAL-RELEASE')
def proposal_release_incremental_delete(request, _id, _product):
    proposal = Proposal.objects.get(proposal_id=_id)
    incremental = IncrementalSales.objects.get(
        proposal_id=_id, id=_product)
    incremental.delete()
    total_inc = IncrementalSales.objects.filter(
        proposal_id=_id).aggregate(Sum('incrp_nom'))['incrp_nom__sum'] if IncrementalSales.objects.filter(proposal_id=_id).exists() else 0
    total_cost = ProjectedCost.objects.filter(
        proposal_id=_id).aggregate(Sum('cost'))['cost__sum'] if ProjectedCost.objects.filter(proposal_id=_id).exists() else 0
    proposal.roi = (total_cost / total_inc) * \
        100 if total_inc != 0 else 0
    proposal.save()

    return HttpResponseRedirect(reverse('proposal-release-view', args=[_id, '0', '0', '0', 0]))


@login_required(login_url='/login/')
@role_required(allowed_roles='PROPOSAL-RELEASE')
def proposal_release_cost_add(request, _id):
    form = FormProjectedCost(request.POST, request.FILES)
    proposal = Proposal.objects.get(proposal_id=_id)
    budget_detail = BudgetDetail.objects.get(
        budget=proposal.budget, budget_channel=proposal.channel)
    available = budget_detail.budget_amount + budget_detail.budget_transfer_plus - \
        budget_detail.budget_transfer_minus - \
        budget_detail.budget_proposed + budget_detail.budget_remaining
    message = '0'
    if form.is_valid():
        try:
            check = ProjectedCost.objects.get(
                proposal_id=_id, activities=request.POST.get('activities'))
            if check:
                message = 'Activity already exist'
        except ProjectedCost.DoesNotExist:
            cost = form.save(commit=False)
            balance = available if budget_detail.budget.budget_status == 'DRAFT' or budget_detail.budget.budget_status == 'IN APPROVAL' else budget_detail.budget_balance
            if cost.cost > balance:
                message = 'Total cost must be less than or equal to budget balance'
            else:
                cost.proposal_id = _id
                cost.save()
                total_inc = IncrementalSales.objects.filter(
                    proposal_id=_id).aggregate(Sum('incrp_nom'))['incrp_nom__sum'] if IncrementalSales.objects.filter(proposal_id=_id).exists() else 0
                total_cost = ProjectedCost.objects.filter(
                    proposal_id=_id).aggregate(Sum('cost'))['cost__sum'] if ProjectedCost.objects.filter(proposal_id=_id).exists() else 0
                proposal.roi = (total_cost / total_inc) * \
                    100 if total_inc != 0 else 0
                proposal.total_cost = total_cost
                proposal.balance = total_cost
                proposal.status = 'PENDING'
                proposal.save()
                sum_cost = Proposal.objects.filter(budget=proposal.budget, channel=proposal.channel).exclude(status__in=['REJECTED']).aggregate(Sum('total_cost'))[
                    'total_cost__sum'] if Proposal.objects.filter(budget=proposal.budget, channel=proposal.channel).exclude(status__in=['REJECTED']).exists() else 0
                budget_detail.budget_proposed = sum_cost
                budget_detail.save()
                sum_balance = BudgetDetail.objects.filter(budget=proposal.budget).aggregate(Sum('budget_balance'))[
                    'budget_balance__sum'] if BudgetDetail.objects.filter(budget=proposal.budget).exists() else 0
                budget = Budget.objects.get(budget_id=proposal.budget)
                budget.budget_balance = sum_balance
                budget.save()

    return HttpResponseRedirect(reverse('proposal-release-view', args=[_id, '0', 'add-cost', message, 0]))


@login_required(login_url='/login/')
@role_required(allowed_roles='PROPOSAL-RELEASE')
def proposal_release_cost_delete(request, _id, _activities):
    proposal = Proposal.objects.get(proposal_id=_id)
    budget_detail = BudgetDetail.objects.get(
        budget=proposal.budget, budget_channel=proposal.channel)
    cost = ProjectedCost.objects.get(proposal_id=_id, id=_activities)
    cost.delete()
    total_inc = IncrementalSales.objects.filter(
        proposal_id=_id).aggregate(Sum('incrp_nom'))['incrp_nom__sum'] if IncrementalSales.objects.filter(proposal_id=_id).exists() else 0
    total_cost = ProjectedCost.objects.filter(
        proposal_id=_id).aggregate(Sum('cost'))['cost__sum'] if ProjectedCost.objects.filter(proposal_id=_id).exists() else 0
    proposal.roi = (total_cost / total_inc) * \
        100 if total_inc != 0 else 0
    proposal.total_cost = total_cost
    proposal.balance = total_cost
    proposal.save()
    sum_cost = Proposal.objects.filter(budget=proposal.budget, channel=proposal.channel).exclude(status__in=['REJECTED']).aggregate(Sum('total_cost'))[
        'total_cost__sum'] if Proposal.objects.filter(budget=proposal.budget, channel=proposal.channel).exclude(status__in=['REJECTED']).exists() else 0
    budget_detail.budget_proposed = sum_cost
    budget_detail.save()
    sum_balance = BudgetDetail.objects.filter(budget=proposal.budget).aggregate(Sum('budget_balance'))[
        'budget_balance__sum'] if BudgetDetail.objects.filter(budget=proposal.budget).exists() else 0
    budget = Budget.objects.get(budget_id=proposal.budget)
    budget.budget_balance = sum_balance
    budget.save()

    return HttpResponseRedirect(reverse('proposal-release-view', args=[_id, '0', '0', '0', 0]))


@login_required(login_url='/login/')
@role_required(allowed_roles='PROPOSAL-RELEASE')
def proposal_release_cost_update(request, _id, _activities):
    proposal = Proposal.objects.get(proposal_id=_id)
    budget_detail = BudgetDetail.objects.get(
        budget=proposal.budget, budget_channel=proposal.channel)
    available = budget_detail.budget_amount + budget_detail.budget_transfer_plus - \
        budget_detail.budget_transfer_minus - \
        budget_detail.budget_proposed + budget_detail.budget_remaining
    update = ProjectedCost.objects.get(
        proposal_id=_id, id=_activities)
    message = '0'
    if request.POST:
        cost = update.cost
        balance = available if budget_detail.budget.budget_status == 'DRAFT' or budget_detail.budget.budget_status == 'IN APPROVAL' else budget_detail.budget_balance
        if int(request.POST.get('cost')) > balance + cost:
            message = 'Total cost must be less than or equal to budget balance'
        else:
            update.activities = request.POST.get('activities')
            update.cost = int(request.POST.get('cost'))
            update.save()
            total_inc = IncrementalSales.objects.filter(
                proposal_id=_id).aggregate(Sum('incrp_nom'))['incrp_nom__sum'] if IncrementalSales.objects.filter(proposal_id=_id).exists() else 0
            total_cost = ProjectedCost.objects.filter(
                proposal_id=_id).aggregate(Sum('cost'))['cost__sum'] if ProjectedCost.objects.filter(proposal_id=_id).exists() else 0
            proposal.roi = (total_cost / total_inc) * \
                100 if total_inc != 0 else 0
            proposal.total_cost = total_cost
            proposal.balance = total_cost
            proposal.save()
            sum_cost = Proposal.objects.filter(budget=proposal.budget, channel=proposal.channel).exclude(status__in=['REJECTED']).aggregate(Sum('total_cost'))[
                'total_cost__sum'] if Proposal.objects.filter(budget=proposal.budget, channel=proposal.channel).exclude(status__in=['REJECTED']).exists() else 0
            budget_detail.budget_proposed = sum_cost
            budget_detail.save()
            sum_balance = BudgetDetail.objects.filter(budget=proposal.budget).aggregate(Sum('budget_balance'))[
                'budget_balance__sum'] if BudgetDetail.objects.filter(budget=proposal.budget).exists() else 0
            budget = Budget.objects.get(budget_id=proposal.budget)
            budget.budget_balance = sum_balance
            budget.save()

    return HttpResponseRedirect(reverse('proposal-release-view', args=[_id, _activities, 'upd-cost', message, 0]))


@login_required(login_url='/login/')
@role_required(allowed_roles='PROPOSAL')
def proposal_print(request, _id):
    proposal = Proposal.objects.get(proposal_id=_id)
    prop_id = _id.replace('/', '-')

    # Create a new PDF file with landscape orientation
    filename = 'proposal_' + prop_id + '.pdf'
    pdf_file = canvas.Canvas(filename, pagesize=landscape(A4))

    # Set the font and font size
    pdf_file.setFont("Helvetica-Bold", 11)  # Set font to bold

    # Add logo in the top left corner
    logo_path = host.url + 'apps/static/img/favicon.png'
    pdf_file.drawImage(logo_path, 25, 515, width=60, height=60)

    # Add title beside the logo in the center of the page
    title = "PROGRAM PROPOSAL"
    title_width = pdf_file.stringWidth(
        title, "Helvetica-Bold", 11)  # Set font to bold
    page_width, _ = landscape(A4)
    title_x = (page_width - title_width) / 2
    pdf_file.setFont("Helvetica-Bold", 11)  # Set font to bold
    pdf_file.drawString(title_x, 545, title)

    # Write the proposal details to the PDF
    y = 510
    pdf_file.setFont("Helvetica-Bold", 8)
    pdf_file.drawString(25, y, "No.")
    pdf_file.drawString(50, y, ":")
    pdf_file.setFont("Helvetica", 8)
    pdf_file.drawString(60, y, pdf_file._escape(proposal.proposal_id))
    pdf_file.setFont("Helvetica-Bold", 8)
    pdf_file.drawString(title_x, y, "Channel")
    pdf_file.drawString(title_x + 40, y, ":")
    pdf_file.setFont("Helvetica", 8)
    pdf_file.drawString(title_x + 50, y, proposal.channel)
    y -= 10
    pdf_file.setFont("Helvetica-Bold", 8)
    pdf_file.drawString(25, y, "Date")
    pdf_file.drawString(50, y, ":")
    pdf_file.setFont("Helvetica", 8)
    pdf_file.drawString(60, y, proposal.proposal_date.strftime('%d %b %Y'))
    pdf_file.setFont("Helvetica-Bold", 8)
    pdf_file.drawString(title_x, y, "Division")
    pdf_file.drawString(title_x + 40, y, ":")
    pdf_file.setFont("Helvetica", 8)
    pdf_file.drawString(title_x + 50, y, proposal.division.division_name)
    y -= 10
    pdf_file.setFont("Helvetica-Bold", 8)
    pdf_file.drawString(25, y, "Type")
    pdf_file.drawString(50, y, ":")
    pdf_file.setFont("Helvetica", 8)
    pdf_file.drawString(60, y, proposal.type)

    y -= 20
    pdf_file.setFont("Helvetica-Bold", 8)
    pdf_file.drawString(25, y, "Program Name")
    pdf_file.drawString(90, y, ":")
    pdf_file.setFont("Helvetica", 8)
    pdf_file.drawString(100, y, proposal.program_name)
    y -= 10
    pdf_file.setFont("Helvetica-Bold", 8)
    pdf_file.drawString(25, y, "Products")
    pdf_file.drawString(90, y, ":")
    pdf_file.setFont("Helvetica", 8)
    pdf_file.drawString(100, y, proposal.products)
    y -= 10
    pdf_file.setFont("Helvetica-Bold", 8)
    pdf_file.drawString(25, y, "Area")
    pdf_file.drawString(90, y, ":")
    pdf_file.setFont("Helvetica", 8)
    pdf_file.drawString(100, y, proposal.area)
    y -= 10
    pdf_file.setFont("Helvetica-Bold", 8)
    pdf_file.drawString(25, y, "Period")
    pdf_file.drawString(90, y, ":")
    pdf_file.drawString(100, y, "Start : ")
    pdf_file.setFont("Helvetica", 8)
    pdf_file.drawString(130, y, proposal.period_start.strftime('%d/%m/%Y'))
    pdf_file.setFont("Helvetica-Bold", 8)
    pdf_file.drawString(200, y, "End : ")
    pdf_file.setFont("Helvetica", 8)
    pdf_file.drawString(230, y, proposal.period_end.strftime('%d/%m/%Y'))
    pdf_file.setFont("Helvetica-Bold", 8)
    pdf_file.drawString(300, y, "Duration : ")
    pdf_file.setFont("Helvetica", 8)
    pdf_file.drawString(350, y, str(proposal.duration) + ' days')
    y -= 10
    styles = getSampleStyleSheet()
    normal_style = styles["Normal"]
    normal_style.fontSize = 8  # Set font size to 8

    pdf_file.setFont("Helvetica-Bold", 8)
    pdf_file.drawString(25, y, "Background")
    pdf_file.drawString(90, y, ":")
    pdf_file.setFont("Helvetica", 8)
    background = proposal.background.split('\n')
    y -= 4
    b = 0
    for line in background:
        if b < 4:
            if len(background) > 4:
                background_paragraph = Paragraph(
                    line + "...", normal_style) if b == 3 else Paragraph(line, normal_style)
            else:
                background_paragraph = Paragraph(line, normal_style)
            background_paragraph.wrapOn(pdf_file, page_width - 125, 100)
            background_paragraph.drawOn(pdf_file, 100, y)
            y -= 10
            b += 1

    y += 4
    pdf_file.setFont("Helvetica-Bold", 8)
    pdf_file.drawString(25, y, "Mechanism")
    pdf_file.drawString(90, y, ":")
    pdf_file.setFont("Helvetica", 8)
    mechanism = proposal.mechanism.split('\n')
    y -= 4
    m = 0
    for line in mechanism:
        if m < 4:
            if len(mechanism) > 4:
                mechanism_paragraph = Paragraph(
                    line + "...", normal_style) if m == 3 else Paragraph(line, normal_style)
            else:
                mechanism_paragraph = Paragraph(line, normal_style)
            mechanism_paragraph.wrapOn(pdf_file, page_width - 125, 100)
            mechanism_paragraph.drawOn(pdf_file, 100, y)
            y -= 10
            m += 1

    y += 4
    pdf_file.setFont("Helvetica-Bold", 8)
    pdf_file.drawString(25, y, "Objectives")
    pdf_file.drawString(90, y, ":")
    pdf_file.setFont("Helvetica", 8)
    objectives = proposal.objectives.split('\n')
    y -= 4
    o = 0
    for line in objectives:
        if o < 4:
            if len(objectives) > 4:
                objectives_paragraph = Paragraph(
                    line + "...", normal_style) if o == 3 else Paragraph(line, normal_style)
            else:
                objectives_paragraph = Paragraph(line, normal_style)
            objectives_paragraph.wrapOn(pdf_file, page_width - 125, 100)
            objectives_paragraph.drawOn(pdf_file, 100, y)
            y -= 10
            o += 1

    y += 4
    pdf_file.setFont("Helvetica-Bold", 8)
    pdf_file.drawString(25, y, "Remarks")
    pdf_file.drawString(90, y, ":")
    pdf_file.setFont("Helvetica", 8)
    remarks = proposal.remarks.split('\n')
    y -= 4
    for line in remarks:
        remarks_paragraph = Paragraph(line, normal_style)
        remarks_paragraph.wrapOn(pdf_file, page_width - 125, 100)
        remarks_paragraph.drawOn(pdf_file, 100, y)
        y -= 10

    y += 4
    pdf_file.setFont("Helvetica-Bold", 8)
    pdf_file.drawString(25, y, "Attachment")
    pdf_file.drawString(90, y, ":")
    pdf_file.setFont("Helvetica", 8)
    # if proposal.attachment:
    #     pdf_file.drawString(100, y, proposal.attachment.name)
    # else:
    #     pdf_file.drawString(100, y, 'None')

    y -= 20
    pdf_file.setFont("Helvetica-Bold", 8)
    pdf_file.setFillColorRGB(1, 0, 0)
    # Set border color to black (RGB: 0, 0, 0)
    pdf_file.setStrokeColorRGB(0, 0, 0)
    # Draw rectangle with specified dimensions
    pdf_file.rect(25, y - 5, page_width - 50, 15, fill=True, stroke=True)

    pdf_file.setFillColorRGB(255, 255, 255)
    pdf_file.setFont("Helvetica-Bold", 8)
    pdf_file.drawString(title_x, y, "Incremental Sales Projection")

    pdf_file.setFillColorRGB(0, 0, 0)
    y -= 15
    pdf_file.rect(25, y - 20, 100, 30, stroke=True)
    title = "Product"
    title_width = pdf_file.stringWidth(title, "Helvetica-Bold", 8)
    title_x = 75 - (title_width / 2)
    pdf_file.drawString(title_x, y - 6, title)

    pdf_file.rect(125, y - 5, 200, 15, stroke=True)
    title = "Sales Without Program (Rp)"
    title_width = pdf_file.stringWidth(title, "Helvetica-Bold", 8)
    title_x = 225 - (title_width / 2)
    pdf_file.drawString(title_x, y, title)

    pdf_file.rect(325, y - 5, 200, 15, stroke=True)
    title = "Sales With Program (Rp)"
    title_width = pdf_file.stringWidth(title, "Helvetica-Bold", 8)
    title_x = 425 - (title_width / 2)
    pdf_file.drawString(title_x, y, title)

    pdf_file.rect(525, y - 5, 150, 15, stroke=True)
    title = "Incremental (Rp)"
    title_width = pdf_file.stringWidth(title, "Helvetica-Bold", 8)
    title_x = 600 - (title_width / 2)
    pdf_file.drawString(title_x, y, title)

    pdf_file.rect(675, y - 5, 142, 15, stroke=True)
    title = "Incremental (%)"
    title_width = pdf_file.stringWidth(title, "Helvetica-Bold", 8)
    title_x = 746 - (title_width / 2)
    pdf_file.drawString(title_x, y, title)

    y -= 15
    pdf_file.rect(125, y - 5, 100, 15, stroke=True)
    title = "Carton"
    title_width = pdf_file.stringWidth(title, "Helvetica-Bold", 8)
    title_x = 175 - (title_width / 2)
    pdf_file.drawString(title_x, y, title)

    pdf_file.rect(225, y - 5, 100, 15, stroke=True)
    title = "Rp"
    title_width = pdf_file.stringWidth(title, "Helvetica-Bold", 8)
    title_x = 275 - (title_width / 2)
    pdf_file.drawString(title_x, y, title)

    pdf_file.rect(325, y - 5, 100, 15, stroke=True)
    title = "Carton"
    title_width = pdf_file.stringWidth(title, "Helvetica-Bold", 8)
    title_x = 375 - (title_width / 2)
    pdf_file.drawString(title_x, y, title)

    pdf_file.rect(425, y - 5, 100, 15, stroke=True)
    title = "Rp"
    title_width = pdf_file.stringWidth(title, "Helvetica-Bold", 8)
    title_x = 475 - (title_width / 2)
    pdf_file.drawString(title_x, y, title)

    pdf_file.rect(525, y - 5, 75, 15, stroke=True)
    title = "Carton"
    title_width = pdf_file.stringWidth(title, "Helvetica-Bold", 8)
    title_x = 562 - (title_width / 2)
    pdf_file.drawString(title_x, y, title)

    pdf_file.rect(600, y - 5, 75, 15, stroke=True)
    title = "Rp"
    title_width = pdf_file.stringWidth(title, "Helvetica-Bold", 8)
    title_x = 637 - (title_width / 2)
    pdf_file.drawString(title_x, y, title)

    pdf_file.rect(675, y - 5, 71, 15, stroke=True)
    title = "Carton"
    title_width = pdf_file.stringWidth(title, "Helvetica-Bold", 8)
    title_x = 711 - (title_width / 2)
    pdf_file.drawString(title_x, y, title)

    pdf_file.rect(746, y - 5, 71, 15, stroke=True)
    title = "Rp"
    title_width = pdf_file.stringWidth(title, "Helvetica-Bold", 8)
    title_x = 782 - (title_width / 2)
    pdf_file.drawString(title_x, y, title)

    incremental = IncrementalSales.objects.filter(proposal_id=_id)
    pdf_file.setFont("Helvetica", 8)
    for i in incremental:
        y -= 15
        pdf_file.rect(25, y - 5, 100, 15, stroke=True)
        pdf_file.drawString(30, y, i.product)
        pdf_file.rect(125, y - 5, 100, 15, stroke=True)
        pdf_file.drawRightString(220, y, "{:,}".format(i.swop_carton))
        pdf_file.rect(225, y - 5, 100, 15, stroke=True)
        pdf_file.drawRightString(320, y, "{:,}".format(i.swop_nom))
        pdf_file.rect(325, y - 5, 100, 15, stroke=True)
        pdf_file.drawRightString(420, y, "{:,}".format(i.swp_carton))
        pdf_file.rect(425, y - 5, 100, 15, stroke=True)
        pdf_file.drawRightString(520, y, "{:,}".format(i.swp_nom))
        pdf_file.rect(525, y - 5, 75, 15, stroke=True)
        pdf_file.drawRightString(595, y, "{:,}".format(i.incrp_carton))
        pdf_file.rect(600, y - 5, 75, 15, stroke=True)
        pdf_file.drawRightString(670, y, "{:,}".format(i.incrp_nom))
        pdf_file.rect(675, y - 5, 71, 15, stroke=True)
        pdf_file.drawRightString(743, y, "{:,}%".format(i.incpst_carton))
        pdf_file.rect(746, y - 5, 71, 15, stroke=True)
        pdf_file.drawRightString(814, y, "{:,}%".format(i.incpst_nom))

    total = IncrementalSales.objects.filter(proposal_id=_id).aggregate(
        swop_carton__sum=Sum('swop_carton'),
        swop_nom__sum=Sum('swop_nom'),
        swp_carton__sum=Sum('swp_carton'),
        swp_nom__sum=Sum('swp_nom'),
        incrp_carton__sum=Sum('incrp_carton'),
        incrp_nom__sum=Sum('incrp_nom'),
        incpst_carton__ratio=(Sum('incrp_carton') /
                              Sum('swop_carton')) * 100 if Sum('swop_carton') else 0,
        incpst_nom__ratio=(Sum('incrp_nom') /
                           Sum('swop_nom')) * 100 if Sum('swop_nom') else 0,
    )
    y -= 15
    pdf_file.rect(25, y - 5, 100, 15, stroke=True)
    pdf_file.setFont("Helvetica-Bold", 8)
    pdf_file.drawString(30, y, "Total")
    pdf_file.rect(125, y - 5, 100, 15, stroke=True)
    pdf_file.drawRightString(220, y, "{:,}".format(total['swop_carton__sum']))
    pdf_file.rect(225, y - 5, 100, 15, stroke=True)
    pdf_file.drawRightString(320, y, "{:,}".format(total['swop_nom__sum']))
    pdf_file.rect(325, y - 5, 100, 15, stroke=True)
    pdf_file.drawRightString(420, y, "{:,}".format(total['swp_carton__sum']))
    pdf_file.rect(425, y - 5, 100, 15, stroke=True)
    pdf_file.drawRightString(520, y, "{:,}".format(total['swp_nom__sum']))
    pdf_file.rect(525, y - 5, 75, 15, stroke=True)
    pdf_file.drawRightString(595, y, "{:,}".format(total['incrp_carton__sum']))
    pdf_file.rect(600, y - 5, 75, 15, stroke=True)
    pdf_file.drawRightString(670, y, "{:,}".format(total['incrp_nom__sum']))
    pdf_file.rect(675, y - 5, 71, 15, stroke=True)
    pdf_file.drawRightString(743, y, "{:.1f}%".format(
        total['incpst_carton__ratio'])) if total['incpst_carton__ratio'] else pdf_file.drawRightString(743, y, "0.0%")
    pdf_file.rect(746, y - 5, 71, 15, stroke=True)
    pdf_file.drawRightString(
        814, y, "{:.1f}%".format(total['incpst_nom__ratio'])) if total['incpst_nom__ratio'] else pdf_file.drawRightString(814, y, "0.0%")

    y -= 25
    pdf_file.setFont("Helvetica-Bold", 8)
    # Set fill color to red (RGB: 255, 0, 0)
    pdf_file.setFillColorRGB(1, 0, 0)
    # Set border color to black (RGB: 0, 0, 0)
    pdf_file.setStrokeColorRGB(0, 0, 0)
    # Draw rectangle with specified dimensions
    pdf_file.rect(25, y - 5, (page_width / 2) +
                  50, 15, fill=True, stroke=True)

    pdf_file.setFillColorRGB(255, 255, 255)
    pdf_file.setFont("Helvetica-Bold", 8)
    title = "Projected Cost"
    title_width = pdf_file.stringWidth(title, "Helvetica-Bold", 8)
    title_x = 25 + (((page_width / 2) + 50) - title_width) / 2
    pdf_file.drawString(title_x, y, title)

    pdf_file.setFillColorRGB(1, 0, 0)
    pdf_file.rect((page_width / 2) + 90, y - 5,
                  (page_width / 2) - 115, 15, fill=True, stroke=True)
    pdf_file.setFillColorRGB(255, 255, 255)
    title = "ROI"
    title_width = pdf_file.stringWidth(title, "Helvetica-Bold", 8)
    title_x = ((page_width / 2) + 90) + \
        (((page_width / 2) - 115) - title_width) / 2
    pdf_file.drawString(title_x, y, title)

    y -= 15
    pdf_file.setFillColorRGB(0, 0, 0)
    pdf_file.rect(25, y - 5, 350, 15, stroke=True)
    title = "Activities"
    title_width = pdf_file.stringWidth(title, "Helvetica-Bold", 8)
    title_x = 200 - (title_width / 2)
    pdf_file.drawString(title_x, y, title)

    pdf_file.rect(375, y - 5, 121, 15, stroke=True)
    title = "Cost"
    title_width = pdf_file.stringWidth(title, "Helvetica-Bold", 8)
    title_x = 435 - (title_width / 2)
    pdf_file.drawString(title_x, y, title)

    pdf_file.setFont("Helvetica", 8)
    pdf_file.rect((page_width / 2) + 90, y - 5, 175, 15, stroke=True)
    pdf_file.drawString(
        (page_width / 2) + 95, y, "Projected Cost")
    pdf_file.rect((page_width / 2) + 265, y - 5, 131, 15, stroke=True)
    pdf_file.drawRightString(
        (page_width / 2) + 390, y, "{:,}".format(proposal.total_cost))

    cost = ProjectedCost.objects.filter(proposal_id=_id)

    y -= 15
    y1 = y
    pdf_file.setFont("Helvetica", 8)
    pdf_file.rect((page_width / 2) + 90, y - 5, 175, 15, stroke=True)
    pdf_file.drawString(
        (page_width / 2) + 95, y, "Incremental Sales Projection")
    pdf_file.rect((page_width / 2) + 265, y - 5, 131, 15, stroke=True)
    pdf_file.drawRightString(
        (page_width / 2) + 390, y, "{:,}".format(total['incrp_nom__sum']))

    y -= 15
    pdf_file.setFont("Helvetica-Bold", 8)
    pdf_file.rect((page_width / 2) + 90, y - 5, 175, 15, stroke=True)
    pdf_file.drawString(
        (page_width / 2) + 95, y, "ROI")
    pdf_file.rect((page_width / 2) + 265, y - 5, 131, 15, stroke=True)
    pdf_file.drawRightString(
        (page_width / 2) + 390, y, "{:,}%".format(proposal.roi))

    pdf_file.setFont("Helvetica", 8)
    for i in cost:
        pdf_file.rect(25, y1 - 5, 350, 15, stroke=True)
        pdf_file.drawString(30, y1, i.activities)
        pdf_file.rect(375, y1 - 5, 121, 15, stroke=True)
        pdf_file.drawRightString(490, y1, "{:,}".format(i.cost))
        y1 -= 15

    pdf_file.rect(25, y1 - 5, 350, 15, stroke=True)
    pdf_file.setFont("Helvetica-Bold", 8)
    pdf_file.drawString(30, y1, "Total")
    pdf_file.rect(375, y1 - 5, 121, 15, stroke=True)
    pdf_file.drawRightString(490, y1, "{:,}".format(proposal.total_cost))

    y = y1
    y -= 25
    col_width = (page_width - 50) / 11
    proposal = Proposal.objects.get(proposal_id=_id)
    approver = ProposalRelease.objects.filter(
        proposal_id=_id, proposal_approval_status='Y', printed=True).order_by('sequence')
    proposer = ProposalRelease.objects.filter(proposal_id=_id, proposal_approval_status='Y', as_approved='proposer', printed=True).aggregate(
        id=Count('id')) if ProposalRelease.objects.filter(proposal_id=_id, proposal_approval_status='Y', as_approved='proposer', printed=True).exists() else 0
    checker = ProposalRelease.objects.filter(proposal_id=_id, proposal_approval_status='Y', as_approved='checker', printed=True).aggregate(
        id=Count('id')) if ProposalRelease.objects.filter(proposal_id=_id, proposal_approval_status='Y', as_approved='checker', printed=True).exists() else 0
    approvers = ProposalRelease.objects.filter(proposal_id=_id, proposal_approval_status='Y', as_approved='approver', printed=True).aggregate(
        id=Count('id')) if ProposalRelease.objects.filter(proposal_id=_id, proposal_approval_status='Y', as_approved='approver', printed=True).exists() else 0
    validator = ProposalRelease.objects.filter(proposal_id=_id, proposal_approval_status='Y', as_approved='validator', printed=True).aggregate(
        id=Count('id')) if ProposalRelease.objects.filter(proposal_id=_id, proposal_approval_status='Y', as_approved='validator', printed=True).exists() else 0
    finalizer = ProposalRelease.objects.filter(proposal_id=_id, proposal_approval_status='Y', as_approved='finalizer', printed=True).aggregate(
        id=Count('id')) if ProposalRelease.objects.filter(proposal_id=_id, proposal_approval_status='Y', as_approved='finalizer', printed=True).exists() else 0

    proposer_count = proposer['id'] if proposer else 0
    checker_count = checker['id'] if checker else 0
    approvers_count = approvers['id'] if approvers else 0
    validator_count = validator['id'] if validator else 0
    finalizer_count = finalizer['id'] if finalizer else 0

    pdf_file.setFont("Helvetica", 8)
    pdf_file.rect(
        25, y - 5, (col_width * (proposer_count + 1)), 15, stroke=True)
    title = 'Proposed By' if proposer_count > 0 else ''
    title_width = pdf_file.stringWidth(title, "Helvetica", 8)
    title_x = 25 + ((col_width * (proposer_count + 1)) - title_width) / 2
    pdf_file.drawString(title_x, y, title)

    pdf_file.rect(
        25 + (col_width * (proposer_count + 1)), y - 5, col_width * checker_count, 15, stroke=True)
    title = 'Checked By' if checker_count > 0 else ''
    title_x = 25 + (col_width * (proposer_count + 1)) + \
        ((col_width * checker_count) - title_width) / 2
    pdf_file.drawString(title_x, y, title)

    pdf_file.rect(
        25 + (col_width * (proposer_count + 1)) + (col_width * checker_count), y - 5, col_width * approvers_count, 15, stroke=True)
    title = 'Approved By' if approvers_count > 0 else ''
    title_x = 25 + (col_width * (proposer_count + 1)) + \
        (col_width * checker_count) + \
        ((col_width * approvers_count) - title_width) / 2
    pdf_file.drawString(title_x, y, title)

    pdf_file.rect(
        25 + (col_width * (proposer_count + 1)) + (col_width * checker_count) + (col_width * approvers_count), y - 5, col_width * validator_count, 15, stroke=True)
    title = 'Validated By' if validator_count > 0 else ''
    title_x = 25 + (col_width * (proposer_count + 1)) + (col_width * checker_count) + \
        (col_width * approvers_count) + \
        ((col_width * validator_count) - title_width) / 2
    pdf_file.drawString(title_x, y, title)

    pdf_file.rect(
        25 + (col_width * (proposer_count + 1)) + (col_width * checker_count) + (col_width * approvers_count) + (col_width * validator_count), y - 5, col_width * finalizer_count, 15, stroke=True)
    title = 'Approved By' if finalizer_count > 0 else ''
    title_x = 25 + (col_width * (proposer_count + 1)) + (col_width * checker_count) + (col_width * approvers_count) + \
        (col_width * validator_count) + \
        ((col_width * finalizer_count) - title_width) / 2
    pdf_file.drawString(title_x, y, title)

    pdf_file.rect(25, y - 55, col_width, 50, stroke=True)
    sign_path = User.objects.get(user_id=proposal.entry_by).signature.path if User.objects.get(
        user_id=proposal.entry_by).signature else ''
    if sign_path:
        pdf_file.drawImage(sign_path, 30, y - 50,
                           width=col_width - 10, height=40)
    else:
        pass
    pdf_file.rect(25, y - 70, col_width, 15, stroke=True)
    title = proposal.entry_pos
    title_width = pdf_file.stringWidth(title, "Helvetica-Bold", 8)
    title_x = 25 + (col_width - title_width) / 2
    pdf_file.setFont("Helvetica-Bold", 8)
    pdf_file.drawString(title_x, y - 65, title)
    pdf_file.rect(25, y - 85, col_width, 15, stroke=True)
    pdf_file.setFont("Helvetica", 8)
    title = 'Date: ' + proposal.entry_date.strftime('%d/%m/%Y')
    title_width = pdf_file.stringWidth(title, "Helvetica", 8)
    title_x = 25 + (col_width - title_width) / 2
    pdf_file.drawString(title_x, y - 80, title)

    for i in range(1, approver.count() + 1):
        pdf_file.rect(25 + (col_width * i), y - 55, col_width, 50, stroke=True)
        if approver:
            sign_path = User.objects.get(user_id=approver[i - 1].proposal_approval_id).signature.path if User.objects.get(
                user_id=approver[i - 1].proposal_approval_id).signature else ''
            if sign_path:
                pdf_file.drawImage(sign_path, 30 + (col_width * i), y - 50,
                                   width=col_width - 10, height=40)
            else:
                pass
            pdf_file.rect(25 + (col_width * i), y - 70,
                          col_width, 15, stroke=True)
            title = approver[i - 1].proposal_approval_position
            title_width = pdf_file.stringWidth(title, "Helvetica-Bold", 8)
            title_x = 25 + (col_width * i) + (col_width - title_width) / 2
            pdf_file.setFont("Helvetica-Bold", 8)
            pdf_file.drawString(title_x, y - 65, title)
            pdf_file.rect(25 + (col_width * i), y - 85,
                          col_width, 15, stroke=True)
            pdf_file.setFont("Helvetica", 8)
            title = 'Date: ' + \
                approver[i - 1].proposal_approval_date.strftime('%d/%m/%Y')
            title_width = pdf_file.stringWidth(title, "Helvetica", 8)
            title_x = 25 + (col_width * i) + (col_width - title_width) / 2
            pdf_file.drawString(title_x, y - 80, title)
        else:
            pass

    pdf_file.save()

    # # Assuming `proposal.attachment` contains the file path of the attachment
    # attachment_path = proposal.attachment.path if proposal.attachment else ''

    # if attachment_path:
    #     # Create a PdfFileMerger object
    #     merger = PdfMerger()

    #     # Add the existing PDF file to the merger
    #     merger.append(filename)

    #     # Add the attachment page to the merger
    #     merger.append(attachment_path)

    #     # Save the merged PDF file
    #     merger.write(filename)

    return FileResponse(open(filename, 'rb'), content_type='application/pdf')


@login_required(login_url='/login/')
@role_required(allowed_roles='BUDGET-RELEASE')
def budget_release_approve(request, _id):
    release = BudgetRelease.objects.get(
        budget_id=_id, budget_approval_id=request.user.user_id)
    release.budget_approval_status = 'Y'
    release.budget_approval_date = timezone.now()
    release.save()
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT budget_id, MAX(sequence) AS seq FROM apps_budgetrelease GROUP BY budget_id HAVING budget_id = '" + str(_id) + "'")
        max_seq = cursor.fetchall()

    budget = Budget.objects.get(budget_id=_id)
    if release.sequence == max_seq[0][1]:
        budget.budget_status = 'OPEN'
    else:
        budget.budget_status = 'IN APPROVAL'

        email = BudgetRelease.objects.filter(budget_id=_id, budget_approval_status='N').order_by(
            'sequence').values_list('budget_approval_email', flat=True)
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT budget_approval_name FROM apps_budgetrelease WHERE budget_id = '" + str(_id) + "' AND budget_approval_status = 'N' ORDER BY sequence LIMIT 1")
            approver = cursor.fetchone()

        subject = 'Budget Approval'
        message = 'Dear ' + approver[0] + ',\n\nYou have a budget to approve. Please check your dashboard.\n\n' + \
            'Click this link to approve, revise or return the budget.\n' + host.url + 'budget_release/view/' + str(_id) + '/NONE/0/' + \
            '\n\nThank you.'
        send_email(subject, message, [email[0]])

    budget.save()

    return HttpResponseRedirect(reverse('budget-release-index'))


@login_required(login_url='/login/')
@role_required(allowed_roles='PROPOSAL-RELEASE')
def proposal_release_approve(request, _id):
    proposal = Proposal.objects.get(proposal_id=_id)
    release = ProposalRelease.objects.get(
        proposal_id=_id, proposal_approval_id=request.user.user_id)
    release.proposal_approval_status = 'Y'
    release.proposal_approval_date = timezone.now()
    release.save()
    highest_approval = ProposalRelease.objects.filter(
        proposal_id=_id, limit__gt=proposal.total_cost).aggregate(Min('sequence')) if ProposalRelease.objects.filter(proposal_id=_id, limit__gt=proposal.total_cost).exists() else ProposalRelease.objects.filter(proposal_id=_id).aggregate(Max('sequence'))
    highest_sequence = highest_approval.get('sequence__min') if highest_approval.get(
        'sequence__min') else highest_approval.get('sequence__max') + 1
    if highest_sequence:
        approval = ProposalRelease.objects.filter(
            proposal_id=_id, sequence__lt=highest_sequence).order_by('sequence').last()
    else:
        approval = ProposalRelease.objects.filter(
            proposal_id=_id).order_by('sequence').last()

    if release.sequence == approval.sequence:
        proposal.status = 'OPEN'
        proposal.save()

        recipients = []

        maker = proposal.entry_by
        maker_mail = User.objects.get(user_id=maker).email
        recipients.append(maker_mail)

        approvers = ProposalRelease.objects.filter(
            proposal_id=_id, notif=True, proposal_approval_status='Y')
        for i in approvers:
            recipients.append(i.proposal_approval_email)

        subject = 'Proposal Approved'
        msg = 'Dear All,\n\nProposal No. ' + str(_id) + ' has been approved.\n\nClick the following link to view the proposal.\n' + host.url + 'proposal/view/open/' + str(_id) + '/0/0/0/' + \
            '\n\nThank you.'
        recipient_list = list(dict.fromkeys(recipients))
        send_email(subject, msg, recipient_list)
    else:
        proposal.status = 'IN APPROVAL'
        proposal.save()

        email = ProposalRelease.objects.filter(proposal_id=_id, proposal_approval_status='N').order_by(
            'sequence').values_list('proposal_approval_email', flat=True)
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT proposal_approval_name FROM apps_proposalrelease WHERE proposal_id = '" + str(_id) + "' AND proposal_approval_status = 'N' ORDER BY sequence LIMIT 1")
            approver = cursor.fetchone()

        subject = 'Proposal Approval'
        msg = 'Dear ' + approver[0] + ',\n\nYou have a new proposal to approve. Please check your proposal release list.\n\n' + \
            'Click this link to approve, revise, return or reject this proposal.\n' + host.url + 'proposal_release/view/' + str(_id) + '/0/0/0/0/' + \
            '\n\nThank you.'
        send_email(subject, msg, [email[0]])

    return HttpResponseRedirect(reverse('proposal-release-index'))


@login_required(login_url='/login/')
@role_required(allowed_roles='BUDGET-RELEASE')
def budget_release_return(request, _id):
    recipients = []

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT budget_id, email FROM apps_budget INNER JOIN apps_user ON apps_budget.entry_by = apps_user.user_id WHERE budget_id = '" + str(_id) + "'")
        entry_mail = cursor.fetchone()
        recipients.append(entry_mail[1])

        cursor.execute(
            "SELECT budget_id, email FROM apps_budget INNER JOIN apps_user ON apps_budget.update_by = apps_user.user_id WHERE budget_id = '" + str(_id) + "'")
        update_mail = cursor.fetchone()
        recipients.append(update_mail[1])

        cursor.execute(
            "SELECT budget_id, email FROM apps_budgetdetail INNER JOIN apps_user ON apps_budgetdetail.update_by = apps_user.user_id WHERE budget_id = '" + str(_id) + "'")
        detail_mail = cursor.fetchone()
        recipients.append(detail_mail[1])

        cursor.execute(
            "SELECT budget_id, budget_approval_email FROM apps_budgetrelease WHERE budget_id = '" + str(_id) + "' AND budget_approval_status = 'Y'")
        approver_mail = cursor.fetchone()
        if approver_mail:
            recipients.append(approver_mail[1])

    try:
        release = BudgetRelease.objects.filter(
            budget_id=_id, budget_approval_status='Y')
        for i in release:
            i.budget_approval_status = 'N'
            i.budget_approval_date = None
            i.upping_note = ''
            i.percentage_note = ''
            i.save()
    except BudgetRelease.DoesNotExist:
        pass

    note = BudgetRelease.objects.get(
        budget_id=_id, budget_approval_id=request.user.user_id)
    note.return_note = request.POST.get('return_note')
    note.save()

    budget = Budget.objects.get(budget_id=_id)
    budget.budget_status = 'DRAFT'
    budget.save()

    subject = 'Budget Returned'
    message = 'Dear All,\n\nBudget No. ' + str(_id) + ' has been returned.\n\nNote: ' + \
        str(note.return_note) + '\n\nClick the following link to revise the budget.\n' + host.url + 'budget/view/draft/' + \
        str(_id) + '/NONE/' + \
        '\n\nThank you.'
    recipient_list = list(dict.fromkeys(recipients))
    send_email(subject, message, recipient_list)

    return HttpResponseRedirect(reverse('budget-release-index'))


@login_required(login_url='/login/')
@role_required(allowed_roles='PROPOSAL-RELEASE')
def proposal_release_return(request, _id):
    recipients = []
    draft = False

    try:
        return_to = ProposalRelease.objects.get(
            proposal_id=_id, return_to=True, sequence__lt=ProposalRelease.objects.get(proposal_id=_id, proposal_approval_id=request.user.user_id).sequence)

        if return_to:
            approvers = ProposalRelease.objects.filter(
                proposal_id=_id, sequence__gte=ProposalRelease.objects.get(proposal_id=_id, return_to=True).sequence, sequence__lt=ProposalRelease.objects.get(proposal_id=_id, proposal_approval_id=request.user.user_id).sequence)
    except ProposalRelease.DoesNotExist:
        approvers = ProposalRelease.objects.filter(
            proposal_id=_id, sequence__lte=ProposalRelease.objects.get(proposal_id=_id, proposal_approval_id=request.user.user_id).sequence)
        draft = True

    for i in approvers:
        recipients.append(i.proposal_approval_email)
        i.proposal_approval_status = 'N'
        i.proposal_approval_date = None
        i.revise_note = ''
        i.return_note = ''
        i.reject_note = ''
        i.mail_sent = False
        i.save()

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT proposal_id, email FROM apps_proposal INNER JOIN apps_user ON apps_proposal.entry_by = apps_user.user_id WHERE proposal_id = '" + str(_id) + "'")
        entry_mail = cursor.fetchone()
        if entry_mail:
            recipients.append(entry_mail[1])

        cursor.execute(
            "SELECT proposal_id, email FROM apps_proposal INNER JOIN apps_user ON apps_proposal.update_by = apps_user.user_id WHERE proposal_id = '" + str(_id) + "'")
        update_mail = cursor.fetchone()
        if update_mail:
            recipients.append(update_mail[1])

        cursor.execute(
            "SELECT proposal_id, email FROM apps_incrementalsales INNER JOIN apps_user ON apps_incrementalsales.update_by = apps_user.user_id WHERE proposal_id = '" + str(_id) + "'")
        incremental_mail = cursor.fetchone()
        if incremental_mail:
            recipients.append(incremental_mail[1])

        cursor.execute(
            "SELECT proposal_id, email FROM apps_projectedcost INNER JOIN apps_user ON apps_projectedcost.update_by = apps_user.user_id WHERE proposal_id = '" + str(_id) + "'")
        cost_mail = cursor.fetchone()
        if cost_mail:
            recipients.append(cost_mail[1])

    note = ProposalRelease.objects.get(
        proposal_id=_id, proposal_approval_id=request.user.user_id)
    note.return_note = request.POST.get('return_note')
    note.save()

    subject = 'Proposal Returned'
    msg = 'Dear All,\n\nProposal No. ' + str(_id) + ' has been returned.\n\nNote: ' + \
        str(note.return_note) + \
        '\n\nClick the following link to revise the proposal.\n'

    if draft:
        proposal = Proposal.objects.get(proposal_id=_id)
        proposal.status = 'DRAFT'
        proposal.save()
        msg += host.url + 'proposal/view/draft/' + str(_id) + '/0/0/0/' + \
            '\n\nThank you.'
    else:
        msg += host.url + 'proposal_release/view/' + \
            str(_id) + '/0/0/0/0/\n\nThank you.'
    recipient_list = list(dict.fromkeys(recipients))
    send_email(subject, msg, recipient_list)

    return HttpResponseRedirect(reverse('proposal-release-index'))


@login_required(login_url='/login/')
@role_required(allowed_roles='PROPOSAL-RELEASE')
def proposal_release_reject(request, _id):
    recipients = []

    try:
        approvers = ProposalRelease.objects.filter(
            proposal_id=_id, sequence__lt=ProposalRelease.objects.get(proposal_id=_id, proposal_approval_id=request.user.user_id).sequence)
    except ProposalRelease.DoesNotExist:
        pass

    for i in approvers:
        recipients.append(i.proposal_approval_email)

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT proposal_id, email FROM apps_proposal INNER JOIN apps_user ON apps_proposal.entry_by = apps_user.user_id WHERE proposal_id = '" + str(_id) + "'")
        entry_mail = cursor.fetchone()
        if entry_mail:
            recipients.append(entry_mail[1])

        cursor.execute(
            "SELECT proposal_id, email FROM apps_proposal INNER JOIN apps_user ON apps_proposal.update_by = apps_user.user_id WHERE proposal_id = '" + str(_id) + "'")
        update_mail = cursor.fetchone()
        if update_mail:
            recipients.append(update_mail[1])

        cursor.execute(
            "SELECT proposal_id, email FROM apps_incrementalsales INNER JOIN apps_user ON apps_incrementalsales.update_by = apps_user.user_id WHERE proposal_id = '" + str(_id) + "'")
        incremental_mail = cursor.fetchone()
        if incremental_mail:
            recipients.append(incremental_mail[1])

        cursor.execute(
            "SELECT proposal_id, email FROM apps_projectedcost INNER JOIN apps_user ON apps_projectedcost.update_by = apps_user.user_id WHERE proposal_id = '" + str(_id) + "'")
        cost_mail = cursor.fetchone()
        if cost_mail:
            recipients.append(cost_mail[1])

    note = ProposalRelease.objects.get(
        proposal_id=_id, proposal_approval_id=request.user.user_id)
    note.reject_note = request.POST.get('reject_note')
    note.save()

    subject = 'Proposal Rejected'
    msg = 'Dear All,\n\nProposal No. ' + str(_id) + ' has been rejected.\n\nNote: ' + \
        str(note.reject_note) + \
        '\n\nClick the following link to see the proposal.\n'

    proposal = Proposal.objects.get(proposal_id=_id)
    proposal.status = 'REJECTED'
    proposal.save()
    sum_cost = Proposal.objects.filter(budget=proposal.budget, channel=proposal.channel).exclude(status__in=['REJECTED']).aggregate(Sum('total_cost'))[
        'total_cost__sum'] if Proposal.objects.filter(budget=proposal.budget, channel=proposal.channel).exclude(status__in=['REJECTED']).exists() else 0
    budget_detail = BudgetDetail.objects.get(
        budget=proposal.budget, budget_channel=proposal.channel)
    budget_detail.budget_proposed = sum_cost
    budget_detail.save()
    sum_balance = BudgetDetail.objects.filter(budget=proposal.budget).aggregate(Sum('budget_balance'))[
        'budget_balance__sum'] if BudgetDetail.objects.filter(budget=proposal.budget).exists() else 0
    budget = Budget.objects.get(budget_id=proposal.budget)
    budget.budget_balance = sum_balance
    budget.save()

    msg += host.url + 'proposal/view/reject/' + str(_id) + '/0/0/0/' + \
        '\n\nThank you.'
    recipient_list = list(dict.fromkeys(recipients))
    send_email(subject, msg, recipient_list)

    return HttpResponseRedirect(reverse('proposal-release-index'))


@login_required(login_url='/login/')
@role_required(allowed_roles='BUDGET-APPROVAL')
def budget_approval_index(request):
    areas = AreaSales.objects.all()

    context = {
        'data': areas,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'budget_approval',
        'group_segment': 'approval',
        'crud': 'index',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='BUDGET-APPROVAL') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/budget_approval_index.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='PROPOSAL-APPROVAL')
def proposal_matrix_index(request):
    areas = AreaSales.objects.all()

    context = {
        'data': areas,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'proposal_matrix',
        'group_segment': 'approval',
        'crud': 'index',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='PROPOSAL-APPROVAL') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/proposal_matrix_index.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='BUDGET-APPROVAL')
def budget_approval_view(request, _id):
    area = AreaSales.objects.get(area_id=_id)
    approvers = BudgetApproval.objects.filter(area_id=_id)
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT user_id, username, position_name, q_budgetapprover.approver_id FROM apps_user INNER JOIN apps_position ON apps_user.position_id = apps_position.position_id LEFT JOIN (SELECT * FROM apps_budgetapproval WHERE area_id = '" + str(_id) + "') AS q_budgetapprover ON apps_user.user_id = q_budgetapprover.approver_id WHERE q_budgetapprover.approver_id IS NULL")
        users = cursor.fetchall()

    if request.POST:
        check = request.POST.getlist('checks[]')
        for i in users:
            if str(i[0]) in check:
                try:
                    approver = BudgetApproval(area_id=_id, approver_id=i[0])
                    approver.save()
                except IntegrityError:
                    continue
            else:
                BudgetApproval.objects.filter(
                    area_id=_id, approver_id=i[0]).delete()

        return HttpResponseRedirect(reverse('budget-approval-view', args=[_id, ]))

    context = {
        'data': area,
        'users': users,
        'approvers': approvers,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'budget_approval',
        'group_segment': 'approval',
        'tab': 'auth',
        'crud': 'view',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='BUDGET-APPROVAL') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/budget_approval_view.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='PROPOSAL-APPROVAL')
def proposal_matrix_view(request, _id, _channel):
    area = AreaSales.objects.get(area_id=_id)
    channels = AreaChannelDetail.objects.filter(area_id=_id, status=1)
    approvers = ProposalMatrix.objects.filter(area_id=_id, channel_id=_channel)
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT user_id, username, position_name, q_proposalmatrix.approver_id FROM apps_user INNER JOIN apps_position ON apps_user.position_id = apps_position.position_id LEFT JOIN (SELECT * FROM apps_proposalmatrix WHERE area_id = '" + str(_id) + "' AND channel_id = '" + str(_channel) + "') AS q_proposalmatrix ON apps_user.user_id = q_proposalmatrix.approver_id WHERE q_proposalmatrix.approver_id IS NULL")
        users = cursor.fetchall()

    if request.POST:
        check = request.POST.getlist('checks[]')
        for i in users:
            if str(i[0]) in check:
                try:
                    approver = ProposalMatrix(
                        area_id=_id, channel_id=_channel, approver_id=i[0])
                    approver.save()
                except IntegrityError:
                    continue
            else:
                ProposalMatrix.objects.filter(
                    area_id=_id, channel_id=_channel, approver_id=i[0]).delete()

        return HttpResponseRedirect(reverse('proposal-matrix-view', args=[_id, _channel]))

    context = {
        'data': area,
        'channels': channels,
        'users': users,
        'approvers': approvers,
        'channel': _channel,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'proposal_matrix',
        'group_segment': 'approval',
        'tab': 'auth',
        'crud': 'view',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='PROPOSAL-APPROVAL') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/proposal_matrix_view.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='BUDGET-APPROVAL')
def budget_approval_update(request, _id, _approver):
    approvers = BudgetApproval.objects.get(area=_id, approver_id=_approver)

    if request.POST:
        approvers.sequence = int(request.POST.get('sequence'))
        approvers.save()

        return HttpResponseRedirect(reverse('budget-approval-view', args=[_id, ]))

    return render(request, 'home/budget_approval_view.html')


@login_required(login_url='/login/')
@role_required(allowed_roles='PROPOSAL-APPROVAL')
def proposal_matrix_update(request, _id, _channel, _approver):
    approvers = ProposalMatrix.objects.get(
        area=_id, channel_id=_channel, approver_id=_approver)

    if request.POST:
        approvers.sequence = int(request.POST.get('sequence'))
        approvers.limit = int(request.POST.get('limit'))
        approvers.return_to = True if request.POST.get('return') else False
        approvers.approve = True if request.POST.get('approve') else False
        approvers.revise = True if request.POST.get('revise') else False
        approvers.returned = True if request.POST.get('returned') else False
        approvers.reject = True if request.POST.get('reject') else False
        approvers.notif = True if request.POST.get('notif') else False
        approvers.printed = True if request.POST.get('printed') else False
        approvers.as_approved = request.POST.get('as_approved')
        approvers.save()

        return HttpResponseRedirect(reverse('proposal-matrix-view', args=[_id, _channel]))

    return render(request, 'home/proposal_matrix_view.html')


@login_required(login_url='/login/')
@role_required(allowed_roles='BUDGET-APPROVAL')
def budget_approval_delete(request, _id, _arg):
    approvers = BudgetApproval.objects.get(area=_id, approver_id=_arg)
    approvers.delete()

    return HttpResponseRedirect(reverse('budget-approval-view', args=[_id, ]))


@login_required(login_url='/login/')
@role_required(allowed_roles='PROPOSAL-APPROVAL')
def proposal_matrix_delete(request, _id, _channel, _arg):
    approvers = ProposalMatrix.objects.get(
        area=_id, channel_id=_channel, approver_id=_arg)
    approvers.delete()

    return HttpResponseRedirect(reverse('proposal-matrix-view', args=[_id, _channel]))


@login_required(login_url='/login/')
@role_required(allowed_roles='CLOSING-PERIOD')
def closing_index(request):
    periods = Closing.objects.all()

    context = {
        'data': periods,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'closing_period',
        'group_segment': 'master',
        'crud': 'index',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id,
                                menu_id='CLOSING-PERIOD') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/closing_index.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='CLOSING-PERIOD')
def closing_add(request):
    if request.POST:
        form = FormClosing(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('closing-index'))
    else:
        last_month = (datetime.datetime(datetime.datetime.now(
        ).year, datetime.datetime.now().month, 1) - datetime.timedelta(days=1)).month
        last_year = (datetime.datetime(datetime.datetime.now(
        ).year, datetime.datetime.now().month, 1) - datetime.timedelta(days=1)).year

        form = FormClosing(initial={'year_closed': last_year, 'month_closed': last_month,
                           'year_open': datetime.datetime.now().year, 'month_open': datetime.datetime.now().month})

    context = {
        'form': form,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'closing_period',
        'group_segment': 'master',
        'crud': 'add',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id,
                                menu_id='CLOSING-PERIOD') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/closing_add.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='CLOSING-PERIOD')
def closing_update(request, _id):
    period = Closing.objects.get(document=_id)

    if request.POST:
        form = FormClosingUpdate(request.POST, request.FILES, instance=period)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('closing-view', args=[_id, ]))
    else:
        form = FormClosingUpdate(instance=period)

    YEAR_CHOICES = []
    for r in range((datetime.datetime.now().year-1), (datetime.datetime.now().year+2)):
        YEAR_CHOICES.append(str(r))

    MONTH_CHOICES = []
    for r in range(1, 13):
        MONTH_CHOICES.append(str(r))

    context = {
        'form': form,
        'data': period,
        'years': YEAR_CHOICES,
        'months': MONTH_CHOICES,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'closing_period',
        'group_segment': 'master',
        'crud': 'update',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id,
                                menu_id='CLOSING-PERIOD') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/closing_view.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='CLOSING-PERIOD')
def closing_delete(request, _id):
    periods = Closing.objects.get(document=_id)
    periods.delete()

    return HttpResponseRedirect(reverse('closing-index'))


@login_required(login_url='/login/')
@role_required(allowed_roles='CLOSING-PERIOD')
def closing_view(request, _id):
    period = Closing.objects.get(document=_id)
    form = FormClosingView(instance=period)

    YEAR_CHOICES = []
    for r in range((datetime.datetime.now().year-1), (datetime.datetime.now().year+2)):
        YEAR_CHOICES.append(str(r))

    MONTH_CHOICES = []
    for r in range(1, 13):
        MONTH_CHOICES.append(str(r))

    context = {
        'data': period,
        'form': form,
        'years': YEAR_CHOICES,
        'months': MONTH_CHOICES,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'closing_period',
        'group_segment': 'master',
        'crud': 'view',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id,
                                menu_id='CLOSING-PERIOD') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/closing_view.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='BUDGET-CLOSING')
def closing(request):
    message = '0'
    period = None
    try:
        period = Closing.objects.get(document='BUDGET')
    except Closing.DoesNotExist:
        message = 'Document Budget not found, add document Budget Closing Period first.'
    budgets = Budget.objects.filter(budget_status='OPEN')
    not_approved_budget = Budget.objects.filter(
        budget_status__in=['IN APPROVAL', 'DRAFT'])
    proposals = Proposal.objects.filter(status__in=['NONE'])

    if request.POST:
        if not_approved_budget:
            message = 'There are still budgets in draft or approval process. Please approve, reject or cancel them first.'
        else:
            if proposals:
                message = 'There are still proposals in draft or approval process. Please approve, reject or cancel them first.'
            else:
                if request.user.is_superuser:
                    period.year_closed = request.POST.get('year_closed')
                    period.month_closed = request.POST.get('month_closed')
                else:
                    period.year_closed = period.year_open
                    period.month_closed = period.month_open
                next_month = (datetime.datetime(int(period.year_closed),
                                                int(period.month_closed), 1) + datetime.timedelta(days=32)).month
                next_year = (datetime.datetime(int(period.year_closed),
                                               int(period.month_closed), 1) + datetime.timedelta(days=32)).year
                period.year_open = next_year
                period.month_open = next_month
                period.save()
                for budget in budgets:
                    detail = BudgetDetail.objects.filter(
                        budget_id=budget.budget_id)
                    total_amount = 0
                    for i in detail:
                        total_amount += i.budget_balance

                    new_budget = Budget(
                        budget_year=str(next_year),
                        budget_month='{:02d}'.format(next_month),
                        budget_area=budget.budget_area,
                        budget_distributor=budget.budget_distributor,
                        budget_amount=total_amount,
                        budget_upping=0,
                        budget_balance=total_amount,
                        budget_status='DRAFT')
                    new_budget.save()

                    for i in detail:
                        new_detail = BudgetDetail(
                            budget_id=new_budget.budget_id,
                            budget_channel=i.budget_channel,
                            budget_amount=i.budget_balance)
                        new_detail.save()

                    approvers = BudgetApproval.objects.filter(
                        area_id=new_budget.budget_area).order_by('sequence')
                    for approver in approvers:
                        new_release = BudgetRelease(
                            budget_id=new_budget.budget_id,
                            budget_approval_id=approver.approver_id,
                            budget_approval_name=approver.approver.username,
                            budget_approval_email=approver.approver.email,
                            budget_approval_position=approver.approver.position.position_name,
                            sequence=approver.sequence)
                        new_release.save()

                    budget.budget_status = 'CLOSED'
                    budget.save()

                context = {
                    'data': period,
                    'month': period.month_closed,
                    'year': period.year_closed,
                    'next_month': next_month,
                    'next_year': next_year,
                    'total': budgets.count(),
                    'budget_notif': budget_notification(request),
                    'proposal_notif': proposal_notification(request),
                    'program_notif': program_notification(request),
                    'claim_notif': claim_notification(request),
                    'cl_notif': cl_notification(request),
                    'segment': 'budget_closing',
                    'group_segment': 'budget',
                    'crud': 'index',
                    'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
                    'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='BUDGET-CLOSING') if not request.user.is_superuser else Auth.objects.all(),
                }
                return render(request, 'home/budget_closingreport.html', context)

    YEAR_CHOICES = []
    for r in range((datetime.datetime.now().year-1), (datetime.datetime.now().year+2)):
        YEAR_CHOICES.append(str(r))

    MONTH_CHOICES = []
    for r in range(1, 13):
        MONTH_CHOICES.append(str(r))

    context = {
        'data': period,
        'message': message,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'budget_closing',
        'years': YEAR_CHOICES,
        'months': MONTH_CHOICES,
        'group_segment': 'budget',
        'crud': 'index',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='BUDGET-CLOSING') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/closing.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='DIVISION')
def division_index(request):
    divisions = Division.objects.all()

    context = {
        'data': divisions,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'division',
        'group_segment': 'master',
        'crud': 'index',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list(
            'menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id,
                                menu_id='DIVISION') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/division_index.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='DIVISION')
def division_add(request):
    if request.POST:
        form = FormDivision(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('division-index'))
    else:
        form = FormDivision()

    context = {
        'form': form,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'division',
        'group_segment': 'master',
        'crud': 'add',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list(
            'menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id,
                                menu_id='DIVISION') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/division_add.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='DIVISION')
def division_update(request, _id):
    division = Division.objects.get(division_id=_id)

    if request.POST:
        form = FormDivisionUpdate(
            request.POST, request.FILES, instance=division)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('division-index'))
    else:
        form = FormDivisionUpdate(instance=division)

    context = {
        'form': form,
        'data': division,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'division',
        'group_segment': 'master',
        'crud': 'update',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list(
            'menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id,
                                menu_id='DIVISION') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/division_view.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='DIVISION')
def division_delete(request, _id):
    division = Division.objects.get(division_id=_id)
    division.delete()

    return HttpResponseRedirect(reverse('division-index'))


@login_required(login_url='/login/')
@role_required(allowed_roles='DIVISION')
def division_view(request, _id):
    division = Division.objects.get(division_id=_id)
    form = FormDivisionView(instance=division)

    context = {
        'data': division,
        'form': form,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'division',
        'group_segment': 'master',
        'crud': 'view',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list(
            'menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id,
                                menu_id='DIVISION') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/division_view.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='PROPOSAL')
def proposal_index(request, _tab):
    drafts = Proposal.objects.filter(status='DRAFT', area__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-proposal_id').all
    draft_count = Proposal.objects.filter(status='DRAFT', area__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-proposal_id').count
    inapprovals = Proposal.objects.filter(status='IN APPROVAL', area__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-proposal_id').values_list('proposal_id', 'proposal_date', 'channel', 'total_cost', 'proposal_claim', 'balance', 'reference', ProposalRelease.objects.filter(proposal_id=OuterRef('proposal_id'), proposal_approval_status='N').order_by('sequence').values('proposal_approval_name')[:1])
    inapproval_count = Proposal.objects.filter(status='IN APPROVAL', area__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-proposal_id').count
    opens = Proposal.objects.filter(status='OPEN', area__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-proposal_id').all
    open_count = Proposal.objects.filter(status='OPEN', area__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-proposal_id').count

    context = {
        'drafts': drafts,
        'draft_count': draft_count,
        'inapprovals': inapprovals,
        'inapproval_count': inapproval_count,
        'opens': opens,
        'open_count': open_count,
        'tab': _tab,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'proposal',
        'group_segment': 'proposal',
        'crud': 'index',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list(
            'menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id,
                                menu_id='PROPOSAL') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/proposal_index.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='PROPOSAL-ARCHIVE')
def proposal_archive_index(request, _tab):
    closes = Proposal.objects.filter(status='CLOSED', area__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-proposal_id').all
    close_count = Proposal.objects.filter(status='CLOSED', area__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-proposal_id').count
    rejects = Proposal.objects.filter(status='REJECTED', area__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-proposal_id').all
    reject_count = Proposal.objects.filter(status='REJECTED', area__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-proposal_id').count

    context = {
        'closes': closes,
        'close_count': close_count,
        'rejects': rejects,
        'reject_count': reject_count,
        'tab': _tab,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'proposal_archive',
        'group_segment': 'proposal',
        'crud': 'index',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list(
            'menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id,
                                menu_id='PROPOSAL-ARCHIVE') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/proposal_archive.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='PROPOSAL')
def proposal_add(request, _area, _budget, _channel):
    selected_area = _area
    selected_budget = _budget
    selected_channel = _channel
    area = AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', 'area__area_name')
    name = AreaSales.objects.get(
        area_id=selected_area) if selected_area != '0' else None
    divs = Division.objects.all()
    budgets = Budget.objects.filter(budget_balance__gt=0, budget_status__in=['OPEN', 'DRAFT', 'IN APPROVAL'], budget_area=selected_area).exclude(
        budget_status='DRAFT', budget_new=True) if selected_area != '0' else None
    budget_detail = BudgetDetail.objects.filter(budget_id=selected_budget).annotate(
        draft_balance=F('budget_amount') + F('budget_transfer_plus') -
        F('budget_transfer_minus') -
        F('budget_proposed') + F('budget_remaining'),
        status=F('budget__budget_status')) if selected_budget != '0' else None
    distributor = Budget.objects.get(
        budget_id=selected_budget).budget_distributor_id if selected_budget != '0' else None
    refs = Proposal.objects.filter(status='OPEN', area=selected_area, budget__budget_distributor_id=distributor,
                                   channel=selected_channel).order_by('-proposal_date')

    message = ''
    no_save = False
    if selected_area != '0' and selected_channel != '0':
        approvers = ProposalMatrix.objects.filter(
            area_id=_area, channel_id=_channel).order_by('sequence')
        if approvers.count() == 0 or approvers[0].limit > 0:
            message = "No proposal's approver found for this area and channel."
            no_save = True

    try:
        _no = Proposal.objects.filter(
            proposal_date__year=datetime.datetime.now().year).latest('seq_number')
    except Proposal.DoesNotExist:
        _no = None
    if _no is None:
        format_no = '{:04d}'.format(1)
    else:
        format_no = '{:04d}'.format(_no.seq_number + 1)

    _id = 'PBS-2' + format_no + '/' + selected_channel + '/' + selected_area + '/' + \
        str(distributor) + '/' + \
        str(datetime.datetime.now().strftime('%m')) + \
        '/' + str(datetime.datetime.now().year)

    if request.method == 'POST':
        form = FormProposal(request.POST, request.FILES)
        if form.is_valid():
            parent = form.save(commit=False)
            parent.duration = form.cleaned_data['period_end'] - \
                form.cleaned_data['period_start']
            if parent.duration.days < 0:
                message = 'Period end must be greater than period start.'
            else:
                parent.budget_id = selected_budget
                parent.channel = selected_channel
                parent.reference = request.POST.get('reference')
                parent.status = 'DRAFT'
                parent.seq_number = _no.seq_number + 1 if _no else 1
                parent.entry_pos = request.user.position.position_id
                parent.save()

                for approver in approvers:
                    release = ProposalRelease(
                        proposal_id=parent.proposal_id,
                        proposal_approval_id=approver.approver_id,
                        proposal_approval_name=approver.approver.username,
                        proposal_approval_email=approver.approver.email,
                        proposal_approval_position=approver.approver.position.position_id,
                        sequence=approver.sequence,
                        limit=approver.limit,
                        return_to=approver.return_to,
                        approve=approver.approve,
                        revise=approver.revise,
                        returned=approver.returned,
                        reject=approver.reject,
                        notif=approver.notif,
                        printed=approver.printed,
                        as_approved=approver.as_approved)
                    release.save()

                return HttpResponseRedirect(reverse('proposal-view', args=['draft', parent.proposal_id, '0', '0', '0']))
    else:
        form = FormProposal(
            initial={'proposal_id': _id, 'area': selected_area, 'period_start': datetime.datetime.now().date(), 'period_end': datetime.datetime.now().date()})

    msg = form.errors
    context = {
        'form': form,
        'area': area,
        'name': name,
        'divs': divs,
        'budgets': budgets,
        'budget_detail': budget_detail,
        'selected_area': selected_area,
        'selected_budget': selected_budget,
        'selected_channel': selected_channel,
        'refs': refs,
        'msg': msg,
        'message': message,
        'no_save': no_save,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'proposal',
        'group_segment': 'proposal',
        'crud': 'add',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list(
            'menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id,
                                menu_id='PROPOSAL') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/proposal_add.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='PROPOSAL')
def proposal_view(request, _tab, _id, _sub_id, _act, _msg):
    proposal = Proposal.objects.get(proposal_id=_id)
    budget = BudgetDetail.objects.get(
        budget=proposal.budget, budget_channel=proposal.channel)
    available = budget.budget_amount + budget.budget_transfer_plus - \
        budget.budget_transfer_minus - budget.budget_proposed + budget.budget_remaining
    form = FormProposalView(instance=proposal)
    divs = Division.objects.all()
    refs = Proposal.objects.filter(status='OPEN', area=proposal.area, budget__budget_distributor_id=budget.budget.budget_distributor_id,
                                   channel=proposal.channel).order_by('-proposal_date')
    form_attachment = FormProposalAttachment()
    attachment = ProposalAttachment.objects.filter(proposal_id=_id)
    form_incremental = FormIncrementalSales()
    incremental = IncrementalSales.objects.filter(proposal_id=_id)
    total = IncrementalSales.objects.filter(proposal_id=_id).aggregate(
        swop_carton__sum=Sum('swop_carton'),
        swop_nom__sum=Sum('swop_nom'),
        swp_carton__sum=Sum('swp_carton'),
        swp_nom__sum=Sum('swp_nom'),
        incrp_carton__sum=Sum('incrp_carton'),
        incrp_nom__sum=Sum('incrp_nom'),
    )
    incpst_carton = (total['incrp_carton__sum'] / total['swop_carton__sum']
                     ) * 100 if total['swop_carton__sum'] else 0
    incpst_nom = (total['incrp_nom__sum'] / total['swop_nom__sum']
                  ) * 100 if total['swop_nom__sum'] else 0
    form_cost = FormProjectedCost()
    cost = ProjectedCost.objects.filter(proposal_id=_id)
    total_cost = ProjectedCost.objects.filter(
        proposal_id=_id).aggregate(Sum('cost'))
    add_cost = True if budget.budget_balance > 0 else False
    period = Closing.objects.get(document='BUDGET')
    diff_period = False

    if proposal.budget.budget_month != '{:02d}'.format(int(period.month_open)) or proposal.budget.budget_year != period.year_open:
        diff_period = True

    highest_approval = ProposalRelease.objects.filter(
        proposal_id=_id, limit__gt=proposal.total_cost).aggregate(Min('sequence')) if ProposalRelease.objects.filter(proposal_id=_id, limit__gt=proposal.total_cost).exists() else ProposalRelease.objects.filter(proposal_id=_id).aggregate(Max('sequence'))
    highest_sequence = highest_approval.get('sequence__min') if highest_approval.get(
        'sequence__min') else highest_approval.get('sequence__max') + 1
    if highest_sequence:
        approval = ProposalRelease.objects.filter(
            proposal_id=_id, sequence__lt=highest_sequence).order_by('sequence')
    else:
        approval = ProposalRelease.objects.filter(
            proposal_id=_id).order_by('sequence')
    rejector = ProposalRelease.objects.filter(
        proposal_id=_id, proposal_approval_status='N').order_by('sequence').first() if proposal.status == 'REJECTED' else None

    if _tab in ['closed', 'reject']:
        segment = 'proposal_archive'
    elif _tab in ['closing']:
        segment = 'proposal_closing'
    else:
        segment = 'proposal'

    context = {
        'data': proposal,
        'budget': budget,
        'available': available,
        'form': form,
        'divs': divs,
        'refs': refs,
        'formAttachment': form_attachment,
        'attachment': attachment,
        'formInc': form_incremental,
        'incremental': incremental,
        'formCost': form_cost,
        'cost': cost,
        'total': total,
        'incpst_carton': incpst_carton,
        'incpst_nom': incpst_nom,
        'total_inc': total['incrp_nom__sum'] if total['incrp_nom__sum'] else 0,
        'total_cost': total_cost['cost__sum'] if total_cost['cost__sum'] else 0,
        'diff_period': diff_period,
        'tab': _tab,
        'sub_id': _sub_id,
        'action': _act,
        'approval': approval,
        'rejector': rejector,
        'message': _msg,
        'status': proposal.status,
        'add_cost': add_cost,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': segment,
        'group_segment': 'proposal',
        'crud': 'view',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list(
            'menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id,
                                menu_id='PROPOSAL') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/proposal_view.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='PROPOSAL')
def proposal_attachment_add(request, _tab, _id):
    if request.method == 'POST':
        form = FormProposalAttachment(request.POST, request.FILES)
        if form.is_valid():
            attachment = form.save(commit=False)
            attachment.proposal_id = _id
            attachment.save()
            if not settings.DEBUG:
                proposal_attachment = ProposalAttachment.objects.get(
                    id=attachment.id)
                if proposal_attachment.attachment:
                    my_file = proposal_attachment.attachment
                    filename = '../../www/' + host.folder + '/apps/media/' + my_file.name
                    with open(filename, 'wb+') as temp_file:
                        for chunk in my_file.chunks():
                            temp_file.write(chunk)

    if _tab in ['draft', 'pending']:
        return HttpResponseRedirect(reverse('proposal-view', args=[_tab, _id, '0', '0', '0']))
    else:
        return HttpResponseRedirect(reverse('proposal-release-view', args=[_id, '0', '0', '0', 1]))


@login_required(login_url='/login/')
@role_required(allowed_roles='PROPOSAL')
def proposal_incremental_add(request, _tab, _id):
    form = FormIncrementalSales(request.POST, request.FILES)
    proposal = Proposal.objects.get(proposal_id=_id)
    message = '0'
    if form.is_valid():
        try:
            check = IncrementalSales.objects.get(
                proposal_id=_id, product=request.POST.get('product'))
            if check:
                message = 'Product already exist'
        except IncrementalSales.DoesNotExist:
            swop_carton = int(request.POST.get('swop_carton'))
            swp_carton = int(request.POST.get('swp_carton'))
            if swop_carton > swp_carton:
                message = 'Sales With Program must be greater than Sales Without Program'
            else:
                incremental = form.save(commit=False)
                incremental.proposal_id = _id
                incremental.save()
                if incremental.incrp_nom < 0:
                    message = 'Incremental Sales must be greater than 0'
                    incremental.delete()
                else:
                    total_inc = IncrementalSales.objects.filter(proposal_id=_id).aggregate(Sum('incrp_nom'))[
                        'incrp_nom__sum'] if IncrementalSales.objects.filter(proposal_id=_id).exists() else 0
                    total_cost = ProjectedCost.objects.filter(proposal_id=_id).aggregate(Sum('cost'))[
                        'cost__sum'] if ProjectedCost.objects.filter(proposal_id=_id).exists() else 0
                    proposal.roi = (
                        total_cost / total_inc) * 100 if total_inc != 0 else 0
                    proposal.save()

    return HttpResponseRedirect(reverse('proposal-view', args=[_tab, _id, '0', 'add-item', message]))


@login_required(login_url='/login/')
@role_required(allowed_roles='PROPOSAL')
def proposal_cost_add(request, _tab, _id):
    form = FormProjectedCost(request.POST, request.FILES)
    proposal = Proposal.objects.get(proposal_id=_id)
    budget_detail = BudgetDetail.objects.get(
        budget=proposal.budget, budget_channel=proposal.channel)
    available = budget_detail.budget_amount + budget_detail.budget_transfer_plus - \
        budget_detail.budget_transfer_minus - \
        budget_detail.budget_proposed + budget_detail.budget_remaining
    message = '0'
    if form.is_valid():
        try:
            check = ProjectedCost.objects.get(
                proposal_id=_id, activities=request.POST.get('activities'))
            if check:
                message = 'Activity already exist'
        except ProjectedCost.DoesNotExist:
            cost = form.save(commit=False)
            balance = available if budget_detail.budget.budget_status == 'DRAFT' or budget_detail.budget.budget_status == 'IN APPROVAL' else budget_detail.budget_balance
            if cost.cost > balance:
                message = 'Total cost must be less than or equal to budget balance'
            else:
                cost.proposal_id = _id
                cost.save()
                total_inc = IncrementalSales.objects.filter(
                    proposal_id=_id).aggregate(Sum('incrp_nom'))['incrp_nom__sum'] if IncrementalSales.objects.filter(proposal_id=_id).exists() else 0
                total_cost = ProjectedCost.objects.filter(
                    proposal_id=_id).aggregate(Sum('cost'))['cost__sum'] if ProjectedCost.objects.filter(proposal_id=_id).exists() else 0
                proposal.roi = (total_cost / total_inc) * \
                    100 if total_inc != 0 else 0
                proposal.total_cost = total_cost
                proposal.balance = total_cost
                proposal.save()

                sum_cost = Proposal.objects.filter(budget=proposal.budget, channel=proposal.channel).exclude(status__in=['REJECTED']).aggregate(Sum('total_cost'))[
                    'total_cost__sum'] if Proposal.objects.filter(budget=proposal.budget, channel=proposal.channel).exclude(status__in=['REJECTED']).exists() else 0
                budget_detail.budget_proposed = sum_cost
                budget_detail.save()
                sum_balance = BudgetDetail.objects.filter(budget=proposal.budget).aggregate(Sum('budget_balance'))[
                    'budget_balance__sum'] if BudgetDetail.objects.filter(budget=proposal.budget).exists() else 0
                budget = Budget.objects.get(budget_id=proposal.budget)
                budget.budget_balance = sum_balance
                budget.save()

    return HttpResponseRedirect(reverse('proposal-view', args=[_tab, _id, '0', 'add-cost', message]))


@login_required(login_url='/login/')
@role_required(allowed_roles='PROPOSAL')
def proposal_submit(request, _id):
    proposal = Proposal.objects.get(proposal_id=_id)
    budget_detail = BudgetDetail.objects.get(
        budget=proposal.budget, budget_channel=proposal.channel)
    proposal.status = 'IN APPROVAL'
    proposal.save()

    mail_sent = ProposalRelease.objects.filter(
        proposal_id=_id).order_by('sequence').values_list('mail_sent', flat=True)
    if mail_sent[0] == False:
        email = ProposalRelease.objects.filter(
            proposal_id=_id).order_by('sequence').values_list('proposal_approval_email', flat=True)
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT username FROM apps_proposalrelease INNER JOIN apps_user ON apps_proposalrelease.proposal_approval_id = apps_user.user_id WHERE proposal_id = '" + str(_id) + "' AND proposal_approval_status = 'N' ORDER BY sequence LIMIT 1")
            approver = cursor.fetchone()

        subject = 'Proposal Approval'
        msg = 'Dear ' + approver[0] + ',\n\nYou have a new proposal to approve. Please check your proposal release list.\n\n' + \
            'Click this link to approve, revise, return or reject this proposal.\n' + host.url + 'proposal_release/view/' + str(_id) + '/0/0/0/0/' + \
            '\n\nThank you.'
        send_email(subject, msg, [email[0]])

        # update mail sent to true
        release = ProposalRelease.objects.filter(
            proposal_id=_id).order_by('sequence').first()
        release.mail_sent = True
        release.save()

    return HttpResponseRedirect(reverse('proposal-index', args=['inapproval']))


@login_required(login_url='/login/')
@role_required(allowed_roles='PROPOSAL')
def proposal_incremental_delete(request, _tab, _id, _product):
    proposal = Proposal.objects.get(proposal_id=_id)
    incremental = IncrementalSales.objects.get(
        proposal_id=_id, id=_product)
    incremental.delete()
    total_inc = IncrementalSales.objects.filter(
        proposal_id=_id).aggregate(Sum('incrp_nom'))['incrp_nom__sum'] if IncrementalSales.objects.filter(proposal_id=_id).exists() else 0
    total_cost = ProjectedCost.objects.filter(
        proposal_id=_id).aggregate(Sum('cost'))['cost__sum'] if ProjectedCost.objects.filter(proposal_id=_id).exists() else 0
    proposal.roi = (total_cost / total_inc) * \
        100 if total_inc != 0 else 0
    proposal.save()

    return HttpResponseRedirect(reverse('proposal-view', args=[_tab, _id, '0', '0', '0']))


@login_required(login_url='/login/')
@role_required(allowed_roles='PROPOSAL')
def proposal_cost_delete(request, _tab, _id, _activities):
    proposal = Proposal.objects.get(proposal_id=_id)
    budget_detail = BudgetDetail.objects.get(
        budget=proposal.budget, budget_channel=proposal.channel)
    cost = ProjectedCost.objects.get(proposal_id=_id, id=_activities)
    cost.delete()
    total_inc = IncrementalSales.objects.filter(
        proposal_id=_id).aggregate(Sum('incrp_nom'))['incrp_nom__sum'] if IncrementalSales.objects.filter(proposal_id=_id).exists() else 0
    total_cost = ProjectedCost.objects.filter(
        proposal_id=_id).aggregate(Sum('cost'))['cost__sum'] if ProjectedCost.objects.filter(proposal_id=_id).exists() else 0
    proposal.roi = (total_cost / total_inc) * \
        100 if total_inc != 0 else 0
    proposal.total_cost = total_cost
    proposal.balance = total_cost
    proposal.save()

    sum_cost = Proposal.objects.filter(budget=proposal.budget, channel=proposal.channel).exclude(status__in=['REJECTED']).aggregate(Sum('total_cost'))[
        'total_cost__sum'] if Proposal.objects.filter(budget=proposal.budget, channel=proposal.channel).exclude(status__in=['REJECTED']).exists() else 0
    budget_detail.budget_proposed = sum_cost
    budget_detail.save()
    sum_balance = BudgetDetail.objects.filter(budget=proposal.budget).aggregate(Sum('budget_balance'))[
        'budget_balance__sum'] if BudgetDetail.objects.filter(budget=proposal.budget).exists() else 0
    budget = Budget.objects.get(budget_id=proposal.budget)
    budget.budget_balance = sum_balance
    budget.save()

    return HttpResponseRedirect(reverse('proposal-view', args=[_tab, _id, '0', '0', '0']))


@login_required(login_url='/login/')
@role_required(allowed_roles='PROPOSAL')
def remove_attachment(request, _tab, _id):
    attachment = ProposalAttachment.objects.get(id=_id)
    attachment_path = attachment.attachment.path
    attachment.delete()

    # Remove the physical file
    if os.path.exists(attachment_path):
        os.remove(attachment_path)

    if not settings.DEBUG and attachment.attachment:
        my_file = attachment.attachment
        filename = '../../www/' + host.folder + '/apps/media/' + my_file.name
        os.remove(filename)

    return HttpResponseRedirect(reverse('proposal-view', args=[_tab, attachment.proposal_id, '0', '0', '0']))


@login_required(login_url='/login/')
@role_required(allowed_roles='PROPOSAL-RELEASE')
def remove_release_attachment(request, _id):
    attachment = ProposalAttachment.objects.get(id=_id)
    attachment_path = attachment.attachment.path
    attachment.delete()

    # Remove the physical file
    if os.path.exists(attachment_path):
        os.remove(attachment_path)

    if not settings.DEBUG and attachment.attachment:
        my_file = attachment.attachment
        filename = '../../www/' + host.folder + '/apps/media/' + my_file.name
        os.remove(filename)

    return HttpResponseRedirect(reverse('proposal-release-view', args=[attachment.proposal_id, '0', '0', '0', 1]))


@login_required(login_url='/login/')
@role_required(allowed_roles='PROPOSAL')
def proposal_incremental_update(request, _tab, _id, _product):
    proposal = Proposal.objects.get(proposal_id=_id)
    update = IncrementalSales.objects.get(proposal_id=_id, id=_product)
    message = '0'
    if request.POST:
        swop_carton = int(request.POST.get('swop_carton'))
        swp_carton = int(request.POST.get('swp_carton'))
        if swop_carton > swp_carton:
            message = 'Sales With Program must be greater than Sales Without Program'
        else:
            swop_carton = update.swop_carton
            swp_carton = update.swp_carton
            swop_nom = update.swop_nom
            swp_nom = update.swp_nom
            update.swop_carton = int(request.POST.get('swop_carton'))
            update.swp_carton = int(request.POST.get('swp_carton'))
            update.swop_nom = int(request.POST.get('swop_nom'))
            update.swp_nom = int(request.POST.get('swp_nom'))
            update.save()
            if update.incrp_nom < 0:
                message = 'Incremental Sales must be greater than 0'
                update.swop_carton = swop_carton
                update.swp_carton = swp_carton
                update.swop_nom = swop_nom
                update.swp_nom = swp_nom
                update.save()
            else:
                total_inc = IncrementalSales.objects.filter(
                    proposal_id=_id).aggregate(Sum('incrp_nom'))['incrp_nom__sum'] if IncrementalSales.objects.filter(proposal_id=_id).exists() else 0
                total_cost = ProjectedCost.objects.filter(
                    proposal_id=_id).aggregate(Sum('cost'))['cost__sum'] if ProjectedCost.objects.filter(proposal_id=_id).exists() else 0
                proposal.roi = (total_cost / total_inc) * \
                    100 if total_inc != 0 else 0
                proposal.save()

    return HttpResponseRedirect(reverse('proposal-view', args=[_tab, _id, _product, 'upd-item', message]))


@login_required(login_url='/login/')
@role_required(allowed_roles='PROPOSAL')
def proposal_cost_update(request, _tab, _id, _activities):
    proposal = Proposal.objects.get(proposal_id=_id)
    budget_detail = BudgetDetail.objects.get(
        budget=proposal.budget, budget_channel=proposal.channel)
    available = budget_detail.budget_amount + budget_detail.budget_transfer_plus - \
        budget_detail.budget_transfer_minus - \
        budget_detail.budget_proposed + budget_detail.budget_remaining
    update = ProjectedCost.objects.get(
        proposal_id=_id, id=_activities)
    message = '0'
    if request.POST:
        cost = update.cost
        balance = available if budget_detail.budget.budget_status == 'DRAFT' or budget_detail.budget.budget_status == 'IN APPROVAL' else budget_detail.budget_balance
        if int(request.POST.get('cost')) > balance + cost:
            message = 'Total cost must be less than or equal to budget balance'
        else:
            update.activities = request.POST.get('activities')
            update.cost = int(request.POST.get('cost'))
            update.save()
            total_inc = IncrementalSales.objects.filter(
                proposal_id=_id).aggregate(Sum('incrp_nom'))['incrp_nom__sum'] if IncrementalSales.objects.filter(proposal_id=_id).exists() else 0
            total_cost = ProjectedCost.objects.filter(
                proposal_id=_id).aggregate(Sum('cost'))['cost__sum'] if ProjectedCost.objects.filter(proposal_id=_id).exists() else 0
            proposal.roi = (total_cost / total_inc) * \
                100 if total_inc != 0 else 0
            proposal.total_cost = total_cost
            proposal.balance = total_cost
            proposal.save()

            sum_cost = Proposal.objects.filter(budget=proposal.budget, channel=proposal.channel).exclude(status__in=['REJECTED']).aggregate(Sum('total_cost'))[
                'total_cost__sum'] if Proposal.objects.filter(budget=proposal.budget, channel=proposal.channel).exclude(status__in=['REJECTED']).exists() else 0
            budget_detail.budget_proposed = sum_cost
            budget_detail.save()
            sum_balance = BudgetDetail.objects.filter(budget=proposal.budget).aggregate(Sum('budget_balance'))[
                'budget_balance__sum'] if BudgetDetail.objects.filter(budget=proposal.budget).exists() else 0
            budget = Budget.objects.get(budget_id=proposal.budget)
            budget.budget_balance = sum_balance
            budget.save()

    return HttpResponseRedirect(reverse('proposal-view', args=[_tab, _id, _activities, 'upd-cost', message]))


@login_required(login_url='/login/')
@role_required(allowed_roles='PROPOSAL')
def proposal_update(request, _tab, _id):
    proposal = Proposal.objects.get(proposal_id=_id)
    divs = Division.objects.all()
    refs = Proposal.objects.filter(status='OPEN', area=proposal.area, budget__budget_distributor_id=proposal.budget.budget_distributor_id,
                                   channel=proposal.channel).exclude(proposal_id=_id).order_by('-proposal_date')
    attachment = ProposalAttachment.objects.filter(proposal_id=_id)
    incremental = IncrementalSales.objects.filter(proposal_id=_id)
    cost = ProjectedCost.objects.filter(proposal_id=_id)
    total = IncrementalSales.objects.filter(proposal_id=_id).aggregate(
        swop_carton__sum=Sum('swop_carton'),
        swop_nom__sum=Sum('swop_nom'),
        swp_carton__sum=Sum('swp_carton'),
        swp_nom__sum=Sum('swp_nom'),
        incrp_carton__sum=Sum('incrp_carton'),
        incrp_nom__sum=Sum('incrp_nom'),
        incpst_carton__ratio=(Sum('incrp_carton') /
                              Sum('swop_carton')) * 100 if Sum('swop_carton') else 0,
        incpst_nom__ratio=(Sum('incrp_nom') /
                           Sum('swop_nom')) * 100 if Sum('swop_nom') else 0,
    )
    total_cost = ProjectedCost.objects.filter(
        proposal_id=_id).aggregate(Sum('cost'))
    message = '0'
    msg = ''

    if request.POST:
        form = FormProposalUpdate(
            request.POST, request.FILES, instance=proposal)
        if form.is_valid():
            parent = form.save(commit=False)
            parent.duration = form.cleaned_data['period_end'] - \
                form.cleaned_data['period_start']
            if parent.duration.days < 0:
                message = 'Period end must be greater than period start.'
            else:
                parent.reference = form.cleaned_data['reference']
                parent.save()
                return HttpResponseRedirect(reverse('proposal-view', args=[_tab, _id, '0', '0', '0']))
    else:
        form = FormProposalUpdate(instance=proposal)

    msg = form.errors

    context = {
        'form': form,
        'data': proposal,
        'divs': divs,
        'refs': refs,
        'attachment': attachment,
        'incremental': incremental,
        'cost': cost,
        'total': total,
        'total_inc': total['incrp_nom__sum'] if total['incrp_nom__sum'] else 0,
        'total_cost': total_cost['cost__sum'] if total_cost['cost__sum'] else 0,
        'tab': _tab,
        'message': message,
        'msg': msg,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'proposal',
        'group_segment': 'proposal',
        'crud': 'update',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list(
            'menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id,
                                menu_id='PROPOSAL') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/proposal_view.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='PROPOSAL')
def proposal_delete(request, _tab, _id):
    proposal = Proposal.objects.get(proposal_id=_id)
    budget_detail = BudgetDetail.objects.get(
        budget=proposal.budget, budget_channel=proposal.channel)
    proposal.delete()
    sum_cost = Proposal.objects.filter(budget=proposal.budget, channel=proposal.channel).exclude(status__in=['REJECTED']).aggregate(Sum('total_cost'))[
        'total_cost__sum'] if Proposal.objects.filter(budget=proposal.budget, channel=proposal.channel).exclude(status__in=['REJECTED']).exists() else 0
    budget_detail.budget_proposed = sum_cost
    budget_detail.save()
    sum_balance = BudgetDetail.objects.filter(budget=proposal.budget).aggregate(Sum('budget_balance'))[
        'budget_balance__sum'] if BudgetDetail.objects.filter(budget=proposal.budget).exists() else 0
    budget = Budget.objects.get(budget_id=proposal.budget)
    budget.budget_balance = sum_balance
    budget.save()

    return HttpResponseRedirect(reverse('proposal-index', args=[_tab, ]))


@login_required(login_url='/login/')
@role_required(allowed_roles='PROPOSAL-CLOSING')
def proposal_closing_index(request):
    proposals = Proposal.objects.exclude(proposal_id__in=Program.objects.filter(status__in=['DRAFT', 'IN APPROVAL']).values_list(
        'proposal_id', flat=True)).exclude(proposal_id__in=Claim.objects.filter(status__in=['DRAFT', 'IN APPROVAL']).values_list('proposal_id', flat=True)).exclude(proposal_id__in=Claim.objects.filter(status__in=['DRAFT', 'IN APPROVAL']).values_list(
            'additional_proposal', flat=True)).filter(area__in=Budget.objects.filter(budget_status__in=['OPEN', 'DRAFT', 'IN APPROVAL'], budget_area__in=AreaUser.objects.filter(user_id=request.user.user_id).values_list('area_id', flat=True)).values_list('budget_area', flat=True), budget__budget_distributor__in=Budget.objects.filter(budget_status__in=['OPEN', 'DRAFT', 'IN APPROVAL']).values_list('budget_distributor', flat=True),
                                                      status='OPEN').order_by('-proposal_id').all()

    context = {
        'data': proposals,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'proposal_closing',
        'group_segment': 'proposal',
        'crud': 'index',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='PROPOSAL-CLOSING') if not request.user.is_superuser else Auth.objects.all(),
    }

    return render(request, 'home/proposal_closing_index.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='PROPOSAL-CLOSING')
def proposal_bulk_close(request):
    prop_nos = request.GET.get('prop_nos')
    _ids = prop_nos.split(',')
    for _id in _ids:
        proposal = Proposal.objects.get(proposal_id=_id)
        budget = Budget.objects.get(
            budget_area=proposal.area, budget_distributor=proposal.budget.budget_distributor, budget_status__in=['OPEN', 'DRAFT', 'IN APPROVAL'])
        budget_detail = BudgetDetail.objects.get(budget__budget_area=proposal.area, budget__budget_distributor=proposal.budget.budget_distributor,
                                                 budget_channel=proposal.channel, budget__budget_status__in=['OPEN', 'DRAFT', 'IN APPROVAL'])

        budget_detail.budget_remaining += proposal.balance
        budget_detail.save()

        sum_balance = BudgetDetail.objects.filter(budget__budget_area=proposal.area, budget__budget_distributor=proposal.budget.budget_distributor, budget__budget_status__in=['OPEN', 'DRAFT', 'IN APPROVAL']).aggregate(Sum('budget_balance'))[
            'budget_balance__sum'] if BudgetDetail.objects.filter(budget__budget_area=proposal.area, budget__budget_distributor=proposal.budget.budget_distributor, budget__budget_status__in=['OPEN', 'DRAFT', 'IN APPROVAL']).exists() else 0
        budget.budget_balance = sum_balance
        budget.save()

        proposal.status = 'CLOSED'
        proposal.save()

    return HttpResponseRedirect(reverse('proposal-closing-index'))


@login_required(login_url='/login/')
@role_required(allowed_roles='PROPOSAL-CLOSING')
def proposal_single_close(request, _id):
    proposal = Proposal.objects.get(proposal_id=_id)
    budget = Budget.objects.get(
        budget_area=proposal.area, budget_distributor=proposal.budget.budget_distributor, budget_status__in=['OPEN', 'DRAFT', 'IN APPROVAL'])
    budget_detail = BudgetDetail.objects.get(budget__budget_area=proposal.area, budget__budget_distributor=proposal.budget.budget_distributor,
                                             budget_channel=proposal.channel, budget__budget_status__in=['OPEN', 'DRAFT', 'IN APPROVAL'])

    budget_detail.budget_remaining += proposal.balance
    budget_detail.save()

    sum_balance = BudgetDetail.objects.filter(budget__budget_area=proposal.area, budget__budget_distributor=proposal.budget.budget_distributor, budget__budget_status__in=['OPEN', 'DRAFT', 'IN APPROVAL']).aggregate(Sum('budget_balance'))[
        'budget_balance__sum'] if BudgetDetail.objects.filter(budget__budget_area=proposal.area, budget__budget_distributor=proposal.budget.budget_distributor, budget__budget_status__in=['OPEN', 'DRAFT', 'IN APPROVAL']).exists() else 0
    budget.budget_balance = sum_balance
    budget.save()

    proposal.status = 'CLOSED'
    proposal.save()

    return HttpResponseRedirect(reverse('proposal-closing-index'))


@login_required(login_url='/login/')
@role_required(allowed_roles='PROGRAM')
def program_index(request, _tab):
    programs = Program.objects.all()
    drafts = Program.objects.filter(status='DRAFT', area__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-program_id').all
    draft_count = Program.objects.filter(status='DRAFT', area__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-program_id').count
    inapprovals = Program.objects.filter(status='IN APPROVAL', area__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-program_id').values_list('program_id', 'program_date', 'proposal__budget__budget_distributor__distributor_name', 'proposal__channel', ProgramRelease.objects.filter(program_id=OuterRef('program_id'), program_approval_status='N').order_by('sequence').values('program_approval_name')[:1])
    inapproval_count = Program.objects.filter(status='IN APPROVAL', area__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-program_id').count
    opens = Program.objects.filter(status='OPEN', area__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-program_id').all
    open_count = Program.objects.filter(status='OPEN', area__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-program_id').count

    context = {
        'data': programs,
        'drafts': drafts,
        'draft_count': draft_count,
        'inapprovals': inapprovals,
        'inapproval_count': inapproval_count,
        'opens': opens,
        'open_count': open_count,
        'tab': _tab,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'program',
        'group_segment': 'program',
        'crud': 'index',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list(
            'menu_id', flat=True),
        'btn': Auth.objects.get(
            user_id=request.user.user_id, menu_id='PROGRAM') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/program_index.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='PROGRAM')
def program_add(request, _area, _distributor, _proposal, _seq):
    selected_area = _area
    selected_distributor = _distributor
    selected_proposal = _proposal
    area = AreaSales.objects.get(
        area_id=selected_area) if selected_area != '0' else None
    proposal = Proposal.objects.get(
        proposal_id=selected_proposal) if selected_proposal != '0' else None
    inc_sales = IncrementalSales.objects.filter(
        proposal_id=selected_proposal) if selected_proposal != '0' else None
    areas = AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', 'area__area_name')
    distributors = Proposal.objects.filter(
        status='OPEN', area=selected_area, balance__gt=0).values_list('budget__budget_distributor__distributor_id', 'budget__budget_distributor__distributor_name').distinct() if selected_area != '0' else None
    proposals = Proposal.objects.filter(
        status='OPEN',
        area=selected_area,
        balance__gt=0,
        # period_end__gte=datetime.datetime.now().date(),
        budget__budget_distributor=selected_distributor,
    ).order_by('proposal_id') if selected_distributor != '0' else None

    message = ''
    no_save = False
    seq = _seq

    if selected_area != '0' and selected_proposal != '0':
        approvers = ProgramMatrix.objects.filter(
            area_id=_area, channel_id=proposal.channel).order_by('sequence')
        print_approvers = ProgramMatrix.objects.filter(
            area_id=_area, channel_id=proposal.channel, printed=1).order_by('sequence')
        if approvers.count() == 0 or approvers[0].limit > 0:
            message = "No program's approver found for this area and channel."
            no_save = True

    if _seq == 0:
        try:
            _no = Program.objects.filter(
                program_date__year=datetime.datetime.now().year).latest('seq_number')
        except Program.DoesNotExist:
            _no = None
        if _no is None:
            format_no = '{:04d}'.format(1)
            seq = 1
        else:
            format_no = '{:04d}'.format(_no.seq_number + 1)
            _no.seq_number += 1
            _no.save()
            seq = _no.seq_number
    else:
        format_no = '{:04d}'.format(seq)

    _id = 'SBS-3' + format_no + '/' + proposal.channel + '/' + selected_area + '/' + \
        str(proposal.budget.budget_distributor.distributor_id) + '/' + \
        datetime.datetime.now().strftime('%m/%Y') if selected_proposal != '0' else 'SBS-3' + format_no + '/' + selected_area + '/0' + \
        datetime.datetime.now().strftime('%m/%Y')

    bulan = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
             'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']
    bln = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun',
           'Jul', 'Agt', 'Sep', 'Okt', 'Nov', 'Des']

    if request.POST:
        form = FormProgram(request.POST, request.FILES)
        if form.is_valid():
            draft = form.save(commit=False)
            draft.program_date = datetime.datetime.now().date()
            draft.proposal_id = selected_proposal
            draft.seq_number = seq
            draft.entry_pos = request.user.position.position_id
            draft.header = '<style>@media only screen and (max-width: 600px) {.mobile-hide {display: none;}} @media (min-width: 601px) {.desktop-hide {display: none;}}</style><b><table style="width: 100%; height: 12;"><tr class="desktop-hide"><td style="text-align: right; padding-right: 0;"><strong>' + area.base_city + ', ' + datetime.datetime.now().strftime('%-d') + ' ' + bulan[int(datetime.datetime.now().strftime('%m')) - 1] + ' ' + datetime.datetime.now().strftime(
                '%Y') + '</strong></td></tr><tr class="desktop-hide"><td>&nbsp;</td></tr><tr><td style="padding-left: 0;"><b>No. ' + _id + '</b></td><td style="text-align: right; padding-right: 0;" class="mobile-hide"><b>' + area.base_city + ', ' + datetime.datetime.now().strftime('%-d') + ' ' + bulan[int(datetime.datetime.now().strftime('%m')) - 1] + ' ' + datetime.datetime.now().strftime('%Y') + '</b></td></tr></table><br>Kepada Yth.<br>' + proposal.budget.budget_distributor.distributor_name + '<br>Di Tempat,</b><br>'
            draft.save()

            for approver in approvers:
                release = ProgramRelease(
                    program_id=draft.program_id,
                    program_approval_id=approver.approver_id,
                    program_approval_name=approver.approver.username,
                    program_approval_email=approver.approver.email,
                    program_approval_position=approver.approver.position.position_id,
                    sequence=approver.sequence,
                    limit=approver.limit,
                    return_to=approver.return_to,
                    approve=approver.approve,
                    revise=approver.revise,
                    returned=approver.returned,
                    reject=approver.reject,
                    notif=approver.notif,
                    printed=approver.printed,
                    as_approved=approver.as_approved)
                release.save()

            return HttpResponseRedirect(reverse('program-view', args=['draft', _id]))
    else:
        prod = ''
        if selected_proposal != '0':
            plus4mo = datetime.date(
                proposal.period_end.year, proposal.period_end.month, 15) + datetime.timedelta(days=120)
            deadline = datetime.date(
                plus4mo.year, plus4mo.month, 1) - datetime.timedelta(days=1)

            for i in range(0, inc_sales.count()):
                prod += inc_sales[i].product
                if i != inc_sales.count() - 1:
                    prod += ', '

            len_prog = len(proposal.program_name)
            if len_prog > 110:
                _height = 24
            else:
                _height = 12

            approver_signature = ''
            for approver in range(print_approvers.count()):
                approver_signature += '<td style="padding-left: 0; height: 50"><img style="flex: 0 0 auto;" src="' + \
                    str(host.url) + 'apps/media/' + str(
                        print_approvers[approver].approver.signature) + '" alt="Signature" width="120" height="70" /></td>'

            approver_name = ''
            for approver in range(print_approvers.count()):
                approver_name += '<td style="padding-left: 0; height: 12"><span style="text-decoration: underline;">' + \
                    print_approvers[approver].approver.username + \
                    '</span></td>'

            approver_position = ''
            for approver in range(print_approvers.count()):
                approver_position += '<td style="padding-left: 0; height: 12">' + \
                    print_approvers[approver].approver.position.position_name + '</td>'

            if no_save:
                form = FormProgram()
            else:
                form = FormProgram(initial={'program_id': _id, 'area': selected_area, 'deadline': deadline, 'header': '<b><table style="width: 100%; height: 12;"><tr><td style="padding-left: 0;"><b>No. ' + _id + '</b></td><td style="text-align: right; padding-right: 0;"><b>' + area.base_city + ', ' + datetime.datetime.now().strftime('%-d') + ' ' + bulan[int(datetime.datetime.now().strftime('%m')) - 1] + ' ' + datetime.datetime.now().strftime('%Y') + '</b></td></tr></table><br>Kepada Yth.<br>' + proposal.budget.budget_distributor.distributor_name + '<br>Di Tempat,</b><br>', 'content': '<b>Hal : <u>' + proposal.program_name + '</u></b><br><br>' + 'Dengan hormat,<br>' +
                                            'Sehubungan dengan informasi proposal ABC PI dengan no. sbb :<br><ul><li><b>' + proposal.proposal_id + ' (ANP Manual)</b></li></ul>Maka bersama surat ini kami sampaikan mengenai support program dengan rincian sebagai berikut :<br><table style="width: 100%; height: 12;"><tr><td style="padding-left: 0; width: 15%; height: ' + str(_height) + '; vertical-align: top;">Nama Program</td><td style="padding-left: 0; width: 2%; height: ' + str(_height) + '; vertical-align: top;">: </td><td style="padding-left: 0; width: 76%; height: ' + str(_height) + '; vertical-align: top;">' + proposal.program_name + '</td></tr><tr><td style="padding-left: 0; width: 15%; height: 12; vertical-align: top;">Produk</td><td style="padding-left: 0; width: 2%; height: 12; vertical-align: top;">: </td><td style="padding-left: 0; width: 76%; height: 12; vertical-align: top;">' + prod + '</td></tr><tr><td style="padding-left: 0; width: 15%; height: 12; vertical-align: top;">Periode</td><td style="padding-left: 0; width: 2%; height: 12; vertical-align: top;">: </td><td style="padding-left: 0; width: 76%; height: 12; vertical-align: top;">' + proposal.period_start.strftime("%-d") + ' ' + bln[int(proposal.period_start.strftime('%m')) - 1] + ' - ' + proposal.period_end.strftime("%d") + ' ' + bln[int(proposal.period_end.strftime('%m')) - 1] + ' ' + proposal.period_end.strftime("%Y") + '</td></tr><tr><td style="padding-left: 0; width: 15%; height: 12; vertical-align: top;">Wilayah/Channel</td><td style="padding-left: 0; width: 2%; height: 12; vertical-align: top;">: </td><td style="padding-left: 0; width: 76%; height: 12; vertical-align: top;">' + proposal.budget.budget_area.area_name + '/' + proposal.channel + '</td></tr><tr><td style="padding-left: 0; width: 15%; height: 12; vertical-align: top;">Detail Qty</td><td style="padding-left: 0; width: 2%; height: 12; vertical-align: top;">: </td><td style="padding-left: 0; width: 76%; height: 12; vertical-align: top;"></td></tr></table>' +
                                            '<br>Mekanisme Program dan Klaim sebagai berikut :<br>' + proposal.mechanism.replace('\n', '<br>'), 'disclaimer': '<p><strong><em>"Program di atas dapat diklaim ke PT. ABC PI paling lambat tanggal ' + deadline.strftime('%d') + ' ' + bulan[int(deadline.strftime('%m')) - 1] + ' ' + deadline.strftime('%Y') + ', melewati dari batas tersebut PT. ABC PI berhak menolak dan tidak memproses klaim tersebut".</em></strong></p>' + '<p>Demikian surat ini kami sampaikan. Atas perhatian dan kerjasamanya kami ucapkan terima kasih.</p>', 'approval':
                                            '<p><br />Hormat Kami,</p>' +
                                            '<table style="width: 100%; height: 50"><tbody><tr>' + approver_signature + '</tr><tr>' +
                                                approver_name + '</tr><tr>' + approver_position +
                                            '</tr></tbody></table><br />',
                                            'footer': '<p style="line-height: 1.05;"><strong><span style="font-size: 6pt;">PT. ABC PRESIDENT INDONESIA (www.abcpresident.com)<br />Head Office : </span></strong><span style="font-size: 6pt;">EightyEight@Kasablanka Office Tower A Lt. 31 Jl. Casablanca Raya Kav. 88 Jakarta Selatan 12870 <strong>Tel : </strong>+62 21 2982 0168 (Hunting) <strong>Fax : </strong>+62 21 2982 0166<br /><strong>Factory : </strong>Desa Walabar Kec. Klari, Karawang Timur 41371, Jawa Barat, Indonesia <strong>Tel : </strong>+62 267 431 422 (Hunting) <strong>Fax : </strong>+62 267 431 421<br /></span></p>'})
        else:
            form = FormProgram()

    msg = form.errors
    context = {
        'form': form,
        'area': areas,
        'distributors': distributors,
        'proposals': proposals,
        'selected_area': selected_area,
        'selected_distributor': selected_distributor,
        'selected_proposal': selected_proposal,
        'seq': seq,
        'msg': msg,
        'message': message,
        'no_save': no_save,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'program',
        'group_segment': 'program',
        'crud': 'add',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list(
            'menu_id', flat=True),
        'btn': Auth.objects.get(
            user_id=request.user.user_id, menu_id='PROGRAM') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/program_add.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='PROGRAM')
def program_submit(request, _id):
    program = Program.objects.get(program_id=_id)
    program.status = 'IN APPROVAL'
    program.save()

    mail_sent = ProgramRelease.objects.filter(
        program_id=_id).order_by('sequence').values_list('mail_sent', flat=True)
    if mail_sent[0] == False:
        email = ProgramRelease.objects.filter(
            program_id=_id).order_by('sequence').values_list('program_approval_email', flat=True)
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT username FROM apps_programrelease INNER JOIN apps_user ON apps_programrelease.program_approval_id = apps_user.user_id WHERE program_id = '" + str(_id) + "' AND program_approval_status = 'N' ORDER BY sequence LIMIT 1")
            approver = cursor.fetchone()

        subject = 'Program Approval'
        msg = 'Dear ' + approver[0] + ',\n\nYou have a new program to approve. Please check your program release list.\n\n' + \
            'Click this link to approve, revise, return or reject this program.\n' + host.url + 'program_release/view/' + str(_id) + '/0/' + \
            '\n\nThank you.'
        send_email(subject, msg, [email[0]])

        # update mail sent to true
        release = ProgramRelease.objects.filter(
            program_id=_id).order_by('sequence').first()
        release.mail_sent = True
        release.save()

    return HttpResponseRedirect(reverse('program-index', args=['inapproval', ]))


@login_required(login_url='/login/')
@role_required(allowed_roles='PROGRAM')
def program_view(request, _tab, _id):
    program = Program.objects.get(program_id=_id)
    form = FormProgramView(instance=program)

    highest_approval = ProgramRelease.objects.filter(
        program_id=_id).aggregate(Max('sequence'))
    highest_sequence = highest_approval.get('sequence__min') if highest_approval.get(
        'sequence__min') else highest_approval.get('sequence__max') + 1
    if highest_sequence:
        approval = ProgramRelease.objects.filter(
            program_id=_id, sequence__lt=highest_sequence).order_by('sequence')
    else:
        approval = ProgramRelease.objects.filter(
            program_id=_id).order_by('sequence')
    rejector = ProgramRelease.objects.filter(
        program_id=_id, program_approval_status='N').order_by('sequence').first() if program.status == 'REJECTED' else None

    context = {
        'data': program,
        'form': form,
        'tab': _tab,
        'approval': approval,
        'rejector': rejector,
        'status': program.status,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'program_archive' if _tab == 'reject' else 'program',
        'group_segment': 'program',
        'crud': 'view',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list(
            'menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id,
                                menu_id='PROGRAM') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/program_view.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='PROGRAM')
def program_update(request, _tab, _id):
    program = Program.objects.get(program_id=_id)
    message = '0'

    if request.POST:
        form = FormProgramUpdate(
            request.POST, request.FILES, instance=program)
        if form.is_valid():
            update = form.save(commit=False)
            update.save()

            return HttpResponseRedirect(reverse('program-view', args=[_tab, _id]))
    else:
        form = FormProgramUpdate(instance=program)

    msg = form.errors
    context = {
        'form': form,
        'data': program,
        'tab': _tab,
        'message': message,
        'msg': msg,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'program',
        'group_segment': 'program',
        'crud': 'update',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list(
            'menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id,
                                menu_id='PROGRAM') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/program_view.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='PROGRAM')
def program_delete(request, _tab, _id):
    program = Program.objects.get(program_id=_id)
    program.delete()

    return HttpResponseRedirect(reverse('program-index', args=[_tab, ]))


@login_required(login_url='/login/')
@role_required(allowed_roles='PROGRAM-RELEASE')
def program_release_index(request):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT apps_program.program_id, apps_program.program_date, apps_distributor.distributor_name, apps_proposal.channel, apps_program.status, apps_programrelease.sequence FROM apps_distributor INNER JOIN apps_budget ON apps_distributor.distributor_id = apps_budget.budget_distributor_id INNER JOIN apps_proposal ON apps_budget.budget_id = apps_proposal.budget_id INNER JOIN apps_program ON apps_proposal.proposal_id = apps_program.proposal_id INNER JOIN apps_programrelease ON apps_program.program_id = apps_programrelease.program_id INNER JOIN (SELECT program_id, MIN(sequence) AS seq FROM apps_programrelease WHERE program_approval_status = 'N' GROUP BY program_id ORDER BY sequence ASC) AS q_group ON apps_programrelease.program_id = q_group.program_id AND apps_programrelease.sequence = q_group.seq WHERE (apps_program.status = 'PENDING' OR apps_program.status = 'IN APPROVAL') AND apps_programrelease.program_approval_id = '" + str(request.user.user_id) + "'")
        release = cursor.fetchall()

    context = {
        'data': release,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'program_release',
        'group_segment': 'program',
        'crud': 'index',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list(
            'menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id,
                                menu_id='PROGRAM-RELEASE') if not request.user.is_superuser else Auth.objects.all(),
    }

    return render(request, 'home/program_release_index.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='PROGRAM-RELEASE')
def program_release_view(request, _id, _is_revise):
    program = Program.objects.get(program_id=_id)
    form = FormProgramView(instance=program)
    approved = ProgramRelease.objects.get(
        program_id=_id, program_approval_id=request.user.user_id).program_approval_status

    context = {
        'form': form,
        'data': program,
        'approved': approved,
        'is_revise': _is_revise,
        'status': program.status,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'program_release',
        'group_segment': 'program',
        'crud': 'view',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='PROGRAM-RELEASE') if not request.user.is_superuser else Auth.objects.all(),
        'btn_release': ProgramRelease.objects.get(program_id=_id, program_approval_id=request.user.user_id),
    }
    return render(request, 'home/program_release_view.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='PROGRAM-RELEASE')
def program_release_update(request, _id):
    program = Program.objects.get(program_id=_id)
    message = '0'
    _deadline = program.deadline
    _content = program.content

    if request.POST:
        form = FormProgramUpdate(
            request.POST, request.FILES, instance=program)
        if form.is_valid():
            update = form.save(commit=False)
            deadline = _deadline if form.cleaned_data['deadline'] != _deadline else None
            content = _content if form.cleaned_data['content'] != _content else None
            update.save()

            recipients = []

            release = ProgramRelease.objects.get(
                program_id=_id, program_approval_id=request.user.user_id)
            release.revise_note = request.POST.get('revise_note')
            release.save()

            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT program_id, email FROM apps_program INNER JOIN apps_user ON apps_program.entry_by = apps_user.user_id WHERE program_id = '" + str(_id) + "'")
                entry_mail = cursor.fetchone()
                if entry_mail:
                    recipients.append(entry_mail[1])

                cursor.execute(
                    "SELECT program_id, email FROM apps_program INNER JOIN apps_user ON apps_program.update_by = apps_user.user_id WHERE program_id = '" + str(_id) + "'")
                update_mail = cursor.fetchone()
                if update_mail:
                    recipients.append(update_mail[1])

                cursor.execute(
                    "SELECT program_id, program_approval_email FROM apps_programrelease WHERE program_id = '" + str(_id) + "' AND program_approval_status = 'Y'")
                approver_mail = cursor.fetchall()
                for mail in approver_mail:
                    recipients.append(mail[1])

            subject = 'Program Revised'
            msg = 'Dear All,\n\nThe following is revised program for Program No. ' + \
                str(_id) + ':\n'
            if deadline:
                msg += '\nBEFORE\n'
                msg += 'Claim Deadline: ' + \
                    deadline.strftime('%d %b %Y') + '\n'
                msg += '\nAFTER\n'
                msg += 'Claim Deadline: ' + \
                    form.cleaned_data['deadline'].strftime('%d %b %Y') + '\n'

            if content:
                msg += '\nCONTENT: Content has been revised. View the program for more details.\n'

            msg += '\nNote: ' + \
                str(release.revise_note) + '\n\nClick the following link to view the program.\n' + host.url + 'program/view/inapproval/' + str(_id) + '/' + \
                '\n\nThank you.'

            recipient_list = list(dict.fromkeys(recipients))
            send_email(subject, msg, recipient_list)

            return HttpResponseRedirect(reverse('program-release-view', args=[_id, 0]))
    else:
        form = FormProgramUpdate(instance=program)

    err = form.errors
    context = {
        'form': form,
        'data': program,
        'message': message,
        'msg': err,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'program',
        'group_segment': 'program',
        'crud': 'update',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list(
            'menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id,
                                menu_id='PROGRAM-RELEASE') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/program_release_view.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='PROGRAM-RELEASE')
def program_release_approve(request, _id):
    program = Program.objects.get(program_id=_id)
    release = ProgramRelease.objects.get(
        program_id=_id, program_approval_id=request.user.user_id)
    release.program_approval_status = 'Y'
    release.program_approval_date = timezone.now()
    release.save()
    highest_approval = ProgramRelease.objects.filter(
        program_id=_id).aggregate(Max('sequence'))
    highest_sequence = highest_approval.get('sequence__min') if highest_approval.get(
        'sequence__min') else highest_approval.get('sequence__max') + 1
    if highest_sequence:
        approval = ProgramRelease.objects.filter(
            program_id=_id, sequence__lt=highest_sequence).order_by('sequence').last()
    else:
        approval = ProgramRelease.objects.filter(
            program_id=_id).order_by('sequence').last()

    if release.sequence == approval.sequence:
        program.status = 'OPEN'
        program.save()

        recipients = []

        maker = program.entry_by
        maker_mail = User.objects.get(user_id=maker).email
        recipients.append(maker_mail)

        approvers = ProgramRelease.objects.filter(
            program_id=_id, notif=True, program_approval_status='Y')
        for i in approvers:
            recipients.append(i.program_approval_email)

        subject = 'Program Approved'
        msg = 'Dear All,\n\nProgram No. ' + str(_id) + ' has been approved.\n\nClick the following link to view the program.\n' + host.url + 'program/view/open/' + str(_id) + \
            '\n\nThank you.'
        recipient_list = list(dict.fromkeys(recipients))
        send_email(subject, msg, recipient_list)
    else:
        program.status = 'IN APPROVAL'
        program.save()

        email = ProgramRelease.objects.filter(program_id=_id, program_approval_status='N').order_by(
            'sequence').values_list('program_approval_email', flat=True)
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT program_approval_name FROM apps_programrelease WHERE program_id = '" + str(_id) + "' AND program_approval_status = 'N' ORDER BY sequence LIMIT 1")
            approver = cursor.fetchone()

        subject = 'Program Approval'
        msg = 'Dear ' + approver[0] + ',\n\nYou have a new program to approve. Please check your program release list.\n\n' + \
            'Click this link to approve, revise, return or reject this program.\n' + host.url + 'program_release/view/' + str(_id) + '/0/' + \
            '\n\nThank you.'
        send_email(subject, msg, [email[0]])

    return HttpResponseRedirect(reverse('program-release-index'))


@login_required(login_url='/login/')
@role_required(allowed_roles='PROGRAM-RELEASE')
def program_release_return(request, _id):
    recipients = []
    draft = False

    try:
        return_to = ProgramRelease.objects.get(
            program_id=_id, return_to=True, sequence__lt=ProgramRelease.objects.get(program_id=_id, program_approval_id=request.user.user_id).sequence)

        if return_to:
            approvers = ProgramRelease.objects.filter(
                program_id=_id, sequence__gte=ProgramRelease.objects.get(program_id=_id, return_to=True).sequence, sequence__lt=ProgramRelease.objects.get(program_id=_id, program_approval_id=request.user.user_id).sequence)
    except ProgramRelease.DoesNotExist:
        approvers = ProgramRelease.objects.filter(
            program_id=_id, sequence__lte=ProgramRelease.objects.get(program_id=_id, program_approval_id=request.user.user_id).sequence)
        draft = True

    for i in approvers:
        recipients.append(i.program_approval_email)
        i.program_approval_status = 'N'
        i.program_approval_date = None
        i.revise_note = ''
        i.return_note = ''
        i.reject_note = ''
        i.mail_sent = False
        i.save()

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT program_id, email FROM apps_program INNER JOIN apps_user ON apps_program.entry_by = apps_user.user_id WHERE program_id = '" + str(_id) + "'")
        entry_mail = cursor.fetchone()
        if entry_mail:
            recipients.append(entry_mail[1])

        cursor.execute(
            "SELECT program_id, email FROM apps_program INNER JOIN apps_user ON apps_program.update_by = apps_user.user_id WHERE program_id = '" + str(_id) + "'")
        update_mail = cursor.fetchone()
        if update_mail:
            recipients.append(update_mail[1])

    note = ProgramRelease.objects.get(
        program_id=_id, program_approval_id=request.user.user_id)
    note.return_note = request.POST.get('return_note')
    note.save()

    subject = 'Program Returned'
    msg = 'Dear All,\n\nProgram No. ' + str(_id) + ' has been returned.\n\nNote: ' + \
        str(note.return_note) + \
        '\n\nClick the following link to revise the program.\n'

    if draft:
        program = Program.objects.get(program_id=_id)
        program.status = 'DRAFT'
        program.save()
        msg += host.url + 'program/view/pending/' + str(_id) + \
            '\n\nThank you.'
    else:
        msg += host.url + 'program_release/view/' + \
            str(_id) + '/0/\n\nThank you.'
    recipient_list = list(dict.fromkeys(recipients))
    send_email(subject, msg, recipient_list)

    return HttpResponseRedirect(reverse('program-release-index'))


@login_required(login_url='/login/')
@role_required(allowed_roles='PROGRAM-RELEASE')
def program_release_reject(request, _id):
    recipients = []

    try:
        approvers = ProgramRelease.objects.filter(
            program_id=_id, sequence__lt=ProgramRelease.objects.get(program_id=_id, program_approval_id=request.user.user_id).sequence)
    except ProgramRelease.DoesNotExist:
        pass

    for i in approvers:
        recipients.append(i.program_approval_email)

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT program_id, email FROM apps_program INNER JOIN apps_user ON apps_program.entry_by = apps_user.user_id WHERE program_id = '" + str(_id) + "'")
        entry_mail = cursor.fetchone()
        if entry_mail:
            recipients.append(entry_mail[1])

        cursor.execute(
            "SELECT program_id, email FROM apps_program INNER JOIN apps_user ON apps_program.update_by = apps_user.user_id WHERE program_id = '" + str(_id) + "'")
        update_mail = cursor.fetchone()
        if update_mail:
            recipients.append(update_mail[1])

    note = ProgramRelease.objects.get(
        program_id=_id, program_approval_id=request.user.user_id)
    note.reject_note = request.POST.get('reject_note')
    note.save()

    subject = 'Program Rejected'
    msg = 'Dear All,\n\nProgram No. ' + str(_id) + ' has been rejected.\n\nNote: ' + \
        str(note.reject_note) + \
        '\n\nClick the following link to see the program.\n'

    program = Program.objects.get(program_id=_id)
    program.status = 'REJECTED'
    program.save()
    msg += host.url + 'program/view/reject/' + str(_id) + \
        '\n\nThank you.'
    recipient_list = list(dict.fromkeys(recipients))
    send_email(subject, msg, recipient_list)

    return HttpResponseRedirect(reverse('program-release-index'))


@login_required(login_url='/login/')
@role_required(allowed_roles='PROGRAM-ARCHIVE')
def program_archive_index(request):
    rejects = Program.objects.filter(status='REJECTED', area__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-program_id').all
    reject_count = Program.objects.filter(status='REJECTED', area__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-program_id').count

    context = {
        'rejects': rejects,
        'reject_count': reject_count,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'program_archive',
        'group_segment': 'program',
        'crud': 'index',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list(
            'menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id,
                                menu_id='PROGRAM-ARCHIVE') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/program_archive.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='PROGRAM')
def program_print(request, _id):
    program = Program.objects.get(program_id=_id)
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT signature, program_approval_name, position_name FROM apps_user INNER JOIN apps_programrelease ON user_id = program_approval_id INNER JOIN apps_position ON program_approval_position = apps_position.position_id WHERE program_id = '" + str(_id) + "' AND program_approval_status = 'Y' AND printed = True ORDER BY sequence")
        approvers = cursor.fetchall()

    html_file = 'home/program_print.html'
    context = {'data': program, 'approvers': approvers,
               'host': host.url, 'space': '0' * 10}
    template = get_template(html_file)
    html = template.render(context)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'filename="' + _id + '.pdf"'

    # Draw the HTML content on the PDF canvas
    pisa.CreatePDF(html, dest=response)

    return response


@login_required(login_url='/login/')
@role_required(allowed_roles='PROGRAM-APPROVAL')
def program_matrix_index(request):
    areas = AreaSales.objects.all()

    context = {
        'data': areas,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'program_matrix',
        'group_segment': 'approval',
        'crud': 'index',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='PROGRAM-APPROVAL') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/program_matrix_index.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='PROGRAM-APPROVAL')
def program_matrix_view(request, _id, _channel):
    area = AreaSales.objects.get(area_id=_id)
    channels = AreaChannelDetail.objects.filter(area_id=_id, status=1)
    approvers = ProgramMatrix.objects.filter(area_id=_id, channel_id=_channel)
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT user_id, username, position_name, q_programmatrix.approver_id FROM apps_user INNER JOIN apps_position ON apps_user.position_id = apps_position.position_id LEFT JOIN (SELECT * FROM apps_programmatrix WHERE area_id = '" + str(_id) + "' AND channel_id = '" + str(_channel) + "') AS q_programmatrix ON apps_user.user_id = q_programmatrix.approver_id WHERE q_programmatrix.approver_id IS NULL")
        users = cursor.fetchall()

    if request.POST:
        check = request.POST.getlist('checks[]')
        for i in users:
            if str(i[0]) in check:
                try:
                    approver = ProgramMatrix(
                        area_id=_id, channel_id=_channel, approver_id=i[0])
                    approver.save()
                except IntegrityError:
                    continue
            else:
                ProgramMatrix.objects.filter(
                    area_id=_id, channel_id=_channel, approver_id=i[0]).delete()

        return HttpResponseRedirect(reverse('program-matrix-view', args=[_id, _channel]))

    context = {
        'data': area,
        'channels': channels,
        'users': users,
        'approvers': approvers,
        'channel': _channel,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'program_matrix',
        'group_segment': 'approval',
        'tab': 'auth',
        'crud': 'view',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='PROGRAM-APPROVAL') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/program_matrix_view.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='PROGRAM-APPROVAL')
def program_matrix_update(request, _id, _channel, _approver):
    approvers = ProgramMatrix.objects.get(
        area=_id, channel_id=_channel, approver_id=_approver)

    if request.POST:
        approvers.sequence = int(request.POST.get('sequence'))
        approvers.limit = int(request.POST.get('limit'))
        approvers.return_to = True if request.POST.get('return') else False
        approvers.approve = True if request.POST.get('approve') else False
        approvers.revise = True if request.POST.get('revise') else False
        approvers.returned = True if request.POST.get('returned') else False
        approvers.reject = True if request.POST.get('reject') else False
        approvers.notif = True if request.POST.get('notif') else False
        approvers.printed = True if request.POST.get('printed') else False
        approvers.as_approved = request.POST.get('as_approved')
        approvers.save()

        return HttpResponseRedirect(reverse('program-matrix-view', args=[_id, _channel]))

    return render(request, 'home/program_matrix_view.html')


@login_required(login_url='/login/')
@role_required(allowed_roles='PROGRAM-APPROVAL')
def program_matrix_delete(request, _id, _channel, _arg):
    approvers = ProgramMatrix.objects.get(
        area=_id, channel_id=_channel, approver_id=_arg)
    approvers.delete()

    return HttpResponseRedirect(reverse('program-matrix-view', args=[_id, _channel]))


@login_required(login_url='/login/')
@role_required(allowed_roles='CLAIM')
def claim_index(request, _tab):
    claims = Claim.objects.all().order_by('-claim_id')
    drafts = Claim.objects.filter(status='DRAFT', area__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-claim_id').all
    draft_count = Claim.objects.filter(status='DRAFT', area__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-claim_id').count
    inapprovals = Claim.objects.filter(status='IN APPROVAL', area__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-claim_id').values_list('claim_id', 'claim_date', 'proposal__budget__budget_distributor__distributor_name', 'proposal__channel', 'total_claim', ClaimRelease.objects.filter(claim_id=OuterRef('claim_id'), claim_approval_status='N').order_by('sequence').values('claim_approval_name')[:1])
    inapproval_count = Claim.objects.filter(status='IN APPROVAL', area__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-claim_id').count
    opens = Claim.objects.filter(status='OPEN', area__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-claim_id').values_list('claim_id', 'cldetail__cl_id', 'claim_date', 'proposal__budget__budget_distributor__distributor_name', 'proposal__channel', 'total_claim', 'status')
    open_count = Claim.objects.filter(status='OPEN', area__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-claim_id').count

    context = {
        'data': claims,
        'drafts': drafts,
        'draft_count': draft_count,
        'inapprovals': inapprovals,
        'inapproval_count': inapproval_count,
        'opens': opens,
        'open_count': open_count,
        'tab': _tab,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'claim',
        'group_segment': 'claim',
        'crud': 'index',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='CLAIM') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/claim_index.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='CLAIM')
def claim_add(request, _area, _distributor, _program):
    selected_area = _area
    selected_distributor = _distributor
    selected_program = _program
    program = Program.objects.get(
        program_id=selected_program) if selected_program != '0' else None
    area = AreaUser.objects.filter(user_id=request.user.user_id).values_list(
        'area_id', 'area__area_name')
    distributors = Program.objects.filter(status='OPEN', area=selected_area).values_list(
        'proposal__budget__budget_distributor__distributor_id', 'proposal__budget__budget_distributor__distributor_name').distinct() if selected_area != '0' else None
    programs = Program.objects.filter(status='OPEN',
                                      #   deadline__gte=datetime.datetime.now().date(),
                                      area=selected_area, proposal__budget__budget_distributor__distributor_id=selected_distributor, proposal__balance__gt=0).distinct() if selected_distributor != '0' else None
    proposal = Proposal.objects.get(
        proposal_id=program.proposal.proposal_id) if selected_program != '0' else None
    proposals = Proposal.objects.filter(
        status='OPEN', area=selected_area, balance__gt=0, budget__budget_distributor=selected_distributor).order_by('-proposal_id') if selected_distributor != '0' else None

    no_save = False
    add_prop = '0'
    message = ''
    difference = 0
    add_proposals = None

    if selected_area != '0' and selected_program != '0':
        approvers = ClaimMatrix.objects.filter(
            area_id=selected_area, channel=program.proposal.channel).order_by('sequence')
        if approvers.count() == 0 or approvers[0].limit > 0:
            no_save = True
            message = "No claim's approver found for this area and channel."

    try:
        _no = Claim.objects.filter(
            claim_date__year=datetime.datetime.now().year).latest('seq_number')
    except Claim.DoesNotExist:
        _no = None
    if _no is None:
        format_no = '{:04d}'.format(1)
    else:
        format_no = '{:04d}'.format(_no.seq_number + 1)

    _id = 'CBS-4' + format_no + '/' + program.proposal.channel + '/' + selected_area + '/' + \
        program.proposal.budget.budget_distributor.distributor_id + '/' + \
        datetime.datetime.now().strftime('%m/%Y') if selected_program != '0' else 'CBS-4' + format_no + '/' + selected_area + '/0' + \
        '/' + datetime.datetime.now().strftime('%m/%Y')

    if request.POST:
        form = FormClaim(request.POST, request.FILES)
        difference = int(request.POST.get('amount')) - int(proposal.balance)
        if int(request.POST.get('amount')) > int(proposal.balance) and request.POST.get('add_proposal') == '':
            add_prop = '1'
            message = 'Claim amount is greater than proposal balance.'
            add_proposals = Proposal.objects.filter(
                status='OPEN', balance__gte=difference, reference=program.proposal_id).order_by('-proposal_id')
        else:
            if form.is_valid():
                draft = form.save(commit=False)
                draft.claim_date = timezone.now().date()
                draft.program_id = selected_program
                draft.seq_number = _no.seq_number + 1 if _no else 1
                draft.entry_pos = request.user.position.position_id
                draft.total_claim = Decimal(request.POST.get('amount'))
                draft.amount = proposal.balance if request.POST.get(
                    'add_proposal') else Decimal(request.POST.get('amount'))
                draft.additional_proposal = request.POST.get(
                    'add_proposal') if request.POST.get('add_proposal') else ''
                draft.additional_amount = difference if request.POST.get(
                    'add_proposal') else 0
                draft.is_tax = True if request.POST.get('is_tax') else False
                draft.save()

                for approver in approvers:
                    release = ClaimRelease(
                        claim_id=draft.claim_id,
                        claim_approval_id=approver.approver_id,
                        claim_approval_name=approver.approver.username,
                        claim_approval_email=approver.approver.email,
                        claim_approval_position=approver.approver.position.position_id,
                        sequence=approver.sequence,
                        limit=approver.limit,
                        return_to=approver.return_to,
                        approve=approver.approve,
                        revise=approver.revise,
                        returned=approver.returned,
                        reject=approver.reject,
                        notif=approver.notif,
                        printed=approver.printed,
                        as_approved=approver.as_approved)
                    release.save()

                return HttpResponseRedirect(reverse('claim-view', args=['draft', _id, '0', '0', '0', '0', 'all']))
    else:
        form = FormClaim(initial={'area': selected_area, 'claim_id': _id,
                         'due_date': datetime.datetime.now().date() + datetime.timedelta(days=30)})

    msg = form.errors
    context = {
        'form': form,
        'area': area,
        'distributors': distributors,
        'program': program,
        'programs': programs,
        'proposals': proposals,
        'add_proposals': add_proposals,
        'selected_area': selected_area,
        'selected_distributor': selected_distributor,
        'selected_program': selected_program,
        'msg': msg,
        'message': message,
        'no_save': no_save,
        'add_prop': add_prop,
        'difference': difference,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'claim',
        'group_segment': 'claim',
        'crud': 'add',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list(
            'menu_id', flat=True),
        'btn': Auth.objects.get(
            user_id=request.user.user_id, menu_id='CLAIM') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/claim_add.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='CLAIM')
def claim_submit(request, _id):
    claim = Claim.objects.get(claim_id=_id)
    program = Program.objects.get(program_id=claim.program_id)
    proposal = Proposal.objects.get(proposal_id=program.proposal.proposal_id)

    claim.status = 'IN APPROVAL'
    claim.save()

    sum_amount = Claim.objects.filter(
        proposal_id=claim.proposal_id).exclude(status__in=['DRAFT', 'REJECTED']).aggregate(Sum('amount'))
    sum_add_amount = Claim.objects.filter(additional_proposal=claim.proposal_id).exclude(
        status__in=['DRAFT', 'REJECTED']).aggregate(Sum('additional_amount'))

    sum_amount2 = Claim.objects.filter(
        proposal_id=claim.additional_proposal).exclude(status__in=['DRAFT', 'REJECTED']).aggregate(Sum('amount'))
    sum_add_amount2 = Claim.objects.filter(additional_proposal=claim.additional_proposal).exclude(status__in=['DRAFT', 'REJECTED']).aggregate(
        Sum('additional_amount'))

    amount = sum_amount.get('amount__sum') if sum_amount.get(
        'amount__sum') else 0
    additional_amount = sum_add_amount.get(
        'additional_amount__sum') if sum_add_amount.get('additional_amount__sum') else 0

    amount2 = sum_amount2.get('amount__sum') if sum_amount2.get(
        'amount__sum') else 0
    additional_amount2 = sum_add_amount2.get('additional_amount__sum') if sum_add_amount2.get(
        'additional_amount__sum') else 0

    # update parked claim
    sum_parked_amount = Claim.objects.filter(
        proposal_id=claim.proposal_id, status__in=['IN APPROVAL']).aggregate(Sum('amount'))
    sum_add_parked_amount = Claim.objects.filter(additional_proposal=claim.proposal_id, status__in=[
        'IN APPROVAL']).aggregate(Sum('additional_amount'))

    parked_amount = sum_parked_amount.get(
        'amount__sum') if sum_parked_amount.get('amount__sum') else 0
    additional_parked_amount = sum_add_parked_amount.get(
        'additional_amount__sum') if sum_add_parked_amount.get('additional_amount__sum') else 0

    sum_parked_amount2 = Claim.objects.filter(proposal_id=claim.additional_proposal, status__in=[
        'IN APPROVAL']).aggregate(Sum('amount'))
    sum_add_parked_amount2 = Claim.objects.filter(additional_proposal=claim.additional_proposal, status__in=[
        'IN APPROVAL']).aggregate(Sum('additional_amount'))

    parked_amount2 = sum_parked_amount2.get(
        'amount__sum') if sum_parked_amount2.get('amount__sum') else 0
    additional_parked_amount2 = sum_add_parked_amount2.get(
        'additional_amount__sum') if sum_add_parked_amount2.get('additional_amount__sum') else 0

    proposal.proposal_claim = amount + additional_amount
    proposal.parked_claim = parked_amount + additional_parked_amount
    proposal.balance = proposal.total_cost - proposal.proposal_claim
    proposal.save()

    proposal2 = Proposal.objects.get(
        proposal_id=claim.additional_proposal) if claim.additional_proposal else None
    if proposal2:
        proposal2.proposal_claim = amount2 + additional_amount2
        proposal2.parked_claim = parked_amount2 + additional_parked_amount2
        proposal2.balance = proposal2.total_cost - proposal2.proposal_claim
        proposal2.save()

    mail_sent = ClaimRelease.objects.filter(
        claim_id=_id).order_by('sequence').values_list('mail_sent', flat=True)
    if mail_sent[0] == False:
        email = ClaimRelease.objects.filter(
            claim_id=_id).order_by('sequence').values_list('claim_approval_email', flat=True)
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT username FROM apps_claimrelease INNER JOIN apps_user ON apps_claimrelease.claim_approval_id = apps_user.user_id WHERE claim_id = '" + str(_id) + "' AND claim_approval_status = 'N' ORDER BY sequence LIMIT 1")
            approver = cursor.fetchone()

        subject = 'Claim Approval'
        msg = 'Dear ' + approver[0] + ',\n\nYou have a new claim to approve. Please check your claim release list.\n\n' + \
            'Click this link to approve, revise, return or reject this claim.\n' + host.url + 'claim_release/view/' + str(_id) + '/0/' + \
            '\n\nThank you.'
        send_email(subject, msg, [email[0]])

        # update mail sent to true
        release = ClaimRelease.objects.filter(
            claim_id=_id).order_by('sequence').first()
        release.mail_sent = True
        release.save()

    return HttpResponseRedirect(reverse('claim-index', args=['inapproval', ]))


@login_required(login_url='/login/')
@role_required(allowed_roles='CLAIM')
def claim_view(request, _tab, _id, _from_yr, _from_mo, _to_yr, _to_mo, _distributor):
    claim = Claim.objects.get(claim_id=_id)
    form = FormClaimView(instance=claim)
    program = Program.objects.get(program_id=claim.program_id)

    highest_approval = ClaimRelease.objects.filter(
        claim_id=_id, limit__gt=claim.total_claim).aggregate(Min('sequence')) if ClaimRelease.objects.filter(claim_id=_id, limit__gt=claim.total_claim).count() > 0 else ClaimRelease.objects.filter(claim_id=_id).aggregate(Max('sequence'))
    highest_sequence = highest_approval.get('sequence__min') if highest_approval.get(
        'sequence__min') else highest_approval.get('sequence__max') + 1
    if highest_sequence:
        approval = ClaimRelease.objects.filter(
            claim_id=_id, sequence__lt=highest_sequence).order_by('sequence')
    else:
        approval = ClaimRelease.objects.filter(
            claim_id=_id).order_by('sequence')
    rejector = ClaimRelease.objects.filter(
        claim_id=_id, claim_approval_status='N').order_by('sequence').first() if claim.status == 'REJECTED' else None

    context = {
        'data': claim,
        'form': form,
        'tab': _tab,
        'program': program,
        'approval': approval,
        'rejector': rejector,
        'status': claim.status,
        'from_yr': _from_yr,
        'from_mo': _from_mo,
        'to_yr': _to_yr,
        'to_mo': _to_mo,
        'distributor': _distributor,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'claim_archive' if _tab == 'reject' else 'claim',
        'group_segment': 'claim',
        'crud': 'view',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list(
            'menu_id', flat=True),
        'btn': Auth.objects.get(
            user_id=request.user.user_id, menu_id='CLAIM') if not request.user.is_superuser else Auth.objects.all(),
    }

    return render(request, 'home/claim_view.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='CLAIM')
def claim_update(request, _tab, _id):
    claim = Claim.objects.get(claim_id=_id)
    proposals = Proposal.objects.filter(
        status='OPEN', area=claim.area, balance__gt=0, budget__budget_distributor=claim.proposal.budget.budget_distributor).order_by('-proposal_id')
    program = Program.objects.get(program_id=claim.program_id)
    proposal = Proposal.objects.get(proposal_id=program.proposal.proposal_id)

    print(request.POST.get('add_proposal'))
    message = '0'
    add_prop = '0'
    difference = 0
    add_proposals = None
    add_prop_before = claim.additional_proposal
    amount_before = claim.amount

    if request.POST:
        form = FormClaimUpdate(request.POST, request.FILES, instance=claim)
        difference = int(request.POST.get('amount')) - \
            (int(proposal.balance) + int(claim.amount))
        if int(request.POST.get('amount')) > (int(program.proposal.balance) + int(claim.amount)) and request.POST.get('add_proposals') == '':
            add_prop = '1'
            message = 'Claim amount is greater than proposal balance.'
            add_proposals = Proposal.objects.filter(
                status='OPEN', balance__gte=difference, reference=program.proposal_id).order_by('-proposal_id')
        else:
            if form.is_valid():
                draft = form.save(commit=False)
                draft.total_claim = Decimal(request.POST.get('amount'))
                draft.amount = proposal.balance + amount_before if request.POST.get(
                    'add_proposals') else Decimal(request.POST.get('amount'))
                if int(request.POST.get('amount')) > (int(proposal.balance) + int(amount_before)):
                    draft.additional_proposal = request.POST.get(
                        'add_proposals')
                else:
                    draft.additional_proposal = ''
                draft.additional_amount = difference if request.POST.get(
                    'add_proposals') else 0
                draft.is_tax = True if request.POST.get('is_tax') else False
                draft.save()

                # sum_amount = Claim.objects.filter(
                #     proposal_id=draft.proposal_id).exclude(status__in=['REJECTED']).aggregate(Sum('amount'))
                # sum_add_amount = Claim.objects.filter(additional_proposal=draft.proposal_id).exclude(
                #     status__in=['REJECTED']).aggregate(Sum('additional_amount'))

                # sum_amount2 = Claim.objects.filter(
                #     proposal_id=draft.additional_proposal).exclude(status__in=['REJECTED']).aggregate(Sum('amount'))
                # sum_add_amount2 = Claim.objects.filter(additional_proposal=draft.additional_proposal).exclude(status__in=['REJECTED']).aggregate(
                #     Sum('additional_amount'))

                # amount = sum_amount.get('amount__sum') if sum_amount.get(
                #     'amount__sum') else 0
                # additional_amount = sum_add_amount.get(
                #     'additional_amount__sum') if sum_add_amount.get('additional_amount__sum') else 0

                # amount2 = sum_amount2.get('amount__sum') if sum_amount2.get(
                #     'amount__sum') else 0
                # additional_amount2 = sum_add_amount2.get('additional_amount__sum') if sum_add_amount2.get(
                #     'additional_amount__sum') else 0

                # # update parked claim
                # sum_parked_amount = Claim.objects.filter(
                #     proposal_id=draft.proposal_id, status__in=['DRAFT', 'IN APPROVAL']).aggregate(Sum('amount'))
                # sum_add_parked_amount = Claim.objects.filter(additional_proposal=draft.proposal_id, status__in=[
                #                                              'DRAFT', 'IN APPROVAL']).aggregate(Sum('additional_amount'))

                # parked_amount = sum_parked_amount.get(
                #     'amount__sum') if sum_parked_amount.get('amount__sum') else 0
                # additional_parked_amount = sum_add_parked_amount.get(
                #     'additional_amount__sum') if sum_add_parked_amount.get('additional_amount__sum') else 0

                # sum_parked_amount2 = Claim.objects.filter(proposal_id=draft.additional_proposal, status__in=[
                #                                           'DRAFT', 'IN APPROVAL']).aggregate(Sum('amount'))
                # sum_add_parked_amount2 = Claim.objects.filter(additional_proposal=draft.additional_proposal, status__in=[
                #                                               'DRAFT', 'IN APPROVAL']).aggregate(Sum('additional_amount'))

                # parked_amount2 = sum_parked_amount2.get(
                #     'amount__sum') if sum_parked_amount2.get('amount__sum') else 0
                # additional_parked_amount2 = sum_add_parked_amount2.get(
                #     'additional_amount__sum') if sum_add_parked_amount2.get('additional_amount__sum') else 0

                # proposal.proposal_claim = amount + additional_amount
                # proposal.parked_claim = parked_amount + additional_parked_amount
                # proposal.balance = proposal.total_cost - proposal.proposal_claim
                # proposal.save()

                # proposal2 = Proposal.objects.get(
                #     proposal_id=draft.additional_proposal) if draft.additional_proposal else None
                # if proposal2:
                #     proposal2.proposal_claim = amount2 + additional_amount2
                #     proposal2.parked_claim = parked_amount2 + additional_parked_amount2
                #     proposal2.balance = proposal2.total_cost - proposal2.proposal_claim
                #     proposal2.save()
                # else:
                #     proposal3 = Proposal.objects.get(
                #         proposal_id=add_prop_before) if add_prop_before else None
                #     if proposal3:
                #         proposal3.proposal_claim = amount2 + additional_amount2
                #         proposal3.parked_claim = parked_amount2 + additional_parked_amount2
                #         proposal3.balance = proposal3.total_cost - proposal3.proposal_claim
                #         proposal3.save()

                return HttpResponseRedirect(reverse('claim-view', args=[_tab, _id, '0', '0', '0', '0', 'all']))
    else:
        form = FormClaimUpdate(instance=claim)

    err = form.errors
    context = {
        'form': form,
        'data': claim,
        'program': program,
        'proposals': proposals,
        'add_proposals': add_proposals,
        'add_prop': add_prop,
        'difference': difference,
        'tab': _tab,
        'message': message,
        'err': err,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'claim',
        'group_segment': 'claim',
        'crud': 'update',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list(
            'menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id,
                                menu_id='CLAIM') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/claim_view.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='CLAIM')
def claim_delete(request, _tab, _id):
    claim = Claim.objects.get(claim_id=_id)
    proposal = Proposal.objects.get(proposal_id=claim.proposal.proposal_id)
    claim.delete()

    # sum_amount = Claim.objects.filter(
    #     proposal_id=claim.proposal_id).exclude(status__in=['REJECTED']).aggregate(Sum('amount'))
    # sum_add_amount = Claim.objects.filter(additional_proposal=claim.proposal_id).exclude(
    #     status__in=['REJECTED']).aggregate(Sum('additional_amount'))

    # sum_amount2 = Claim.objects.filter(
    #     proposal_id=claim.additional_proposal).exclude(status__in=['REJECTED']).aggregate(Sum('amount'))
    # sum_add_amount2 = Claim.objects.filter(additional_proposal=claim.additional_proposal).exclude(status__in=['REJECTED']).aggregate(
    #     Sum('additional_amount'))

    # amount = sum_amount.get('amount__sum') if sum_amount.get(
    #     'amount__sum') else 0
    # additional_amount = sum_add_amount.get(
    #     'additional_amount__sum') if sum_add_amount.get('additional_amount__sum') else 0

    # amount2 = sum_amount2.get('amount__sum') if sum_amount2.get(
    #     'amount__sum') else 0
    # additional_amount2 = sum_add_amount2.get('additional_amount__sum') if sum_add_amount2.get(
    #     'additional_amount__sum') else 0

    # # update parked claim
    # sum_parked_amount = Claim.objects.filter(
    #     proposal_id=claim.proposal_id, status__in=['DRAFT', 'IN APPROVAL']).aggregate(Sum('amount'))
    # sum_add_parked_amount = Claim.objects.filter(additional_proposal=claim.proposal_id, status__in=[
    #     'DRAFT', 'IN APPROVAL']).aggregate(Sum('additional_amount'))

    # parked_amount = sum_parked_amount.get(
    #     'amount__sum') if sum_parked_amount.get('amount__sum') else 0
    # additional_parked_amount = sum_add_parked_amount.get(
    #     'additional_amount__sum') if sum_add_parked_amount.get('additional_amount__sum') else 0

    # sum_parked_amount2 = Claim.objects.filter(proposal_id=claim.additional_proposal, status__in=[
    #     'DRAFT', 'IN APPROVAL']).aggregate(Sum('amount'))
    # sum_add_parked_amount2 = Claim.objects.filter(additional_proposal=claim.additional_proposal, status__in=[
    #     'DRAFT', 'IN APPROVAL']).aggregate(Sum('additional_amount'))

    # parked_amount2 = sum_parked_amount2.get(
    #     'amount__sum') if sum_parked_amount2.get('amount__sum') else 0
    # additional_parked_amount2 = sum_add_parked_amount2.get(
    #     'additional_amount__sum') if sum_add_parked_amount2.get('additional_amount__sum') else 0

    # proposal.proposal_claim = amount + additional_amount
    # proposal.parked_claim = parked_amount + additional_parked_amount
    # proposal.balance = proposal.total_cost - proposal.proposal_claim
    # proposal.save()

    # proposal2 = Proposal.objects.get(
    #     proposal_id=claim.additional_proposal) if claim.additional_proposal else None
    # if proposal2:
    #     proposal2.proposal_claim = amount2 + additional_amount2
    #     proposal2.parked_claim = parked_amount2 + additional_parked_amount2
    #     proposal2.balance = proposal2.total_cost - proposal2.proposal_claim
    #     proposal2.save()

    return HttpResponseRedirect(reverse('claim-index', args=[_tab, ]))


@login_required(login_url='/login/')
@role_required(allowed_roles='CLAIM-RELEASE')
def claim_release_index(request):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT apps_claim.claim_id, apps_claim.claim_date, apps_distributor.distributor_name, apps_proposal.channel, apps_claim.total_claim, apps_claim.status, apps_claimrelease.sequence FROM apps_distributor INNER JOIN apps_budget ON apps_distributor.distributor_id = apps_budget.budget_distributor_id INNER JOIN apps_proposal ON apps_budget.budget_id = apps_proposal.budget_id INNER JOIN apps_claim ON apps_proposal.proposal_id = apps_claim.proposal_id INNER JOIN apps_claimrelease ON apps_claim.claim_id = apps_claimrelease.claim_id INNER JOIN (SELECT claim_id, MIN(sequence) AS seq FROM apps_claimrelease WHERE claim_approval_status = 'N' AND approve = 1 GROUP BY claim_id ORDER BY sequence ASC) AS q_group ON apps_claimrelease.claim_id = q_group.claim_id AND apps_claimrelease.sequence = q_group.seq WHERE (apps_claim.status = 'PENDING' OR apps_claim.status = 'IN APPROVAL') AND apps_claimrelease.claim_approval_id = '" + str(request.user.user_id) + "'")
        release = cursor.fetchall()

    context = {
        'data': release,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'claim_release',
        'group_segment': 'claim',
        'crud': 'index',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='CLAIM-RELEASE') if not request.user.is_superuser else Auth.objects.all(),
    }

    return render(request, 'home/claim_release_index.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='CLAIM-RELEASE')
def claim_release_view(request, _id, _is_revise):
    claim = Claim.objects.get(claim_id=_id)
    form = FormClaimView(instance=claim)
    approved = ClaimRelease.objects.get(
        claim_id=_id, claim_approval_id=request.user.user_id).claim_approval_status
    program = Program.objects.get(program_id=claim.program_id)

    context = {
        'form': form,
        'data': claim,
        'approved': approved,
        'program': program,
        'is_revise': _is_revise,
        'status': claim.status,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'claim_release',
        'group_segment': 'claim',
        'crud': 'view',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='CLAIM-RELEASE') if not request.user.is_superuser else Auth.objects.all(),
        'btn_release': ClaimRelease.objects.get(claim_id=_id, claim_approval_id=request.user.user_id),
    }
    return render(request, 'home/claim_release_view.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='CLAIM-RELEASE')
def claim_release_update(request, _id):
    claim = Claim.objects.get(claim_id=_id)
    program = Program.objects.get(program_id=claim.program_id)
    proposal = Proposal.objects.get(proposal_id=claim.proposal.proposal_id)
    proposals = Proposal.objects.filter(
        status='OPEN', area=claim.area, balance__gt=0, budget__budget_distributor=claim.proposal.budget.budget_distributor).order_by('-proposal_id')
    message = '0'
    add_prop = '0'
    difference = 0
    revise_note = ''
    add_proposals = None
    add_prop_before = claim.additional_proposal
    amount_before = claim.amount
    _invoice = claim.invoice
    _invoice_date = claim.invoice_date
    _due_date = claim.due_date
    _amount = claim.amount
    _is_tax = claim.is_tax
    _remarks = claim.remarks
    _depo = claim.depo
    _claim_period = claim.claim_period
    _additional_proposal = claim.additional_proposal
    _additional_amount = claim.additional_amount

    if request.POST:
        form = FormClaimUpdate(
            request.POST, request.FILES, instance=claim)
        difference = int(request.POST.get('amount')) - \
            (int(proposal.balance) + int(claim.amount))
        if int(request.POST.get('amount')) > (int(proposal.balance) + int(claim.amount)) and request.POST.get('add_proposals') == '':
            add_prop = '1'
            revise_note = request.POST.get('id_revise-note')
            message = 'Claim amount is greater than proposal balance.'
            add_proposals = Proposal.objects.filter(
                status='OPEN', balance__gte=difference, reference=program.proposal_id).order_by('-proposal_id')
        else:
            if form.is_valid():
                parent = form.save(commit=False)
                invoice = _invoice if form.cleaned_data['invoice'] != _invoice else None
                invoice_date = _invoice_date if form.cleaned_data[
                    'invoice_date'] != _invoice_date else None
                due_date = _due_date if form.cleaned_data['due_date'] != _due_date else None
                claim_amount = _amount if form.cleaned_data['amount'] != _amount else None
                is_tax = _is_tax if request.POST.get(
                    'is_tax') != _is_tax else False
                remarks = _remarks if form.cleaned_data['remarks'] != _remarks else None
                depo = _depo if form.cleaned_data['depo'] != _depo else None
                claim_period = _claim_period if form.cleaned_data[
                    'claim_period'] != _claim_period else None
                additional_proposal = _additional_proposal if request.POST.get(
                    'add_proposals') != _additional_proposal else None
                add_amount = _additional_amount if request.POST.get(
                    'add_amount') != _additional_amount else None
                parent.total_claim = Decimal(request.POST.get('amount'))
                parent.amount = proposal.balance + amount_before if request.POST.get(
                    'add_proposals') else Decimal(request.POST.get('amount'))
                if int(request.POST.get('amount')) > (int(proposal.balance) + int(amount_before)):
                    parent.additional_proposal = request.POST.get(
                        'add_proposals')
                else:
                    parent.additional_proposal = ''
                parent.additional_amount = difference if request.POST.get(
                    'add_proposals') else 0
                parent.is_tax = True if request.POST.get('is_tax') else False
                parent.save()

                sum_amount = Claim.objects.filter(
                    proposal_id=parent.proposal_id).exclude(status__in=['DRAFT', 'REJECTED']).aggregate(Sum('amount'))
                sum_add_amount = Claim.objects.filter(additional_proposal=parent.proposal_id).exclude(
                    status__in=['DRAFT', 'REJECTED']).aggregate(Sum('additional_amount'))

                sum_amount2 = Claim.objects.filter(
                    proposal_id=parent.additional_proposal).exclude(status__in=['DRAFT', 'REJECTED']).aggregate(Sum('amount'))
                sum_add_amount2 = Claim.objects.filter(additional_proposal=parent.additional_proposal).exclude(status__in=['DRAFT', 'REJECTED']).aggregate(
                    Sum('additional_amount'))

                amount = sum_amount.get('amount__sum') if sum_amount.get(
                    'amount__sum') else 0
                additional_amount = sum_add_amount.get(
                    'additional_amount__sum') if sum_add_amount.get('additional_amount__sum') else 0

                amount2 = sum_amount2.get('amount__sum') if sum_amount2.get(
                    'amount__sum') else 0
                additional_amount2 = sum_add_amount2.get('additional_amount__sum') if sum_add_amount2.get(
                    'additional_amount__sum') else 0

                # update parked claim
                sum_parked_amount = Claim.objects.filter(
                    proposal_id=parent.proposal_id, status__in=['IN APPROVAL']).aggregate(Sum('amount'))
                sum_add_parked_amount = Claim.objects.filter(additional_proposal=parent.proposal_id, status__in=[
                                                             'IN APPROVAL']).aggregate(Sum('additional_amount'))

                parked_amount = sum_parked_amount.get(
                    'amount__sum') if sum_parked_amount.get('amount__sum') else 0
                additional_parked_amount = sum_add_parked_amount.get(
                    'additional_amount__sum') if sum_add_parked_amount.get('additional_amount__sum') else 0

                sum_parked_amount2 = Claim.objects.filter(proposal_id=parent.additional_proposal, status__in=[
                                                          'IN APPROVAL']).aggregate(Sum('amount'))
                sum_add_parked_amount2 = Claim.objects.filter(additional_proposal=parent.additional_proposal, status__in=[
                                                              'IN APPROVAL']).aggregate(Sum('additional_amount'))

                parked_amount2 = sum_parked_amount2.get(
                    'amount__sum') if sum_parked_amount2.get('amount__sum') else 0
                additional_parked_amount2 = sum_add_parked_amount2.get(
                    'additional_amount__sum') if sum_add_parked_amount2.get('additional_amount__sum') else 0

                proposal.proposal_claim = amount + additional_amount
                proposal.parked_claim = parked_amount + additional_parked_amount
                proposal.balance = proposal.total_cost - proposal.proposal_claim
                proposal.save()

                proposal2 = Proposal.objects.get(
                    proposal_id=parent.additional_proposal) if parent.additional_proposal else None
                if proposal2:
                    proposal2.proposal_claim = amount2 + additional_amount2
                    proposal2.parked_claim = parked_amount2 + additional_parked_amount2
                    proposal2.balance = proposal2.total_cost - proposal2.proposal_claim
                    proposal2.save()
                else:
                    proposal3 = Proposal.objects.get(
                        proposal_id=add_prop_before) if add_prop_before else None
                    if proposal3:
                        proposal3.proposal_claim = amount2 + additional_amount2
                        proposal3.parked_claim = parked_amount2 + additional_parked_amount2
                        proposal3.balance = proposal3.total_cost - proposal3.proposal_claim
                        proposal3.save()

                recipients = []

                release = ClaimRelease.objects.get(
                    claim_id=_id, claim_approval_id=request.user.user_id)
                release.revise_note = request.POST.get('id_revise-note')
                release.save()

                with connection.cursor() as cursor:
                    cursor.execute(
                        "SELECT claim_id, email FROM apps_claim INNER JOIN apps_user ON apps_claim.entry_by = apps_user.user_id WHERE claim_id = '" + str(_id) + "'")
                    entry_mail = cursor.fetchone()
                    if entry_mail:
                        recipients.append(entry_mail[1])

                    cursor.execute(
                        "SELECT claim_id, email FROM apps_claim INNER JOIN apps_user ON apps_claim.update_by = apps_user.user_id WHERE claim_id = '" + str(_id) + "'")
                    update_mail = cursor.fetchone()
                    if update_mail:
                        recipients.append(update_mail[1])

                    cursor.execute(
                        "SELECT claim_id, claim_approval_email FROM apps_claimrelease WHERE claim_id = '" + str(_id) + "' AND claim_approval_status = 'Y'")
                    approver_mail = cursor.fetchall()
                    for mail in approver_mail:
                        recipients.append(mail[1])

                subject = 'Claim Revised'
                msg = 'Dear All,\n\nThe following is revised claim for Claim No. ' + \
                    str(_id) + ':\n'
                if invoice:
                    msg += '\nBEFORE\n'
                    msg += 'Invoice: ' + str(invoice) + '\n'
                    msg += '\nAFTER\n'
                    msg += 'Invoice: ' + \
                        form.cleaned_data['invoice'] + '\n'

                if invoice_date:
                    msg += '\nBEFORE\n'
                    msg += 'Invoice Date: ' + \
                        invoice_date.strftime('%d %b %Y') + '\n'
                    msg += '\nAFTER\n'
                    msg += 'Invoice Date: ' + \
                        form.cleaned_data['invoice_date'].strftime(
                            '%d %b %Y') + '\n'

                if due_date:
                    msg += '\nBEFORE\n'
                    msg += 'Due Date: ' + \
                        due_date.strftime('%d %b %Y') + '\n'
                    msg += '\nAFTER\n'
                    msg += 'Due Date: ' + \
                        form.cleaned_data['due_date'].strftime(
                            '%d %b %Y') + '\n'

                if claim_amount:
                    msg += '\nBEFORE\n'
                    msg += 'Amount: ' + '{:,}'.format(claim_amount) + '\n'
                    msg += '\nAFTER\n'
                    msg += 'Amount: ' + \
                        '{:,}'.format(form.cleaned_data['amount']) + '\n'

                if is_tax:
                    msg += '\nBEFORE\n'
                    msg += 'Using Tax: ' + str(is_tax) + '\n'
                    msg += '\nAFTER\n'
                    msg += 'Using Tax: ' + \
                        str(request.POST.get('is_tax')) + '\n'

                if remarks:
                    msg += '\nBEFORE\n'
                    msg += 'Invoice Description: ' + str(remarks) + '\n'
                    msg += '\nAFTER\n'
                    msg += 'Invoice Description: ' + \
                        form.cleaned_data['remarks'] + '\n'

                if depo:
                    msg += '\nBEFORE\n'
                    msg += 'Depo: ' + str(depo) + '\n'
                    msg += '\nAFTER\n'
                    msg += 'Depo: ' + \
                        form.cleaned_data['depo'] + '\n'

                if claim_period:
                    msg += '\nBEFORE\n'
                    msg += 'Claim Period: ' + str(claim_period) + '\n'
                    msg += '\nAFTER\n'
                    msg += 'Claim Period: ' + \
                        form.cleaned_data['claim_period'] + '\n'

                if additional_proposal:
                    msg += '\nBEFORE\n'
                    msg += 'Additional Proposal: ' + \
                        str(additional_proposal) + '\n'
                    msg += '\nAFTER\n'
                    msg += 'Additional Proposal: ' + \
                        request.POST.get('add_proposals') + '\n'

                if add_amount:
                    msg += '\nBEFORE\n'
                    msg += 'Additional Amount: ' + \
                        str(add_amount) + '\n'
                    msg += '\nAFTER\n'
                    msg += 'Additional Amount: ' + \
                        request.POST.get('add_amount') + '\n'

                msg += '\nNote: ' + \
                    str(release.revise_note) + '\n\nClick the following link to view the claim.\n' + host.url + 'claim/view/inapproval/' + str(_id) + '/' + \
                    '\n\nThank you.'

                recipient_list = list(dict.fromkeys(recipients))
                send_email(subject, msg, recipient_list)

                return HttpResponseRedirect(reverse('claim-release-view', args=[_id, 0]))
    else:
        form = FormClaimUpdate(instance=claim)

    # msg = form.errors
    context = {
        'form': form,
        'data': claim,
        'program': program,
        'message': message,
        'add_prop': add_prop,
        'revise_note': revise_note,
        'add_proposals': add_proposals,
        'proposals': proposals,
        'difference': difference,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'claim_release',
        'group_segment': 'claim',
        'crud': 'update',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list(
            'menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id,
                                menu_id='CLAIM-RELEASE') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/claim_release_view.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='CLAIM-RELEASE')
def claim_release_approve(request, _id):
    claim = Claim.objects.get(claim_id=_id)
    release = ClaimRelease.objects.get(
        claim_id=_id, claim_approval_id=request.user.user_id)
    release.claim_approval_status = 'Y'
    release.claim_approval_date = timezone.now()
    release.save()

    highest_approval = ClaimRelease.objects.filter(
        claim_id=_id, limit__gt=claim.total_claim).aggregate(Min('sequence')) if ClaimRelease.objects.filter(claim_id=_id, limit__gt=claim.total_claim).count() > 0 else ClaimRelease.objects.filter(claim_id=_id).aggregate(Max('sequence'))
    highest_sequence = highest_approval.get('sequence__min') if highest_approval.get(
        'sequence__min') else highest_approval.get('sequence__max') + 1
    if highest_sequence:
        approval = ClaimRelease.objects.filter(
            claim_id=_id, sequence__lt=highest_sequence).order_by('sequence').last()
    else:
        approval = ClaimRelease.objects.filter(
            claim_id=_id).order_by('sequence').last()

    if release.sequence == approval.sequence:
        claim.status = 'OPEN'
        
        recipients = []

        maker = claim.entry_by
        maker_mail = User.objects.get(user_id=maker).email
        recipients.append(maker_mail)

        approvers = ClaimRelease.objects.filter(
            claim_id=_id, notif=True, claim_approval_status='Y')
        for i in approvers:
            recipients.append(i.claim_approval_email)

        subject = 'Claim Approved'
        msg = 'Dear All,\n\nClaim No. ' + str(_id) + ' has been approved.\n\nClick the following link to view the claim.\n' + host.url + 'claim/view/open/' + str(_id) + \
            '\n\nThank you.'
        recipient_list = list(dict.fromkeys(recipients))
    else:
        claim.status = 'IN APPROVAL'
        
        email = ClaimRelease.objects.filter(claim_id=_id, claim_approval_status='N').order_by(
            'sequence').values_list('claim_approval_email', flat=True)
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT claim_approval_name FROM apps_claimrelease WHERE claim_id = '" + str(_id) + "' AND claim_approval_status = 'N' ORDER BY sequence LIMIT 1")
            approver = cursor.fetchone()

        subject = 'Claim Approval'
        msg = 'Dear ' + approver[0] + ',\n\nYou have a new claim to approve. Please check your claim release list.\n\n' + \
            'Click this link to approve, revise, return or reject this claim.\n' + host.url + 'claim_release/view/' + str(_id) + '/0/' + \
            '\n\nThank you.'

    claim.save()

    sum_amount = Claim.objects.filter(
        proposal_id=claim.proposal_id).exclude(status__in=['DRAFT', 'REJECTED']).aggregate(Sum('amount'))
    sum_add_amount = Claim.objects.filter(additional_proposal=claim.proposal_id).exclude(
        status__in=['DRAFT', 'REJECTED']).aggregate(Sum('additional_amount'))

    sum_amount2 = Claim.objects.filter(
        proposal_id=claim.additional_proposal).exclude(status__in=['DRAFT', 'REJECTED']).aggregate(Sum('amount'))
    sum_add_amount2 = Claim.objects.filter(additional_proposal=claim.additional_proposal).exclude(status__in=['DRAFT', 'REJECTED']).aggregate(
        Sum('additional_amount'))

    amount = sum_amount.get('amount__sum') if sum_amount.get(
        'amount__sum') else 0
    additional_amount = sum_add_amount.get(
        'additional_amount__sum') if sum_add_amount.get('additional_amount__sum') else 0

    amount2 = sum_amount2.get('amount__sum') if sum_amount2.get(
        'amount__sum') else 0
    additional_amount2 = sum_add_amount2.get('additional_amount__sum') if sum_add_amount2.get(
        'additional_amount__sum') else 0

    # update parked claim
    sum_parked_amount = Claim.objects.filter(
        proposal_id=claim.proposal_id, status__in=['IN APPROVAL']).aggregate(Sum('amount'))
    sum_add_parked_amount = Claim.objects.filter(additional_proposal=claim.proposal_id, status__in=[
        'IN APPROVAL']).aggregate(Sum('additional_amount'))

    parked_amount = sum_parked_amount.get(
        'amount__sum') if sum_parked_amount.get('amount__sum') else 0
    additional_parked_amount = sum_add_parked_amount.get(
        'additional_amount__sum') if sum_add_parked_amount.get('additional_amount__sum') else 0

    sum_parked_amount2 = Claim.objects.filter(proposal_id=claim.additional_proposal, status__in=[
        'IN APPROVAL']).aggregate(Sum('amount'))
    sum_add_parked_amount2 = Claim.objects.filter(additional_proposal=claim.additional_proposal, status__in=[
        'IN APPROVAL']).aggregate(Sum('additional_amount'))

    parked_amount2 = sum_parked_amount2.get(
        'amount__sum') if sum_parked_amount2.get('amount__sum') else 0
    additional_parked_amount2 = sum_add_parked_amount2.get(
        'additional_amount__sum') if sum_add_parked_amount2.get('additional_amount__sum') else 0

    proposal = Proposal.objects.get(proposal_id=claim.proposal_id)

    proposal.proposal_claim = amount + additional_amount
    proposal.parked_claim = parked_amount + additional_parked_amount
    proposal.balance = proposal.total_cost - proposal.proposal_claim
    proposal.save()

    proposal2 = Proposal.objects.get(
        proposal_id=claim.additional_proposal) if claim.additional_proposal else None
    if proposal2:
        proposal2.proposal_claim = amount2 + additional_amount2
        proposal2.parked_claim = parked_amount2 + additional_parked_amount2
        proposal2.balance = proposal2.total_cost - proposal2.proposal_claim
        proposal2.save()

    if release.sequence == approval.sequence:
        send_email(subject, msg, recipient_list)
    else:
        send_email(subject, msg, [email[0]])

    return HttpResponseRedirect(reverse('claim-release-index'))


@login_required(login_url='/login/')
@role_required(allowed_roles='CLAIM-RELEASE')
def claim_release_bulk_approve(request):
    claim_nos = request.GET.get('claim_nos')
    _ids = claim_nos.split(',')
    for _id in _ids:
        claim = Claim.objects.get(claim_id=_id)
        release = ClaimRelease.objects.get(
            claim_id=_id, claim_approval_id=request.user.user_id)
        release.claim_approval_status = 'Y'
        release.claim_approval_date = timezone.now()
        release.save()

        highest_approval = ClaimRelease.objects.filter(
            claim_id=_id, limit__gt=claim.total_claim).aggregate(Min('sequence')) if ClaimRelease.objects.filter(claim_id=_id, limit__gt=claim.total_claim).count() > 0 else ClaimRelease.objects.filter(claim_id=_id).aggregate(Max('sequence'))
        highest_sequence = highest_approval.get('sequence__min') if highest_approval.get(
            'sequence__min') else highest_approval.get('sequence__max') + 1
        if highest_sequence:
            approval = ClaimRelease.objects.filter(
                claim_id=_id, sequence__lt=highest_sequence).order_by('sequence').last()
        else:
            approval = ClaimRelease.objects.filter(
                claim_id=_id).order_by('sequence').last()

        if release.sequence == approval.sequence:
            claim.status = 'OPEN'
        else:
            claim.status = 'IN APPROVAL'

        claim.save()

        sum_amount = Claim.objects.filter(
            proposal_id=claim.proposal_id).exclude(status__in=['DRAFT', 'REJECTED']).aggregate(Sum('amount'))
        sum_add_amount = Claim.objects.filter(additional_proposal=claim.proposal_id).exclude(
            status__in=['DRAFT', 'REJECTED']).aggregate(Sum('additional_amount'))

        sum_amount2 = Claim.objects.filter(
            proposal_id=claim.additional_proposal).exclude(status__in=['DRAFT', 'REJECTED']).aggregate(Sum('amount'))
        sum_add_amount2 = Claim.objects.filter(additional_proposal=claim.additional_proposal).exclude(status__in=['DRAFT', 'REJECTED']).aggregate(
            Sum('additional_amount'))

        amount = sum_amount.get('amount__sum') if sum_amount.get(
            'amount__sum') else 0
        additional_amount = sum_add_amount.get(
            'additional_amount__sum') if sum_add_amount.get('additional_amount__sum') else 0

        amount2 = sum_amount2.get('amount__sum') if sum_amount2.get(
            'amount__sum') else 0
        additional_amount2 = sum_add_amount2.get('additional_amount__sum') if sum_add_amount2.get(
            'additional_amount__sum') else 0

        # update parked claim
        sum_parked_amount = Claim.objects.filter(
            proposal_id=claim.proposal_id, status__in=['IN APPROVAL']).aggregate(Sum('amount'))
        sum_add_parked_amount = Claim.objects.filter(additional_proposal=claim.proposal_id, status__in=[
            'IN APPROVAL']).aggregate(Sum('additional_amount'))

        parked_amount = sum_parked_amount.get(
            'amount__sum') if sum_parked_amount.get('amount__sum') else 0
        additional_parked_amount = sum_add_parked_amount.get(
            'additional_amount__sum') if sum_add_parked_amount.get('additional_amount__sum') else 0

        sum_parked_amount2 = Claim.objects.filter(proposal_id=claim.additional_proposal, status__in=[
            'IN APPROVAL']).aggregate(Sum('amount'))
        sum_add_parked_amount2 = Claim.objects.filter(additional_proposal=claim.additional_proposal, status__in=[
            'IN APPROVAL']).aggregate(Sum('additional_amount'))

        parked_amount2 = sum_parked_amount2.get(
            'amount__sum') if sum_parked_amount2.get('amount__sum') else 0
        additional_parked_amount2 = sum_add_parked_amount2.get(
            'additional_amount__sum') if sum_add_parked_amount2.get('additional_amount__sum') else 0

        proposal = Proposal.objects.get(proposal_id=claim.proposal_id)

        proposal.proposal_claim = amount + additional_amount
        proposal.parked_claim = parked_amount + additional_parked_amount
        proposal.balance = proposal.total_cost - proposal.proposal_claim
        proposal.save()

        proposal2 = Proposal.objects.get(
            proposal_id=claim.additional_proposal) if claim.additional_proposal else None
        if proposal2:
            proposal2.proposal_claim = amount2 + additional_amount2
            proposal2.parked_claim = parked_amount2 + additional_parked_amount2
            proposal2.balance = proposal2.total_cost - proposal2.proposal_claim
            proposal2.save()

        if release.sequence == approval.sequence:
            recipients = []

            maker = claim.entry_by
            maker_mail = User.objects.get(user_id=maker).email
            recipients.append(maker_mail)

            approvers = ClaimRelease.objects.filter(
                claim_id=_id, notif=True, claim_approval_status='Y')
            for i in approvers:
                recipients.append(i.claim_approval_email)

            subject = 'Claim Approved'
            msg = 'Dear All,\n\nClaim No. ' + str(_id) + ' has been approved.\n\nClick the following link to view the claim.\n' + host.url + 'claim/view/open/' + str(_id) + \
                '\n\nThank you.'
            recipient_list = list(dict.fromkeys(recipients))
            send_email(subject, msg, recipient_list)
        else:
            email = ClaimRelease.objects.filter(claim_id=_id, claim_approval_status='N').order_by(
                'sequence').values_list('claim_approval_email', flat=True)
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT claim_approval_name FROM apps_claimrelease WHERE claim_id = '" + str(_id) + "' AND claim_approval_status = 'N' ORDER BY sequence LIMIT 1")
                approver = cursor.fetchone()

            subject = 'Claim Approval'
            msg = 'Dear ' + approver[0] + ',\n\nYou have a new claim to approve. Please check your claim release list.\n\n' + \
                'Click this link to approve, revise, return or reject this claim.\n' + host.url + 'claim_release/view/' + str(_id) + '/0/' + \
                '\n\nThank you.'
            send_email(subject, msg, [email[0]])

    return HttpResponseRedirect(reverse('claim-release-index'))


@login_required(login_url='/login/')
@role_required(allowed_roles='CLAIM-RELEASE')
def claim_release_return(request, _id):
    claim = Claim.objects.get(claim_id=_id)
    program = Program.objects.get(program_id=claim.program_id)
    proposal = Proposal.objects.get(proposal_id=program.proposal.proposal_id)

    recipients = []
    draft = False

    try:
        return_to = ClaimRelease.objects.get(
            claim_id=_id, return_to=True, sequence__lt=ClaimRelease.objects.get(claim_id=_id, claim_approval_id=request.user.user_id).sequence)

        if return_to:
            approvers = ClaimRelease.objects.filter(
                claim_id=_id, sequence__gte=ClaimRelease.objects.get(claim_id=_id, return_to=True).sequence, sequence__lt=ClaimRelease.objects.get(claim_id=_id, claim_approval_id=request.user.user_id).sequence)
    except ClaimRelease.DoesNotExist:
        approvers = ClaimRelease.objects.filter(
            claim_id=_id, sequence__lte=ClaimRelease.objects.get(claim_id=_id, claim_approval_id=request.user.user_id).sequence)
        draft = True

    for i in approvers:
        recipients.append(i.claim_approval_email)
        i.claim_approval_status = 'N'
        i.claim_approval_date = None
        i.revise_note = ''
        i.return_note = ''
        i.reject_note = ''
        i.mail_sent = False
        i.save()

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT claim_id, email FROM apps_claim INNER JOIN apps_user ON apps_claim.entry_by = apps_user.user_id WHERE claim_id = '" + str(_id) + "'")
        entry_mail = cursor.fetchone()
        if entry_mail:
            recipients.append(entry_mail[1])

        cursor.execute(
            "SELECT claim_id, email FROM apps_claim INNER JOIN apps_user ON apps_claim.update_by = apps_user.user_id WHERE claim_id = '" + str(_id) + "'")
        update_mail = cursor.fetchone()
        if update_mail:
            recipients.append(update_mail[1])

    note = ClaimRelease.objects.get(
        claim_id=_id, claim_approval_id=request.user.user_id)
    note.return_note = request.POST.get('return_note')
    note.save()

    subject = 'Claim Returned'
    msg = 'Dear All,\n\nClaim No. ' + str(_id) + ' has been returned.\n\nNote: ' + \
        str(note.return_note) + \
        '\n\nClick the following link to revise the claim.\n'

    if draft:
        claim = Claim.objects.get(claim_id=_id)
        claim.status = 'DRAFT'
        claim.save()
        msg += host.url + 'claim/view/pending/' + str(_id) + \
            '\n\nThank you.'
    else:
        msg += host.url + 'claim_release/view/' + \
            str(_id) + '/0/\n\nThank you.'

    sum_amount = Claim.objects.filter(
        proposal_id=claim.proposal_id).exclude(status__in=['DRAFT', 'REJECTED']).aggregate(Sum('amount'))
    sum_add_amount = Claim.objects.filter(additional_proposal=claim.proposal_id).exclude(
        status__in=['DRAFT', 'REJECTED']).aggregate(Sum('additional_amount'))

    sum_amount2 = Claim.objects.filter(
        proposal_id=claim.additional_proposal).exclude(status__in=['DRAFT', 'REJECTED']).aggregate(Sum('amount'))
    sum_add_amount2 = Claim.objects.filter(additional_proposal=claim.additional_proposal).exclude(status__in=['DRAFT', 'REJECTED']).aggregate(
        Sum('additional_amount'))

    amount = sum_amount.get('amount__sum') if sum_amount.get(
        'amount__sum') else 0
    additional_amount = sum_add_amount.get(
        'additional_amount__sum') if sum_add_amount.get('additional_amount__sum') else 0

    amount2 = sum_amount2.get('amount__sum') if sum_amount2.get(
        'amount__sum') else 0
    additional_amount2 = sum_add_amount2.get('additional_amount__sum') if sum_add_amount2.get(
        'additional_amount__sum') else 0

    # update parked claim
    sum_parked_amount = Claim.objects.filter(
        proposal_id=claim.proposal_id, status__in=['IN APPROVAL']).aggregate(Sum('amount'))
    sum_add_parked_amount = Claim.objects.filter(additional_proposal=claim.proposal_id, status__in=[
        'IN APPROVAL']).aggregate(Sum('additional_amount'))

    parked_amount = sum_parked_amount.get(
        'amount__sum') if sum_parked_amount.get('amount__sum') else 0
    additional_parked_amount = sum_add_parked_amount.get(
        'additional_amount__sum') if sum_add_parked_amount.get('additional_amount__sum') else 0

    sum_parked_amount2 = Claim.objects.filter(proposal_id=claim.additional_proposal, status__in=[
        'IN APPROVAL']).aggregate(Sum('amount'))
    sum_add_parked_amount2 = Claim.objects.filter(additional_proposal=claim.additional_proposal, status__in=[
        'IN APPROVAL']).aggregate(Sum('additional_amount'))

    parked_amount2 = sum_parked_amount2.get(
        'amount__sum') if sum_parked_amount2.get('amount__sum') else 0
    additional_parked_amount2 = sum_add_parked_amount2.get(
        'additional_amount__sum') if sum_add_parked_amount2.get('additional_amount__sum') else 0

    proposal.proposal_claim = amount + additional_amount
    proposal.parked_claim = parked_amount + additional_parked_amount
    proposal.balance = proposal.total_cost - proposal.proposal_claim
    proposal.save()

    proposal2 = Proposal.objects.get(
        proposal_id=claim.additional_proposal) if claim.additional_proposal else None
    if proposal2:
        proposal2.proposal_claim = amount2 + additional_amount2
        proposal2.parked_claim = parked_amount2 + additional_parked_amount2
        proposal2.balance = proposal2.total_cost - proposal2.proposal_claim
        proposal2.save()

    recipient_list = list(dict.fromkeys(recipients))
    send_email(subject, msg, recipient_list)

    return HttpResponseRedirect(reverse('claim-release-index'))


@login_required(login_url='/login/')
@role_required(allowed_roles='CLAIM-RELEASE')
def claim_release_reject(request, _id):
    claim = Claim.objects.get(claim_id=_id)
    proposal = Proposal.objects.get(proposal_id=claim.proposal.proposal_id)
    recipients = []

    try:
        approvers = ClaimRelease.objects.filter(
            claim_id=_id, sequence__lt=ClaimRelease.objects.get(claim_id=_id, claim_approval_id=request.user.user_id).sequence)
    except ClaimRelease.DoesNotExist:
        pass

    for i in approvers:
        recipients.append(i.claim_approval_email)

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT claim_id, email FROM apps_claim INNER JOIN apps_user ON apps_claim.entry_by = apps_user.user_id WHERE claim_id = '" + str(_id) + "'")
        entry_mail = cursor.fetchone()
        if entry_mail:
            recipients.append(entry_mail[1])

        cursor.execute(
            "SELECT claim_id, email FROM apps_claim INNER JOIN apps_user ON apps_claim.update_by = apps_user.user_id WHERE claim_id = '" + str(_id) + "'")
        update_mail = cursor.fetchone()
        if update_mail:
            recipients.append(update_mail[1])

    note = ClaimRelease.objects.get(
        claim_id=_id, claim_approval_id=request.user.user_id)
    note.reject_note = request.POST.get('reject_note')
    note.save()

    subject = 'Claim Rejected'
    msg = 'Dear All,\n\nClaim No. ' + str(_id) + ' has been rejected.\n\nNote: ' + \
        str(note.reject_note) + \
        '\n\nClick the following link to see the claim.\n'

    claim = Claim.objects.get(claim_id=_id)
    claim.status = 'REJECTED'
    claim.save()

    sum_amount = Claim.objects.filter(
        proposal_id=claim.proposal_id).exclude(status__in=['DRAFT', 'REJECTED']).aggregate(Sum('amount'))
    sum_add_amount = Claim.objects.filter(additional_proposal=claim.proposal_id).exclude(
        status__in=['DRAFT', 'REJECTED']).aggregate(Sum('additional_amount'))

    sum_amount2 = Claim.objects.filter(
        proposal_id=claim.additional_proposal).exclude(status__in=['DRAFT', 'REJECTED']).aggregate(Sum('amount'))
    sum_add_amount2 = Claim.objects.filter(additional_proposal=claim.additional_proposal).exclude(status__in=['DRAFT', 'REJECTED']).aggregate(
        Sum('additional_amount'))

    amount = sum_amount.get('amount__sum') if sum_amount.get(
        'amount__sum') else 0
    additional_amount = sum_add_amount.get(
        'additional_amount__sum') if sum_add_amount.get('additional_amount__sum') else 0

    amount2 = sum_amount2.get('amount__sum') if sum_amount2.get(
        'amount__sum') else 0
    additional_amount2 = sum_add_amount2.get('additional_amount__sum') if sum_add_amount2.get(
        'additional_amount__sum') else 0

    # update parked claim
    sum_parked_amount = Claim.objects.filter(
        proposal_id=claim.proposal_id, status__in=['IN APPROVAL']).aggregate(Sum('amount'))
    sum_add_parked_amount = Claim.objects.filter(additional_proposal=claim.proposal_id, status__in=[
        'IN APPROVAL']).aggregate(Sum('additional_amount'))

    parked_amount = sum_parked_amount.get(
        'amount__sum') if sum_parked_amount.get('amount__sum') else 0
    additional_parked_amount = sum_add_parked_amount.get(
        'additional_amount__sum') if sum_add_parked_amount.get('additional_amount__sum') else 0

    sum_parked_amount2 = Claim.objects.filter(proposal_id=claim.additional_proposal, status__in=[
        'IN APPROVAL']).aggregate(Sum('amount'))
    sum_add_parked_amount2 = Claim.objects.filter(additional_proposal=claim.additional_proposal, status__in=[
        'IN APPROVAL']).aggregate(Sum('additional_amount'))

    parked_amount2 = sum_parked_amount2.get(
        'amount__sum') if sum_parked_amount2.get('amount__sum') else 0
    additional_parked_amount2 = sum_add_parked_amount2.get(
        'additional_amount__sum') if sum_add_parked_amount2.get('additional_amount__sum') else 0

    proposal.proposal_claim = amount + additional_amount
    proposal.parked_claim = parked_amount + additional_parked_amount
    proposal.balance = proposal.total_cost - proposal.proposal_claim
    proposal.save()

    proposal2 = Proposal.objects.get(
        proposal_id=claim.additional_proposal) if claim.additional_proposal else None
    if proposal2:
        proposal2.proposal_claim = amount2 + additional_amount2
        proposal2.parked_claim = parked_amount2 + additional_parked_amount2
        proposal2.balance = proposal2.total_cost - proposal2.proposal_claim
        proposal2.save()

    msg += host.url + 'claim/view/reject/' + str(_id) + \
        '\n\nThank you.'
    recipient_list = list(dict.fromkeys(recipients))
    send_email(subject, msg, recipient_list)

    return HttpResponseRedirect(reverse('claim-release-index'))


@login_required(login_url='/login/')
@role_required(allowed_roles='CLAIM')
def claim_print(request, _id):
    claim = Claim.objects.get(claim_id=_id)
    claim_id = _id.replace('/', '-')

    # Create a new PDF file with landscape orientation
    filename = 'claim_' + claim_id + '.pdf'
    pdf_file = canvas.Canvas(filename, pagesize=landscape(A4))

    # Set the font and font size
    pdf_file.setFont('Helvetica-Bold', 11)

    # Add logo in the center of the page
    logo_path = host.url + 'apps/static/img/favicon.png'
    logo_width = 60
    logo_height = 60
    page_width = landscape(A4)
    pdf_file.drawImage(logo_path, 25, 500,
                       width=logo_width, height=logo_height)

    # Add title in the center of page width
    title = 'PAYMENT VOUCHER'
    title_width = pdf_file.stringWidth(title, 'Helvetica-Bold', 11)
    title_x = (page_width[0] - title_width) / 2
    pdf_file.setFont('Helvetica-Bold', 11)
    pdf_file.drawString(title_x, 530, title)

    pdf_file.setFont('Helvetica-Bold', 8)
    pdf_file.drawString(615, 535, 'No.')
    pdf_file.drawString(670, 535, ':')
    pdf_file.setFont('Helvetica', 8)
    pdf_file.drawString(680, 535, claim_id)
    pdf_file.setFont('Helvetica-Bold', 8)
    pdf_file.drawString(615, 525, 'Date')
    pdf_file.drawString(670, 525, ':')
    pdf_file.setFont('Helvetica', 8)
    pdf_file.drawString(680, 525, claim.claim_date.strftime('%d %b %Y'))
    pdf_file.setFont('Helvetica-Bold', 8)
    pdf_file.drawString(615, 515, 'No. Invoice')
    pdf_file.drawString(670, 515, ':')
    pdf_file.setFont('Helvetica', 8)
    pdf_file.drawString(680, 515, str(claim.invoice))

    # Write the claim details
    y = 485
    pdf_file.setFont('Helvetica-Bold', 8)
    pdf_file.drawString(25, y, 'Pay To')
    pdf_file.drawString(150, y, ': ')
    pdf_file.setFont('Helvetica', 8)
    pdf_file.drawString(160, y, str(
        claim.proposal.budget.budget_distributor.distributor_name))
    pdf_file.setFont('Helvetica-Bold', 8)
    y -= 20
    pdf_file.rect(25, y - 5, 25, 15)
    title = 'No.'
    title_width = pdf_file.stringWidth(title, 'Helvetica-Bold', 8)
    title_x = 25 + (25 - title_width) / 2
    pdf_file.drawString(title_x, y, title)
    pdf_file.rect(50, y - 5, 70, 15)
    title = 'Date'
    title_width = pdf_file.stringWidth(title, 'Helvetica-Bold', 8)
    title_x = 50 + (70 - title_width) / 2
    pdf_file.drawString(title_x, y, title)
    pdf_file.rect(120, y - 5, 155, 15)
    title = 'Proposal No.'
    title_width = pdf_file.stringWidth(title, 'Helvetica-Bold', 8)
    title_x = 120 + (155 - title_width) / 2
    pdf_file.drawString(title_x, y, title)
    pdf_file.rect(275, y - 5, 390, 15)
    title = 'Description'
    title_width = pdf_file.stringWidth(title, 'Helvetica-Bold', 8)
    title_x = 275 + (390 - title_width) / 2
    pdf_file.drawString(title_x, y, title)
    pdf_file.rect(665, y - 5, 50, 15)
    title = 'Curr'
    title_width = pdf_file.stringWidth(title, 'Helvetica-Bold', 8)
    title_x = 665 + (50 - title_width) / 2
    pdf_file.drawString(title_x, y, title)
    pdf_file.rect(715, y - 5, 100, 15)
    title = 'Amount'
    title_width = pdf_file.stringWidth(title, 'Helvetica-Bold', 8)
    title_x = 715 + (100 - title_width) / 2
    pdf_file.drawString(title_x, y, title)

    y -= 15
    pdf_file.setFont('Helvetica', 8)
    pdf_file.rect(25, y - 20, 25, 30)
    title = '1'
    title_width = pdf_file.stringWidth(title, 'Helvetica', 8)
    title_x = 25 + (25 - title_width) / 2
    pdf_file.drawString(title_x, y, title)
    pdf_file.rect(50, y - 20, 70, 30)
    title = claim.invoice_date.strftime('%d %b %Y')
    title_width = pdf_file.stringWidth(title, 'Helvetica', 8)
    title_x = 50 + (70 - title_width) / 2
    pdf_file.drawString(title_x, y, title)
    pdf_file.rect(120, y - 20, 155, 30)
    title = str(claim.proposal.proposal_id)
    title_width = pdf_file.stringWidth(title, 'Helvetica', 8)
    title_x = 120 + (155 - title_width) / 2
    pdf_file.drawString(title_x, y, title)
    pdf_file.rect(275, y - 20, 390, 30)
    title = str(claim.remarks)
    pdf_file.drawString(280, y, title)
    pdf_file.rect(665, y - 20, 50, 30)
    title = 'IDR'
    title_width = pdf_file.stringWidth(title, 'Helvetica', 8)
    title_x = 665 + (50 - title_width) / 2
    pdf_file.drawString(title_x, y, title)
    pdf_file.rect(715, y - 20, 100, 30)
    title = '{:,}'.format(claim.amount)
    pdf_file.drawRightString(810, y, title)

    y -= 10
    if claim.additional_proposal:
        title = claim.additional_proposal
        title_width = pdf_file.stringWidth(title, 'Helvetica', 8)
        title_x = 120 + (155 - title_width) / 2
        pdf_file.drawString(title_x, y, title)
        pdf_file.drawString(280, y, 'Additional Proposal')
        pdf_file.drawRightString(
            810, y, '{:,}'.format(claim.additional_amount))

    y -= 20
    pdf_file.rect(25, y - 5, 690, 15)
    pdf_file.setFont('Helvetica-Bold', 8)
    title = 'TOTAL'
    pdf_file.drawRightString(710, y, title)
    pdf_file.rect(715, y - 5, 100, 15)
    pdf_file.setFont('Helvetica', 8)
    pdf_file.drawRightString(810, y, '{:,}'.format(claim.total_claim))

    y -= 15
    pdf_file.setFont('Helvetica-Bold', 8)
    pdf_file.drawRightString(710, y, 'PPN')
    pdf_file.setFont('Helvetica', 8)
    pdf_file.drawRightString(810, y, '{:,}'.format(claim.tax))
    y -= 10
    pdf_file.setFont('Helvetica-Bold', 8)
    pdf_file.drawRightString(710, y, 'TOTAL PAYMENT')
    pdf_file.setFont('Helvetica', 8)
    pdf_file.drawRightString(810, y, '{:,}'.format(claim.total))

    y -= 50
    col_width = (page_width[0] - 50) / 11
    approver = ClaimRelease.objects.filter(
        claim_id=_id, claim_approval_status='Y', printed=True).order_by('sequence')
    verificator = ClaimRelease.objects.filter(claim_id=_id, claim_approval_status='Y', as_approved='verificator', printed=True).aggregate(id=Count(
        'id')) if ClaimRelease.objects.filter(claim_id=_id, claim_approval_status='Y', as_approved='verificator', printed=True).exists() else 0
    area_approver = ClaimRelease.objects.filter(claim_id=_id, claim_approval_status='Y', as_approved='area_approver', printed=True).aggregate(id=Count(
        'id')) if ClaimRelease.objects.filter(claim_id=_id, claim_approval_status='Y', as_approved='area_approver', printed=True).exists() else 0
    checker = ClaimRelease.objects.filter(claim_id=_id, claim_approval_status='Y', as_approved='checker', printed=True).aggregate(id=Count(
        'id')) if ClaimRelease.objects.filter(claim_id=_id, claim_approval_status='Y', as_approved='checker', printed=True).exists() else 0
    ho_approver = ClaimRelease.objects.filter(claim_id=_id, claim_approval_status='Y', as_approved='ho_approver', printed=True).aggregate(id=Count(
        'id')) if ClaimRelease.objects.filter(claim_id=_id, claim_approval_status='Y', as_approved='ho_approver', printed=True).exists() else 0
    validator = ClaimRelease.objects.filter(claim_id=_id, claim_approval_status='Y', as_approved='validator', printed=True).aggregate(id=Count(
        'id')) if ClaimRelease.objects.filter(claim_id=_id, claim_approval_status='Y', as_approved='validator', printed=True).exists() else 0
    finalizer = ClaimRelease.objects.filter(claim_id=_id, claim_approval_status='Y', as_approved='finalizer', printed=True).aggregate(id=Count(
        'id')) if ClaimRelease.objects.filter(claim_id=_id, claim_approval_status='Y', as_approved='finalizer', printed=True).exists() else 0

    verificator_count = verificator['id'] if verificator else 0
    area_approver_count = area_approver['id'] if area_approver else 0
    checker_count = checker['id'] if checker else 0
    ho_approver_count = ho_approver['id'] if ho_approver else 0
    validator_count = validator['id'] if validator else 0
    finalizer_count = finalizer['id'] if finalizer else 0

    pdf_file.setFont('Helvetica', 8)
    pdf_file.rect(25, y-5, col_width, 15, stroke=True)
    title = 'Prepared By'
    title_width = pdf_file.stringWidth(title, "Helvetica", 8)
    title_x = 25 + (col_width - title_width) / 2
    pdf_file.drawString(title_x, y, title)

    pdf_file.setFont('Helvetica', 8)
    pdf_file.rect(25 + col_width, y-5,
                  col_width * verificator_count, 15, stroke=True)
    title = 'Verified By' if verificator_count > 0 else ''
    title_width = pdf_file.stringWidth(title, "Helvetica", 8)
    title_x = 25 + col_width + \
        ((col_width * verificator_count) - title_width) / 2
    pdf_file.drawString(title_x, y, title)

    pdf_file.setFont('Helvetica', 8)
    pdf_file.rect(25 + (col_width * (verificator_count + 1)), y-5,
                  col_width * area_approver_count, 15, stroke=True)
    title = 'Approved By' if area_approver_count > 0 else ''
    title_width = pdf_file.stringWidth(title, "Helvetica", 8)
    title_x = 25 + (col_width * (verificator_count + 1)) + \
        ((col_width * area_approver_count) - title_width) / 2
    pdf_file.drawString(title_x, y, title)

    pdf_file.setFont('Helvetica', 8)
    pdf_file.rect(25 + (col_width * (verificator_count + area_approver_count + 1)),
                  y-5, col_width * checker_count, 15, stroke=True)
    title = 'Checked By' if checker_count > 0 else ''
    title_width = pdf_file.stringWidth(title, "Helvetica", 8)
    title_x = 25 + (col_width * (verificator_count + area_approver_count + 1)
                    ) + ((col_width * checker_count) - title_width) / 2
    pdf_file.drawString(title_x, y, title)

    pdf_file.setFont('Helvetica', 8)
    pdf_file.rect(25 + (col_width * (verificator_count + area_approver_count +
                  checker_count + 1)), y-5, col_width * ho_approver_count, 15, stroke=True)
    title = 'Approved By' if ho_approver_count > 0 else ''
    title_width = pdf_file.stringWidth(title, "Helvetica", 8)
    title_x = 25 + (col_width * (verificator_count + area_approver_count +
                    checker_count + 1)) + ((col_width * ho_approver_count) - title_width) / 2
    pdf_file.drawString(title_x, y, title)

    pdf_file.setFont('Helvetica', 8)
    pdf_file.rect(25 + (col_width * (verificator_count + area_approver_count + checker_count +
                  ho_approver_count + 1)), y-5, col_width * validator_count, 15, stroke=True)
    title = 'Validated By' if validator_count > 0 else ''
    title_width = pdf_file.stringWidth(title, "Helvetica", 8)
    title_x = 25 + (col_width * (verificator_count + area_approver_count + checker_count +
                    ho_approver_count + 1)) + ((col_width * validator_count) - title_width) / 2
    pdf_file.drawString(title_x, y, title)

    pdf_file.setFont('Helvetica', 8)
    pdf_file.rect(25 + (col_width * (verificator_count + area_approver_count + checker_count +
                  ho_approver_count + validator_count + 1)), y-5, col_width * finalizer_count, 15, stroke=True)
    title = 'Approved By' if finalizer_count > 0 else ''
    title_width = pdf_file.stringWidth(title, "Helvetica", 8)
    title_x = 25 + (col_width * (verificator_count + area_approver_count + checker_count +
                    ho_approver_count + validator_count + 1)) + ((col_width * finalizer_count) - title_width) / 2
    pdf_file.drawString(title_x, y, title)

    pdf_file.rect(25, y - 55, col_width, 50, stroke=True)
    sign_path = User.objects.get(user_id=claim.entry_by).signature.path if User.objects.get(
        user_id=claim.entry_by).signature else ''
    if sign_path:
        pdf_file.drawImage(sign_path, 30, y - 50,
                           width=col_width - 10, height=40)
    else:
        pass
    pdf_file.rect(25, y - 70, col_width, 15, stroke=True)
    title = claim.entry_pos
    title_width = pdf_file.stringWidth(title, "Helvetica-Bold", 8)
    title_x = 25 + (col_width - title_width) / 2
    pdf_file.setFont("Helvetica-Bold", 8)
    pdf_file.drawString(title_x, y - 65, title)
    pdf_file.rect(25, y - 85, col_width, 15, stroke=True)
    pdf_file.setFont("Helvetica", 8)
    title = 'Date: ' + claim.entry_date.strftime('%d/%m/%Y')
    title_width = pdf_file.stringWidth(title, "Helvetica", 8)
    title_x = 25 + (col_width - title_width) / 2
    pdf_file.drawString(title_x, y - 80, title)

    for i in range(1, approver.count() + 1):
        pdf_file.rect(25 + (col_width * i), y - 55, col_width, 50, stroke=True)
        if approver:
            sign_path = User.objects.get(user_id=approver[i - 1].claim_approval_id).signature.path if User.objects.get(
                user_id=approver[i - 1].claim_approval_id).signature else ''
            if sign_path:
                pdf_file.drawImage(sign_path, 30 + (col_width * i), y - 50,
                                   width=col_width - 10, height=40)
            else:
                pass
            pdf_file.rect(25 + (col_width * i), y - 70,
                          col_width, 15, stroke=True)
            title = approver[i - 1].claim_approval_position
            title_width = pdf_file.stringWidth(title, "Helvetica-Bold", 8)
            title_x = 25 + (col_width * i) + (col_width - title_width) / 2
            pdf_file.setFont("Helvetica-Bold", 8)
            pdf_file.drawString(title_x, y - 65, title)
            pdf_file.rect(25 + (col_width * i), y - 85,
                          col_width, 15, stroke=True)
            pdf_file.setFont("Helvetica", 8)
            title = 'Date: ' + \
                approver[i - 1].claim_approval_date.strftime('%d/%m/%Y')
            title_width = pdf_file.stringWidth(title, "Helvetica", 8)
            title_x = 25 + (col_width * i) + (col_width - title_width) / 2
            pdf_file.drawString(title_x, y - 80, title)
        else:
            pass

    y = 50
    pdf_file.setFont("Helvetica-Bold", 7)
    pdf_file.drawString(
        25, y, 'PT. ABC PRESIDENT INDONESIA (www.abcpresident.com)')
    pdf_file.drawString(25, y - 10, 'Head Office : ')
    title_x = pdf_file.stringWidth('Head Office : ', 'Helvetica-Bold', 7)
    pdf_file.setFont("Helvetica", 7)
    address = 'EightyEight@Kasablanka Office Tower A Lt. 31 Jl. Casablanca Raya Kav. 88 Jakarta Selatan 12870 '
    pdf_file.drawString(25 + title_x, y - 10, address)
    address_x = pdf_file.stringWidth(address, 'Helvetica', 7)
    pdf_file.setFont("Helvetica-Bold", 7)
    pdf_file.drawString(25 + title_x + address_x, y - 10, 'Tel : ')
    tel_x = pdf_file.stringWidth('Tel : ', 'Helvetica-Bold', 7)
    pdf_file.setFont("Helvetica", 7)
    tel = '+62 21 2982 0168 (Hunting) '
    ph_x = pdf_file.stringWidth(tel, 'Helvetica', 7)
    pdf_file.drawString(25 + title_x + address_x + tel_x, y - 10, tel)
    pdf_file.setFont("Helvetica-Bold", 7)
    fax_x = pdf_file.stringWidth('Fax : ', 'Helvetica-Bold', 7)
    pdf_file.drawString(25 + title_x + address_x +
                        tel_x + ph_x, y - 10, 'Fax : ')
    pdf_file.setFont("Helvetica", 7)
    fax = '+62 21 2982 0166 '
    pdf_file.drawString(25 + title_x + address_x +
                        tel_x + ph_x + fax_x, y - 10, fax)
    pdf_file.setFont("Helvetica-Bold", 7)
    factory = 'Factory : '
    factory_x = pdf_file.stringWidth(factory, 'Helvetica-Bold', 7)
    pdf_file.drawString(25, y - 20, factory)
    pdf_file.setFont("Helvetica", 7)
    factory_address = 'Desa Walabar Kec. Klari, Karawang Timur 41371, Jawa Barat, Indonesia '
    pdf_file.drawString(25 + factory_x, y - 20, factory_address)
    factory_address_x = pdf_file.stringWidth(factory_address, 'Helvetica', 7)
    pdf_file.setFont("Helvetica-Bold", 7)
    pdf_file.drawString(25 + factory_x + factory_address_x, y - 20, 'Tel : ')
    factory_tel_x = pdf_file.stringWidth('Tel : ', 'Helvetica-Bold', 7)
    pdf_file.setFont("Helvetica", 7)
    factory_tel = '+62 267 431 422 (Hunting) '
    factory_ph_x = pdf_file.stringWidth(factory_tel, 'Helvetica', 7)
    pdf_file.drawString(25 + factory_x + factory_address_x +
                        factory_tel_x, y - 20, factory_tel)
    pdf_file.setFont("Helvetica-Bold", 7)
    factory_fax_x = pdf_file.stringWidth('Fax : ', 'Helvetica-Bold', 7)
    pdf_file.drawString(25 + factory_x + factory_address_x +
                        factory_tel_x + factory_ph_x, y - 20, 'Fax : ')
    pdf_file.setFont("Helvetica", 7)
    factory_fax = '+62 267 431 421'
    pdf_file.drawString(25 + factory_x + factory_address_x +
                        factory_tel_x + factory_ph_x + factory_fax_x, y - 20, factory_fax)

    pdf_file.save()

    return FileResponse(open(filename, 'rb'), content_type='application/pdf')


@login_required(login_url='/login/')
@role_required(allowed_roles='CLAIM-ARCHIVE')
def claim_archive_index(request):
    rejects = Claim.objects.filter(status='REJECTED', area__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-claim_id').all

    context = {
        'rejects': rejects,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'claim_archive',
        'group_segment': 'claim',
        'crud': 'index',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list(
            'menu_id', flat=True),
        'btn': Auth.objects.get(
            user_id=request.user.user_id, menu_id='CLAIM-ARCHIVE') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/claim_archive.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='CLAIM-APPROVAL')
def claim_matrix_index(request):
    areas = AreaSales.objects.all()

    context = {
        'data': areas,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'claim_matrix',
        'group_segment': 'approval',
        'crud': 'index',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='CLAIM-APPROVAL') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/claim_matrix_index.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='CLAIM-APPROVAL')
def claim_matrix_view(request, _id, _channel):
    area = AreaSales.objects.get(area_id=_id)
    channels = AreaChannelDetail.objects.filter(area_id=_id, status=1)
    approvers = ClaimMatrix.objects.filter(area_id=_id, channel_id=_channel)
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT user_id, username, position_name, q_claimmatrix.approver_id FROM apps_user INNER JOIN apps_position ON apps_user.position_id = apps_position.position_id LEFT JOIN (SELECT * FROM apps_claimmatrix WHERE area_id = '" + str(_id) + "' AND channel_id = '" + str(_channel) + "') AS q_claimmatrix ON apps_user.user_id = q_claimmatrix.approver_id WHERE q_claimmatrix.approver_id IS NULL")
        users = cursor.fetchall()

    if request.POST:
        check = request.POST.getlist('checks[]')
        for i in users:
            if str(i[0]) in check:
                try:
                    approver = ClaimMatrix(
                        area_id=_id, channel_id=_channel, approver_id=i[0])
                    approver.save()
                except IntegrityError:
                    continue
            else:
                ClaimMatrix.objects.filter(
                    area_id=_id, channel_id=_channel, approver_id=i[0]).delete()

        return HttpResponseRedirect(reverse('claim-matrix-view', args=[_id, _channel]))

    context = {
        'data': area,
        'channels': channels,
        'users': users,
        'approvers': approvers,
        'channel': _channel,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'claim_matrix',
        'group_segment': 'approval',
        'tab': 'auth',
        'crud': 'view',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='CLAIM-APPROVAL') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/claim_matrix_view.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='CLAIM-APPROVAL')
def claim_matrix_update(request, _id, _channel, _approver):
    approvers = ClaimMatrix.objects.get(
        area=_id, channel_id=_channel, approver_id=_approver)

    if request.POST:
        approvers.sequence = int(request.POST.get('sequence'))
        approvers.limit = int(request.POST.get('limit'))
        approvers.return_to = True if request.POST.get('return') else False
        approvers.approve = True if request.POST.get('approve') else False
        approvers.revise = True if request.POST.get('revise') else False
        approvers.returned = True if request.POST.get('returned') else False
        approvers.reject = True if request.POST.get('reject') else False
        approvers.notif = True if request.POST.get('notif') else False
        approvers.printed = True if request.POST.get('printed') else False
        approvers.as_approved = request.POST.get('as_approved')
        approvers.save()

        return HttpResponseRedirect(reverse('claim-matrix-view', args=[_id, _channel]))

    return render(request, 'home/claim_matrix_view.html')


@login_required(login_url='/login/')
@role_required(allowed_roles='CLAIM-APPROVAL')
def claim_matrix_delete(request, _id, _channel, _arg):
    approvers = ClaimMatrix.objects.get(
        area=_id, channel_id=_channel, approver_id=_arg)
    approvers.delete()

    return HttpResponseRedirect(reverse('claim-matrix-view', args=[_id, _channel]))


@login_required(login_url='/login/')
@role_required(allowed_roles='CL')
def cl_index(request, _tab):
    cl = CL.objects.all()
    draft_count = CL.objects.filter(status='DRAFT', area__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).count
    inapproval_count = CL.objects.filter(status='IN APPROVAL', area__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).count
    open_count = CL.objects.filter(status='OPEN', area__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).count

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT cl_id, cl_date, area_id, distributor_name, sum_total_claim FROM apps_distributor INNER JOIN apps_cl ON apps_distributor.distributor_id = apps_cl.distributor_id LEFT JOIN (SELECT cl_id_id, sum(total_claim) AS sum_total_claim FROM apps_cldetail INNER JOIN apps_claim ON apps_cldetail.claim_id = apps_claim.claim_id WHERE apps_claim.status = 'OPEN' GROUP BY cl_id_id) AS q_cldetail ON apps_cl.cl_id = q_cldetail.cl_id_id WHERE apps_cl.status = 'OPEN' AND apps_cl.area_id IN (SELECT area_id FROM apps_areauser WHERE user_id = '" + str(request.user.user_id) + "') ORDER BY cl_id")
        opens = cursor.fetchall()

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT cl_id, cl_date, area_id, distributor_name, sum_total_claim, status FROM apps_distributor INNER JOIN apps_cl ON apps_distributor.distributor_id = apps_cl.distributor_id LEFT JOIN (SELECT cl_id_id, sum(total_claim) AS sum_total_claim FROM apps_cldetail INNER JOIN apps_claim ON apps_cldetail.claim_id = apps_claim.claim_id WHERE apps_claim.status = 'OPEN' GROUP BY cl_id_id) AS q_cldetail ON apps_cl.cl_id = q_cldetail.cl_id_id WHERE apps_cl.status = 'DRAFT' AND apps_cl.area_id IN (SELECT area_id FROM apps_areauser WHERE user_id = '" + str(request.user.user_id) + "') ORDER BY cl_id")
        drafts = cursor.fetchall()

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT cl_id, cl_date, area_id, distributor_name, sum_total_claim, status, cl_approval_name FROM apps_distributor INNER JOIN apps_cl ON apps_distributor.distributor_id = apps_cl.distributor_id LEFT JOIN (SELECT cl_id_id, sum(total_claim) AS sum_total_claim FROM apps_cldetail INNER JOIN apps_claim ON apps_cldetail.claim_id = apps_claim.claim_id WHERE apps_claim.status = 'OPEN' GROUP BY cl_id_id) AS q_cldetail ON apps_cl.cl_id = q_cldetail.cl_id_id INNER JOIN (SELECT cl_id_id, MIN(sequence) AS seq FROM apps_clrelease WHERE cl_approval_status = 'N' GROUP BY cl_id_id) AS q_clrelease ON apps_cl.cl_id = q_clrelease.cl_id_id INNER JOIN apps_clrelease ON q_clrelease.cl_id_id = apps_clrelease.cl_id_id AND q_clrelease.seq = apps_clrelease.sequence WHERE apps_cl.status = 'IN APPROVAL' AND apps_cl.area_id IN (SELECT area_id FROM apps_areauser WHERE user_id = '" + str(request.user.user_id) + "') ORDER BY cl_id")
        inapprovals = cursor.fetchall()

    context = {
        'data': cl,
        'drafts': drafts,
        'draft_count': draft_count,
        'inapprovals': inapprovals,
        'inapproval_count': inapproval_count,
        'opens': opens,
        'open_count': open_count,
        'tab': _tab,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'cl',
        'group_segment': 'cl',
        'crud': 'index',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='CL') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/cl_index.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='CL')
def cl_add(request, _area, _distributor):
    selected_area = _area
    selected_distributor = _distributor
    area = AreaUser.objects.filter(user_id=request.user.user_id).values_list(
        'area_id', 'area__area_name')
    distributors = Claim.objects.filter(status='OPEN', area=selected_area).values_list(
        'proposal__budget__budget_distributor', 'proposal__budget__budget_distributor__distributor_name').distinct() if selected_area != '0' else None

    no_save = False
    message = ''

    if selected_area != '0' and selected_distributor != '0':
        approvers = CLMatrix.objects.filter(
            area_id=selected_area).order_by('sequence')
        if approvers.count() == 0:
            no_save = True
            message = "No communication letter's approver found for this area."

    try:
        _no = CL.objects.filter(
            cl_date__year=datetime.datetime.now().year).latest('seq_number')
    except CL.DoesNotExist:
        _no = None
    if _no is None:
        format_no = '{:04d}'.format(1)
    else:
        format_no = '{:04d}'.format(_no.seq_number + 1)

    _id = 'LBS-5' + format_no + '/' + selected_area + \
        '/' + selected_distributor + '/' + datetime.datetime.now().strftime('%m/%Y')

    if selected_area != '0' and selected_distributor != '0' and not no_save:
        parent = CL(cl_id=_id, cl_date=datetime.datetime.now(), area_id=selected_area,
                    distributor_id=selected_distributor, entry_pos=request.user.position.position_id, seq_number=_no.seq_number + 1 if _no else 1)
        parent.save()

        for i in approvers:
            _cl = CL.objects.get(cl_id=_id)
            release = CLRelease(
                cl_id=_cl,
                cl_approval_id=i.approver_id,
                cl_approval_name=i.approver.username,
                cl_approval_email=i.approver.email,
                cl_approval_position=i.approver.position.position_id,
                sequence=i.sequence,
                limit=i.limit,
                return_to=i.return_to,
                approve=i.approve,
                revise=i.revise,
                returned=i.returned,
                reject=i.reject,
                notif=i.notif,
                printed=i.printed,
                as_approved=i.as_approved)
            release.save()

        return HttpResponseRedirect(reverse('cl-view', args=['draft', _id]))

    context = {
        'selected_area': selected_area,
        'selected_distributor': selected_distributor,
        'area': area,
        'distributors': distributors,
        'no_save': no_save,
        'message': message,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'cl',
        'group_segment': 'cl',
        'crud': 'add',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='CL') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/cl_add.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='CL')
def cl_view(request, _tab, _id):
    cl = CL.objects.get(cl_id=_id)
    cl_detail = CLDetail.objects.filter(cl_id=_id)
    claim = Claim.objects.filter(status='OPEN', area_id=cl.area_id, proposal__budget__budget_distributor=cl.distributor_id).exclude(
        cldetail__claim_id__in=CLDetail.objects.exclude(cl_id__status='REJECTED').values_list('claim_id', flat=True)).values_list('claim_id', 'remarks', 'claim_date', 'total_claim', 'cldetail__claim_id')

    sum_cl_detail = CLDetail.objects.filter(
        cl_id=_id).aggregate(total_claim=Sum('claim_id__total_claim'))

    highest_approval = CLRelease.objects.filter(
        cl_id=_id).aggregate(Max('sequence'))
    highest_sequence = highest_approval.get('sequence__min') if highest_approval.get(
        'sequence__min') else highest_approval.get('sequence__max') + 1
    if highest_sequence:
        approval = CLRelease.objects.filter(
            cl_id=_id, sequence__lt=highest_sequence).order_by('sequence')
    else:
        approval = CLRelease.objects.filter(cl_id=_id).order_by('sequence')
    rejector = CLRelease.objects.filter(
        cl_id=_id, cl_approval_status='N').order_by('sequence').first() if cl.status == 'REJECTED' else None

    if request.POST:
        check = request.POST.getlist('checks[]')
        _cl = CL.objects.get(cl_id=_id)
        for i in claim:
            if str(i[0]) in check:
                try:
                    detail = CLDetail(cl_id=_cl, claim_id=i[0])
                    detail.save()
                except IntegrityError:
                    continue
            else:
                CLDetail.objects.filter(cl_id=_id, claim_id=i[0]).delete()

        return HttpResponseRedirect(reverse('cl-view', args=[_tab, _id]))

    context = {
        'data': cl,
        'cl_detail': cl_detail,
        'claim': claim,
        'sum_cl_detail': sum_cl_detail,
        'tab': _tab,
        'approval': approval,
        'rejector': rejector,
        'status': cl.status,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'cl_archive' if _tab == 'reject' else 'cl',
        'group_segment': 'cl',
        'crud': 'view',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list(
            'menu_id', flat=True),
        'btn': Auth.objects.get(
            user_id=request.user.user_id, menu_id='CL') if not request.user.is_superuser else Auth.objects.all(),
    }

    return render(request, 'home/cl_view.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='CL')
def cl_submit(request, _id):
    cl = CL.objects.get(cl_id=_id)
    cl.status = 'IN APPROVAL'
    cl.save()

    mail_sent = CLRelease.objects.filter(
        cl_id=_id).order_by('sequence').values_list('mail_sent', flat=True)
    if mail_sent[0] == False:
        email = CLRelease.objects.filter(
            cl_id=_id).order_by('sequence').values_list('cl_approval_email', flat=True)
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT username FROM apps_clrelease INNER JOIN apps_user ON apps_clrelease.cl_approval_id = apps_user.user_id WHERE cl_id_id = '" + str(_id) + "' AND cl_approval_status = 'N' ORDER BY sequence LIMIT 1")
            approver = cursor.fetchone()

        subject = 'CL Approval'
        msg = 'Dear ' + approver[0] + ',\n\nYou have a new CL to approve. Please check your CL release list.\n\n' + \
            'Click this link to approve, revise, return or reject this CL.\n' + host.url + 'cl_release/view/' + str(_id) + '/0/' + \
            '\n\nThank you.'
        send_email(subject, msg, [email[0]])

        # update mail sent to true
        release = CLRelease.objects.filter(
            cl_id=_id).order_by('sequence').first()
        release.mail_sent = True
        release.save()

    return HttpResponseRedirect(reverse('cl-index', args=['inapproval']))


@login_required(login_url='/login/')
@role_required(allowed_roles='CL')
def cldetail_delete(request, _tab, _id):
    detail = CLDetail.objects.get(id=_id)
    detail.delete()

    return HttpResponseRedirect(reverse('cl-view', args=[_tab, detail.cl_id_id]))


@login_required(login_url='/login/')
@role_required(allowed_roles='CL-RELEASE')
def cldetail_release_delete(request, _id):
    detail = CLDetail.objects.get(id=_id)
    detail.delete()

    return HttpResponseRedirect(reverse('cl-release-view', args=[detail.cl_id_id]))


@login_required(login_url='/login/')
@role_required(allowed_roles='CL')
def cl_delete(request, _tab, _id):
    cl = CL.objects.get(cl_id=_id)

    cl.delete()
    return HttpResponseRedirect(reverse('cl-index', args=[_tab]))


@login_required(login_url='/login/')
@role_required(allowed_roles='CL-RELEASE')
def cl_release_index(request):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT apps_cl.cl_id, apps_cl.cl_date, apps_cl.area_id, apps_distributor.distributor_name, sum_total_claim, apps_cl.status, apps_clrelease.sequence FROM apps_distributor INNER JOIN apps_cl ON apps_distributor.distributor_id = apps_cl.distributor_id INNER JOIN apps_clrelease ON apps_cl.cl_id = apps_clrelease.cl_id_id INNER JOIN (SELECT cl_id_id, MIN(sequence) AS seq FROM apps_clrelease WHERE cl_approval_status = 'N' GROUP BY cl_id_id ORDER BY sequence ASC) AS q_group ON apps_clrelease.cl_id_id = q_group.cl_id_id AND apps_clrelease.sequence = q_group.seq LEFT JOIN (SELECT cl_id_id, sum(total_claim) AS sum_total_claim FROM apps_cldetail INNER JOIN apps_claim ON apps_cldetail.claim_id = apps_claim.claim_id WHERE apps_claim.status = 'OPEN' GROUP BY cl_id_id) AS q_cldetail ON apps_cl.cl_id = q_cldetail.cl_id_id WHERE (apps_cl.status = 'PENDING' OR apps_cl.status = 'IN APPROVAL') AND apps_clrelease.cl_approval_id = '" + str(request.user.user_id) + "'")
        release = cursor.fetchall()

    context = {
        'data': release,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'cl_release',
        'group_segment': 'cl',
        'crud': 'index',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='CL-RELEASE') if not request.user.is_superuser else Auth.objects.all(),
    }

    return render(request, 'home/cl_release_index.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='CL-RELEASE')
def cl_release_view(request, _id, _is_revise):
    cl = CL.objects.get(cl_id=_id)
    cl_detail = CLDetail.objects.filter(cl_id=_id)
    approved = CLRelease.objects.get(
        cl_id=_id, cl_approval_id=request.user.user_id).cl_approval_status
    claim = Claim.objects.filter(status='OPEN', area_id=cl.area_id, proposal__budget__budget_distributor=cl.distributor_id).exclude(
        cldetail__claim_id__in=CLDetail.objects.all().values_list('claim_id', flat=True)).values_list('claim_id', 'remarks', 'cldetail__claim_id')

    sum_cl_detail = CLDetail.objects.filter(
        cl_id=_id).aggregate(total_claim=Sum('claim_id__total_claim'))

    if request.POST:
        check = request.POST.getlist('checks[]')
        for i in claim:
            if str(i[0]) in check:
                try:
                    detail = CLDetail(cl_id=_id, claim_id=i[0])
                    detail.save()
                except IntegrityError:
                    continue
            else:
                CLDetail.objects.filter(cl_id=_id, claim_id=i[0]).delete()

        return HttpResponseRedirect(reverse('cl-release-view', args=[_id, 0]))

    context = {
        'data': cl,
        'cl_detail': cl_detail,
        'claim': claim,
        'sum_cl_detail': sum_cl_detail,
        'approved': approved,
        'is_revise': _is_revise,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'cl_release',
        'group_segment': 'cl',
        'crud': 'view',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list(
            'menu_id', flat=True),
        'btn': Auth.objects.get(
            user_id=request.user.user_id, menu_id='CL-RELEASE') if not request.user.is_superuser else Auth.objects.all(),
        'btn_release': CLRelease.objects.get(cl_id=_id, cl_approval_id=request.user.user_id) if not request.user.is_superuser else None,
    }
    return render(request, 'home/cl_release_view.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='CL-RELEASE')
def cl_release_update(request, _id):
    cl = CL.objects.get(cl_id=_id)
    cl_detail = CLDetail.objects.filter(cl_id=_id)
    claim = Claim.objects.filter(status='OPEN', area_id=cl.area_id, proposal__budget__budget_distributor=cl.distributor_id).exclude(
        cldetail__claim_id__in=CLDetail.objects.all().values_list('claim_id', flat=True)).values_list('claim_id', 'remarks', 'cldetail__claim_id')

    _add = ''
    _remove = ''

    if request.POST:
        check = request.POST.getlist('checks[]')
        for i in claim:
            if str(i[0]) in check:
                try:
                    detail = CLDetail(cl_id=_id, claim_id=i[0])
                    detail.save()
                    _add += i[0] + '\n'
                except IntegrityError:
                    continue
            else:
                CLDetail.objects.filter(cl_id=_id, claim_id=i[0]).delete()
                _remove += i[0] + '\n'

        recipients = []

        release = CLRelease.objects.get(
            cl_id=_id, cl_approval_id=request.user.user_id)
        release.revise_note = request.POST.get('revise_note')
        release.save()

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT cl_id, email FROM apps_cl INNER JOIN apps_user ON apps_cl.entry_by = apps_user.user_id WHERE cl_id = '" + str(_id) + "'")
            entry_mail = cursor.fetchone()
            if entry_mail:
                recipients.append(entry_mail[1])

            cursor.execute(
                "SELECT cl_id, email FROM apps_cl INNER JOIN apps_user ON apps_cl.update_by = apps_user.user_id WHERE cl_id = '" + str(_id) + "'")
            update_mail = cursor.fetchone()
            if update_mail:
                recipients.append(update_mail[1])

            cursor.execute(
                "SELECT cl_id, cl_approval_email FROM apps_clrelease WHERE cl_id = '" + str(_id) + "' AND cl_approval_status = 'Y'")
            approver_mail = cursor.fetchall()
            for mail in approver_mail:
                recipients.append(mail[1])

        subject = 'CL Revised'
        msg = 'Dear All,\n\nThe following is revised CL for CL No. ' + \
            str(_id) + ':\n'
        msg += '\nCLAIM ADD:\n'
        msg += _add
        msg += '\nCLAIM REMOVE\n'
        msg += _remove

        msg += '\nNote: ' + \
            str(release.revise_note) + '\n\nClick the following link to view the CL.\n' + host.url + 'cl/view/inapproval/' + str(_id) + '/' + \
            '\n\nThank you.'

        recipient_list = list(dict.fromkeys(recipients))
        send_email(subject, msg, recipient_list)

        return HttpResponseRedirect(reverse('cl-release-view', args=[_id, 0]))

    context = {
        'data': cl,
        'cl_detail': cl_detail,
        'claim': claim,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'cl_release',
        'group_segment': 'cl',
        'crud': 'update',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list(
            'menu_id', flat=True),
        'btn': Auth.objects.get(
            user_id=request.user.user_id, menu_id='CL-RELEASE') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/cl_view.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='CL-RELEASE')
def cl_release_approve(request, _id):
    cl = CL.objects.get(cl_id=_id)
    release = CLRelease.objects.get(
        cl_id=_id, cl_approval_id=request.user.user_id)
    release.cl_approval_status = 'Y'
    release.cl_approval_date = timezone.now()
    release.save()

    highest_approval = CLRelease.objects.filter(
        cl_id=_id).aggregate(Max('sequence'))
    highest_sequence = highest_approval.get('sequence__min') if highest_approval.get(
        'sequence__min') else highest_approval.get('sequence__max') + 1
    if highest_sequence:
        approval = CLRelease.objects.filter(
            cl_id=_id, sequence__lt=highest_sequence).order_by('sequence').last()
    else:
        approval = CLRelease.objects.filter(
            cl_id=_id).order_by('sequence').last()

    if release.sequence == approval.sequence:
        cl.status = 'OPEN'

        recipients = []

        maker = cl.entry_by
        maker_mail = User.objects.get(user_id=maker).email
        recipients.append(maker_mail)

        approvers = CLRelease.objects.filter(
            cl_id=_id, notif=True, cl_approval_status='Y')
        for i in approvers:
            recipients.append(i.cl_approval_email)

        subject = 'CL Approved'
        msg = 'Dear All,\n\nCL No. ' + str(_id) + ' has been approved.\n\nClick the following link to view the CL.\n' + host.url + 'cl/view/open/' + str(_id) + \
            '\n\nThank you.'
        recipient_list = list(dict.fromkeys(recipients))
        send_email(subject, msg, recipient_list)
    else:
        cl.status = 'IN APPROVAL'

        email = CLRelease.objects.filter(cl_id=_id, cl_approval_status='N').order_by(
            'sequence').values_list('cl_approval_email', flat=True)
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT cl_approval_name FROM apps_clrelease WHERE cl_id_id = '" + str(_id) + "' AND cl_approval_status = 'N' ORDER BY sequence LIMIT 1")
            approver = cursor.fetchone()

        subject = 'CL Approval'
        msg = 'Dear ' + approver[0] + ',\n\nYou have a new CL to approve. Please check your CL release list.\n\n' + \
            'Click this link to approve, revise, return or reject this CL.\n' + host.url + 'cl_release/view/' + str(_id) + '/0/' + \
            '\n\nThank you.'
        send_email(subject, msg, [email[0]])

    cl.save()

    return HttpResponseRedirect(reverse('cl-release-index'))


@login_required(login_url='/login/')
@role_required(allowed_roles='CL-RELEASE')
def cl_release_return(request, _id):
    recipients = []
    draft = False

    try:
        return_to = CLRelease.objects.get(
            cl_id=_id, return_to=True, sequence__lt=CLRelease.objects.get(cl_id=_id, cl_approval_id=request.user.user_id).sequence)

        if return_to:
            approvers = CLRelease.objects.filter(
                cl_id=_id, sequence__gte=CLRelease.objects.get(cl_id=_id, return_to=True).sequence, sequence__lt=CLRelease.objects.get(cl_id=_id, cl_approval_id=request.user.user_id).sequence)
    except CLRelease.DoesNotExist:
        approvers = CLRelease.objects.filter(
            cl_id=_id, sequence__lte=CLRelease.objects.get(cl_id=_id, cl_approval_id=request.user.user_id).sequence)
        draft = True

    for i in approvers:
        recipients.append(i.cl_approval_email)
        i.cl_approval_status = 'N'
        i.cl_approval_date = None
        i.revise_note = ''
        i.return_note = ''
        i.reject_note = ''
        i.mail_sent = False
        i.save()

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT cl_id, email FROM apps_cl INNER JOIN apps_user ON apps_cl.entry_by = apps_user.user_id WHERE cl_id = '" + str(_id) + "'")
        entry_mail = cursor.fetchone()
        if entry_mail:
            recipients.append(entry_mail[1])

        cursor.execute(
            "SELECT cl_id, email FROM apps_cl INNER JOIN apps_user ON apps_cl.update_by = apps_user.user_id WHERE cl_id = '" + str(_id) + "'")
        update_mail = cursor.fetchone()
        if update_mail:
            recipients.append(update_mail[1])

    note = CLRelease.objects.get(
        cl_id=_id, cl_approval_id=request.user.user_id)
    note.return_note = request.POST.get('return_note')
    note.save()

    subject = 'CL Returned'
    msg = 'Dear All,\n\nCL No. ' + str(_id) + ' has been returned.\n\nNote: ' + \
        str(note.return_note) + \
        '\n\nClick the following link to revise the CL.\n'

    if draft:
        cl = CL.objects.get(cl_id=_id)
        cl.status = 'DRAFT'
        cl.save()
        msg += host.url + 'cl/view/pending/' + str(_id) + \
            '\n\nThank you.'
    else:
        msg += host.url + 'cl_release/view/' + \
            str(_id) + '/0/\n\nThank you.'
    recipient_list = list(dict.fromkeys(recipients))
    send_email(subject, msg, recipient_list)

    return HttpResponseRedirect(reverse('cl-release-index'))


@login_required(login_url='/login/')
@role_required(allowed_roles='CL-RELEASE')
def cl_release_reject(request, _id):
    cl = CL.objects.get(cl_id=_id)
    recipients = []

    try:
        approvers = CLRelease.objects.filter(
            cl_id=_id, sequence__lt=CLRelease.objects.get(cl_id=_id, cl_approval_id=request.user.user_id).sequence)
    except CLRelease.DoesNotExist:
        pass

    for i in approvers:
        recipients.append(i.cl_approval_email)

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT cl_id, email FROM apps_cl INNER JOIN apps_user ON apps_cl.entry_by = apps_user.user_id WHERE cl_id = '" + str(_id) + "'")
        entry_mail = cursor.fetchone()
        if entry_mail:
            recipients.append(entry_mail[1])

        cursor.execute(
            "SELECT cl_id, email FROM apps_cl INNER JOIN apps_user ON apps_cl.update_by = apps_user.user_id WHERE cl_id = '" + str(_id) + "'")
        update_mail = cursor.fetchone()
        if update_mail:
            recipients.append(update_mail[1])

    note = CLRelease.objects.get(
        cl_id=_id, cl_approval_id=request.user.user_id)
    note.reject_note = request.POST.get('reject_note')
    note.save()

    cl = CL.objects.get(cl_id=_id)
    cl.status = 'REJECTED'
    cl.save()

    subject = 'CL Rejected'
    msg = 'Dear All,\n\nCL No. ' + str(_id) + ' has been rejected.\n\nNote: ' + \
        str(note.reject_note) + \
        '\n\nClick the following link to see the CL.\n'
    msg += host.url + 'cl/view/reject/' + str(_id) + \
        '\n\nThank you.'
    recipient_list = list(dict.fromkeys(recipients))
    send_email(subject, msg, recipient_list)

    return HttpResponseRedirect(reverse('cl-release-index'))


@login_required(login_url='/login/')
@role_required(allowed_roles='CL-APPROVAL')
def cl_matrix_index(request):
    areas = AreaSales.objects.all()

    context = {
        'data': areas,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'cl_matrix',
        'group_segment': 'approval',
        'crud': 'index',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='CL-APPROVAL') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/cl_matrix_index.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='CL-APPROVAL')
def cl_matrix_view(request, _id):
    area = AreaSales.objects.get(area_id=_id)
    approvers = CLMatrix.objects.filter(area_id=_id)
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT user_id, username, position_name, q_clmatrix.approver_id FROM apps_user INNER JOIN apps_position ON apps_user.position_id = apps_position.position_id LEFT JOIN (SELECT * FROM apps_clmatrix WHERE area_id = '" + str(_id) + "') AS q_clmatrix ON apps_user.user_id = q_clmatrix.approver_id WHERE q_clmatrix.approver_id IS NULL")
        users = cursor.fetchall()

    if request.POST:
        check = request.POST.getlist('checks[]')
        for i in users:
            if str(i[0]) in check:
                try:
                    approver = CLMatrix(area_id=_id, approver_id=i[0])
                    approver.save()
                except IntegrityError:
                    continue
            else:
                CLMatrix.objects.filter(area_id=_id, approver_id=i[0]).delete()

        return HttpResponseRedirect(reverse('cl-matrix-view', args=[_id]))

    context = {
        'data': area,
        'users': users,
        'approvers': approvers,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'cl_matrix',
        'group_segment': 'approval',
        'tab': 'auth',
        'crud': 'view',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='CL-APPROVAL') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/cl_matrix_view.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='CL-APPROVAL')
def cl_matrix_update(request, _id, _approver):
    approvers = CLMatrix.objects.get(area=_id, approver_id=_approver)

    if request.POST:
        approvers.sequence = int(request.POST.get('sequence'))
        # approvers.limit = int(request.POST.get('limit'))
        approvers.return_to = True if request.POST.get('return') else False
        approvers.approve = True if request.POST.get('approve') else False
        approvers.revise = True if request.POST.get('revise') else False
        approvers.returned = True if request.POST.get('returned') else False
        approvers.reject = True if request.POST.get('reject') else False
        approvers.notif = True if request.POST.get('notif') else False
        approvers.printed = True if request.POST.get('printed') else False
        approvers.as_approved = request.POST.get('as_approved')
        approvers.save()

        return HttpResponseRedirect(reverse('cl-matrix-view', args=[_id]))

    return render(request, 'home/cl_matrix_view.html')


@login_required(login_url='/login/')
@role_required(allowed_roles='CL-APPROVAL')
def cl_matrix_delete(request, _id, _arg):
    approvers = CLMatrix.objects.get(area=_id, approver_id=_arg)
    approvers.delete()

    return HttpResponseRedirect(reverse('cl-matrix-view', args=[_id]))


@login_required(login_url='/login/')
@role_required(allowed_roles='CL-ARCHIVE')
def cl_archive_index(request):
    cl = CL.objects.filter(status='REJECTED', area__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-cl_id').all

    context = {
        'data': cl,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'cl_archive',
        'group_segment': 'cl',
        'crud': 'index',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='CL-ARCHIVE') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/cl_archive.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='CL')
def cl_print(request, _id):
    cl = CL.objects.get(cl_id=_id)
    cl_detail = CLDetail.objects.filter(cl_id=_id)
    area = AreaSales.objects.get(area_id=cl.area_id)
    detail_sum = Claim.objects.filter(
        claim_id__in=cl_detail.values_list('claim_id')).aggregate(total=Sum('total_claim'))
    approver = CLRelease.objects.filter(
        cl_id=_id, cl_approval_status='Y', printed=True).order_by('sequence')
    cl_id = _id.replace('/', '-')
    bulan = ['Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
             'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember']

    # Create a new PDF file with landscape orientation
    filename = 'CL-' + cl_id + '.pdf'
    pdf_file = canvas.Canvas(filename, pagesize=landscape(A4))

    # Set the font and font size
    pdf_file.setFont('Helvetica-Bold', 8)

    # Add logo in the center of the page
    logo_path = host.url + 'apps/static/img/favicon.png'
    logo_width = 60
    logo_height = 60
    page_width = landscape(A4)
    logo_x = (page_width[0] - logo_width) / 2
    pdf_file.drawImage(logo_path, logo_x, 515,
                       width=logo_width, height=logo_height)

    # Add header
    y = 500
    pdf_file.drawString(25, y, area.base_city.capitalize() + ', ' +
                        cl.cl_date.strftime('%-d') + ' ' + bulan[cl.cl_date.month - 1] + ' ' + cl.cl_date.strftime('%Y'))
    pdf_file.drawRightString(815, y, 'No. ' + cl.cl_id)

    y -= 25
    pdf_file.drawString(25, y, 'Kepada Yth.')
    y -= 10
    pdf_file.drawString(25, y, cl.distributor.distributor_name)
    y -= 10
    pdf_file.drawString(25, y, 'Di tempat')

    y -= 25
    pdf_file.setFont('Helvetica', 8)
    pdf_file.drawString(25, y, 'Dengan hormat,')

    y -= 25
    pdf_file.drawString(25, y, 'Bersama ini kami sampaikan daftar program yang akan memotong Budget Selisih Margin PT. ABC PI di ' +
                        cl.distributor.distributor_name + ' sebagai berikut:')

    y -= 20
    pdf_file.setFont('Helvetica-Bold', 8)
    pdf_file.rect(25, y - 5, 25, 15, stroke=True)
    title = 'No.'
    title_width = pdf_file.stringWidth(title, 'Helvetica-Bold', 8)
    title_x = 25 + (25 - title_width) / 2
    pdf_file.drawString(title_x, y, title)

    pdf_file.rect(50, y-5, 50, 15, stroke=True)
    title = 'Depo'
    title_width = pdf_file.stringWidth(title, 'Helvetica-Bold', 8)
    title_x = 50 + (50 - title_width) / 2
    pdf_file.drawString(title_x, y, title)

    pdf_file.rect(100, y-5, 120, 15, stroke=True)
    title = 'No. Invoice'
    title_width = pdf_file.stringWidth(title, 'Helvetica-Bold', 8)
    title_x = 100 + (120 - title_width) / 2
    pdf_file.drawString(title_x, y, title)

    pdf_file.rect(220, y-5, 245, 15, stroke=True)
    title = 'Deskripsi'
    title_width = pdf_file.stringWidth(title, 'Helvetica-Bold', 8)
    title_x = 220 + (245 - title_width) / 2
    pdf_file.drawString(title_x, y, title)

    pdf_file.rect(465, y-5, 60, 15, stroke=True)
    title = 'Nilai Klaim'
    title_width = pdf_file.stringWidth(title, 'Helvetica-Bold', 8)
    title_x = 465 + (60 - title_width) / 2
    pdf_file.drawString(title_x, y, title)

    pdf_file.rect(525, y-5, 145, 15, stroke=True)
    title = 'No. Surat Program'
    title_width = pdf_file.stringWidth(title, 'Helvetica-Bold', 8)
    title_x = 525 + (145 - title_width) / 2
    pdf_file.drawString(title_x, y, title)

    pdf_file.rect(670, y-5, 145, 15, stroke=True)
    title = 'No. Proposal'
    title_width = pdf_file.stringWidth(title, 'Helvetica-Bold', 8)
    title_x = 670 + (145 - title_width) / 2
    pdf_file.drawString(title_x, y, title)

    pdf_file.setFont("Helvetica", 8)
    n = 0
    for i in cl_detail:
        y -= 15
        n += 1
        pdf_file.rect(25, y - 5, 25, 15, stroke=True)
        title = str(n)
        title_width = pdf_file.stringWidth(title, 'Helvetica', 8)
        title_x = 25 + (25 - title_width) / 2
        pdf_file.drawString(title_x, y, title)
        pdf_file.rect(50, y - 5, 50, 15, stroke=True)
        depo = Truncator(i.claim.depo.capitalize()).chars(
            9) if i.claim.depo else ''
        pdf_file.drawString(55, y, depo if i.claim.depo else '')
        pdf_file.rect(100, y - 5, 120, 15, stroke=True)
        pdf_file.drawString(105, y, i.claim.invoice)
        pdf_file.rect(220, y - 5, 245, 15, stroke=True)
        remarks = Truncator(i.claim.remarks).chars(55)
        pdf_file.drawString(225, y, remarks)
        pdf_file.rect(465, y - 5, 60, 15, stroke=True)
        pdf_file.drawRightString(520, y, "{:,}".format(i.claim.total_claim))
        pdf_file.rect(525, y - 5, 145, 15, stroke=True)
        pdf_file.drawString(530, y, i.claim.program_id)
        pdf_file.rect(670, y - 5, 145, 15, stroke=True)
        pdf_file.drawString(675, y, i.claim.proposal_id)
        if n % 20 == 0:
            footer(pdf_file)
            pdf_file.showPage()
            pdf_file.drawImage(logo_path, logo_x, 515,
                               width=logo_width, height=logo_height)
            pdf_file.setFont("Helvetica", 8)
            y = 500

    y -= 15
    pdf_file.setFont("Helvetica-Bold", 8)
    pdf_file.rect(25, y - 5, 790, 15, stroke=True)
    pdf_file.drawRightString(460, y, 'Total')
    pdf_file.drawRightString(520, y, "{:,}".format(detail_sum.get('total')))

    y -= 25
    pdf_file.setFont("Helvetica", 8)
    pdf_file.drawString(
        25, y, 'Demikian surat konfirmasi ini kami sampaikan. Atas perhatian dan kerjasamanya kami ucapkann terima kasih.')

    y -= 25
    if y == 155:
        footer(pdf_file)
        pdf_file.showPage()
        pdf_file.drawImage(logo_path, logo_x, 515,
                           width=logo_width, height=logo_height)
        pdf_file.setFont("Helvetica", 8)
        y = 500

    col_width = (page_width[0] - 50) / 11
    pdf_file.drawString(25, y, 'Hormat Kami,')
    pdf_file.drawString(25 + (col_width * 2), y, 'Mengetahui,')

    for i in range(1, approver.count() + 1):
        if approver:
            sign_path = User.objects.get(user_id=approver[i - 1].cl_approval_id).signature.path if User.objects.get(
                user_id=approver[i - 1].cl_approval_id).signature else ''
            pos = User.objects.get(
                user_id=approver[i - 1].cl_approval_id).position
            if sign_path:
                pdf_file.drawImage(sign_path, 25 + ((col_width * 2) * (i - 1)), y - 50,
                                   width=col_width - 10, height=40)
            else:
                pass

            pdf_file.setFont("Helvetica-Bold", 8)
            pdf_file.drawString(25 + ((col_width * 2) * (i - 1)),
                                y - 60, approver[i - 1].cl_approval_name)
            pdf_file.setFont("Helvetica", 8)
            pdf_file.drawString(25 + ((col_width * 2) * (i - 1)),
                                y - 70, str(pos))

    y -= 95
    pdf_file.setFont("Helvetica-Bold", 8)
    pdf_file.drawString(25, y, 'Cc : Finance Department')

    footer(pdf_file)

    pdf_file.save()

    return FileResponse(open(filename, 'rb'), content_type='application/pdf')


def footer(pdf_file):
    y = 50
    pdf_file.setFont("Helvetica-Bold", 7)
    pdf_file.drawString(
        25, y, 'PT. ABC PRESIDENT INDONESIA (www.abcpresident.com)')
    pdf_file.drawString(25, y - 10, 'Head Office : ')
    title_x = pdf_file.stringWidth('Head Office : ', 'Helvetica-Bold', 7)
    pdf_file.setFont("Helvetica", 7)
    address = 'EightyEight@Kasablanka Office Tower A Lt. 31 Jl. Casablanca Raya Kav. 88 Jakarta Selatan 12870 '
    pdf_file.drawString(25 + title_x, y - 10, address)
    address_x = pdf_file.stringWidth(address, 'Helvetica', 7)
    pdf_file.setFont("Helvetica-Bold", 7)
    pdf_file.drawString(25 + title_x + address_x, y - 10, 'Tel : ')
    tel_x = pdf_file.stringWidth('Tel : ', 'Helvetica-Bold', 7)
    pdf_file.setFont("Helvetica", 7)
    tel = '+62 21 2982 0168 (Hunting) '
    ph_x = pdf_file.stringWidth(tel, 'Helvetica', 7)
    pdf_file.drawString(25 + title_x + address_x + tel_x, y - 10, tel)
    pdf_file.setFont("Helvetica-Bold", 7)
    fax_x = pdf_file.stringWidth('Fax : ', 'Helvetica-Bold', 7)
    pdf_file.drawString(25 + title_x + address_x +
                        tel_x + ph_x, y - 10, 'Fax : ')
    pdf_file.setFont("Helvetica", 7)
    fax = '+62 21 2982 0166 '
    pdf_file.drawString(25 + title_x + address_x +
                        tel_x + ph_x + fax_x, y - 10, fax)
    pdf_file.setFont("Helvetica-Bold", 7)
    factory = 'Factory : '
    factory_x = pdf_file.stringWidth(factory, 'Helvetica-Bold', 7)
    pdf_file.drawString(25, y - 20, factory)
    pdf_file.setFont("Helvetica", 7)
    factory_address = 'Desa Walabar Kec. Klari, Karawang Timur 41371, Jawa Barat, Indonesia '
    pdf_file.drawString(25 + factory_x, y - 20, factory_address)
    factory_address_x = pdf_file.stringWidth(factory_address, 'Helvetica', 7)
    pdf_file.setFont("Helvetica-Bold", 7)
    pdf_file.drawString(25 + factory_x + factory_address_x, y - 20, 'Tel : ')
    factory_tel_x = pdf_file.stringWidth('Tel : ', 'Helvetica-Bold', 7)
    pdf_file.setFont("Helvetica", 7)
    factory_tel = '+62 267 431 422 (Hunting) '
    factory_ph_x = pdf_file.stringWidth(factory_tel, 'Helvetica', 7)
    pdf_file.drawString(25 + factory_x + factory_address_x +
                        factory_tel_x, y - 20, factory_tel)
    pdf_file.setFont("Helvetica-Bold", 7)
    factory_fax_x = pdf_file.stringWidth('Fax : ', 'Helvetica-Bold', 7)
    pdf_file.drawString(25 + factory_x + factory_address_x +
                        factory_tel_x + factory_ph_x, y - 20, 'Fax : ')
    pdf_file.setFont("Helvetica", 7)
    factory_fax = '+62 267 431 421'
    pdf_file.drawString(25 + factory_x + factory_address_x +
                        factory_tel_x + factory_ph_x + factory_fax_x, y - 20, factory_fax)


@login_required(login_url='/login/')
@role_required(allowed_roles='REGION')
def region_index(request):
    regions = Region.objects.all()

    context = {
        'data': regions,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'region',
        'group_segment': 'master',
        'crud': 'index',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='REGION') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/region_index.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='REGION')
def region_add(request):
    if request.POST:
        form = FormRegion(request.POST)
        if form.is_valid():
            region = form.save(commit=False)
            region.region_id = form.cleaned_data['region_id'].replace(' ', '')
            region.save()

            return HttpResponseRedirect(reverse('region-view', args=[region.region_id]))
    else:
        form = FormRegion()

    message = form.errors
    context = {
        'form': form,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'region',
        'group_segment': 'master',
        'crud': 'add',
        'message': message,
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list(
            'menu_id', flat=True),
        'btn': Auth.objects.get(
            user_id=request.user.user_id, menu_id='REGION') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/region_add.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='REGION')
def region_view(request, _id):
    region = Region.objects.get(region_id=_id)
    form = FormRegionView(instance=region)
    details = RegionDetail.objects.filter(region_id=_id)
    areas = AreaSales.objects.exclude(area_id__in=RegionDetail.objects.all().values_list('area_id', flat=True)).values_list(
        'area_id', 'area_name', 'regiondetail__region_id')

    if request.POST:
        check = request.POST.getlist('checks[]')
        for area in areas:
            if str(area[0]) in check:
                try:
                    detail = RegionDetail(region_id=_id, area_id=area[0])
                    detail.save()
                except IntegrityError:
                    continue
            else:
                RegionDetail.objects.filter(
                    region_id=_id, area_id=area[0]).delete()

    context = {
        'form': form,
        'data': region,
        'areas': areas,
        'detail': details,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'region',
        'group_segment': 'master',
        'crud': 'view',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list(
            'menu_id', flat=True),
        'btn': Auth.objects.get(
            user_id=request.user.user_id, menu_id='REGION') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/region_view.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='REGION')
def region_update(request, _id):
    region = Region.objects.get(region_id=_id)
    detail = RegionDetail.objects.filter(region_id=_id)

    if request.POST:
        form = FormRegionUpdate(request.POST, instance=region)
        if form.is_valid():
            region = form.save(commit=False)
            region.save()

            return HttpResponseRedirect(reverse('region-view', args=[_id]))
    else:
        form = FormRegionUpdate(instance=region)

    message = form.errors
    context = {
        'form': form,
        'data': region,
        'detail': detail,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'region',
        'group_segment': 'master',
        'crud': 'update',
        'message': message,
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list(
            'menu_id', flat=True),
        'btn': Auth.objects.get(
            user_id=request.user.user_id, menu_id='REGION') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/region_view.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='REGION')
def region_delete(request, _id):
    region = Region.objects.get(region_id=_id)
    region.delete()

    return HttpResponseRedirect(reverse('region-index'))


@login_required(login_url='/login/')
@role_required(allowed_roles='REGION')
def region_detail_delete(request, _id, _area):
    detail = RegionDetail.objects.get(region_id=_id, area_id=_area)
    detail.delete()

    return HttpResponseRedirect(reverse('region-view', args=[_id]))


@login_required(login_url='/login/')
@role_required(allowed_roles='REPORT')
def report_transfer(request, _from_yr, _from_mo, _to_yr, _to_mo, _distributor):
    from_date = datetime.date(int(_from_yr), int(
        _from_mo), 1) if _from_yr != '0' and _from_mo != '0' else datetime.date.today().replace(day=1)
    _to_date = datetime.date(int(_to_yr), int(
        _to_mo), 15) + datetime.timedelta(days=30) if _to_yr != '0' and _to_mo != '0' else datetime.date.today().replace(day=1)
    to_date = datetime.date(_to_date.year, _to_date.month,
                            1) if _to_yr != '0' and _to_mo != '0' else datetime.date.today().replace(day=1)
    years = [str(year) for year in BudgetTransfer.objects.dates(
        'date', 'year').distinct().values_list('date__year', flat=True)]
    distributors = Distributor.objects.all()
    months = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']

    if _distributor == 'all':
        transfer = BudgetTransfer.objects.filter(area__in=AreaUser.objects.filter(user_id=request.user.user_id).values_list('area_id', flat=True),
                                                 date__gte=from_date, date__lt=to_date)
    else:
        transfer = BudgetTransfer.objects.filter(area__in=AreaUser.objects.filter(user_id=request.user.user_id).values_list('area_id', flat=True),
                                                 date__gte=from_date, date__lt=to_date, distributor_id=_distributor)

    context = {
        'data': transfer,
        'from_year': _from_yr,
        'from_month': _from_mo,
        'to_year': _to_yr,
        'to_month': _to_mo,
        'selected_distributor': _distributor,
        'years': years,
        'distributors': distributors,
        'months': months,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'report_transfer',
        'group_segment': 'report',
        'crud': 'index',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='REPORT') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/report_transfer.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='REPORT')
def report_transfer_toxl(request, _from_yr, _from_mo, _to_yr, _to_mo, _distributor):
    from_date = datetime.date(int(_from_yr), int(
        _from_mo), 1) if _from_yr != '0' and _from_mo != '0' else datetime.date.today().replace(day=1)
    _to_date = datetime.date(int(_to_yr), int(
        _to_mo), 15) + datetime.timedelta(days=30) if _to_yr != '0' and _to_mo != '0' else datetime.date.today().replace(day=1)
    to_date = datetime.date(_to_date.year, _to_date.month,
                            1) if _to_yr != '0' and _to_mo != '0' else datetime.date.today().replace(day=1)

    if _distributor == 'all':
        transfer = BudgetTransfer.objects.filter(area__in=AreaUser.objects.filter(user_id=request.user.user_id).values_list('area_id', flat=True),
                                                 date__gte=from_date, date__lt=to_date)
    else:
        transfer = BudgetTransfer.objects.filter(area__in=AreaUser.objects.filter(user_id=request.user.user_id).values_list('area_id', flat=True),
                                                 date__gte=from_date, date__lt=to_date, distributor_id=_distributor)

    # Create a HttpResponse object with the csv data
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    filename = 'historical_transfer_' + \
        _from_mo + '_' + _from_yr + '_to_' + _to_mo + '_' + \
        _to_yr + '_distributor_' + _distributor + '.xlsx'
    response['Content-Disposition'] = 'attachment; filename=' + filename

    # Create an XlsxWriter workbook object and add a worksheet.
    workbook = xlsxwriter.Workbook(response, {'in_memory': True})
    worksheet = workbook.add_worksheet()

    # Define column headers
    headers = ['Transfer No.', 'Date', 'Area', 'Distributor',
               'Channel From', 'Channel To', 'Amount']

    # Define cell formats
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#7eaa55',
        'font_color': 'white',
        'border': 1,
        'align': 'center',
    })
    cell_format = workbook.add_format({'border': 1})
    date_format = workbook.add_format(
        {'border': 1, 'num_format': 'dd/mm/yyyy'})
    num_format = workbook.add_format({'border': 1, 'num_format': '#,##0'})

    # Set column width
    worksheet.set_column('A:A', 26)
    worksheet.set_column('B:C', 10)
    worksheet.set_column('D:D', 28)
    worksheet.set_column('E:F', 10)
    worksheet.set_column('G:G', 14)

    # Write data to XlsxWriter Object
    for idx, record in enumerate(transfer.values('transfer_id', 'date', 'area_id', 'distributor__distributor_name', 'channel_from_id', 'channel_to_id', 'amount')):
        for col_idx, (col_name, col_value) in enumerate(record.items()):
            if idx == 0:
                # Write the column headers on the first row
                worksheet.write(idx, col_idx, headers[col_idx], header_format)
            # Write the data rows
            if col_name == 'date':
                worksheet.write(idx + 1, col_idx, col_value, date_format)
            elif col_name == 'amount':
                worksheet.write(idx + 1, col_idx, col_value, num_format)
            else:
                worksheet.write(idx + 1, col_idx, col_value, cell_format)

    # Close the workbook before sending the data.
    workbook.close()

    return response


@login_required(login_url='/login/')
@role_required(allowed_roles='REPORT')
def report_cl(request, _from_yr, _from_mo, _to_yr, _to_mo, _distributor):
    from_date = datetime.date(int(_from_yr), int(
        _from_mo), 1) if _from_yr != '0' and _from_mo != '0' else datetime.date.today().replace(day=1)
    _to_date = datetime.date(int(_to_yr), int(
        _to_mo), 15) + datetime.timedelta(days=30) if _to_yr != '0' and _to_mo != '0' else datetime.date.today().replace(day=1)
    to_date = datetime.date(_to_date.year, _to_date.month,
                            1) if _to_yr != '0' and _to_mo != '0' else datetime.date.today().replace(day=1)
    years = [str(year) for year in CL.objects.dates(
        'cl_date', 'year').distinct().values_list('cl_date__year', flat=True)]
    distributors = Distributor.objects.all()
    months = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']

    if _distributor == 'all':
        cl = CLDetail.objects.filter(cl_id__area__in=AreaUser.objects.filter(user_id=request.user.user_id).values_list('area_id', flat=True),
                                     cl_id__cl_date__gte=from_date, cl_id__cl_date__lt=to_date)
    else:
        cl = CLDetail.objects.filter(cl_id__area__in=AreaUser.objects.filter(user_id=request.user.user_id).values_list('area_id', flat=True),
                                     cl_id__cl_date__gte=from_date, cl_id__cl_date__lt=to_date, cl_id__distributor_id=_distributor)

    context = {
        'data': cl,
        'from_year': _from_yr,
        'from_month': _from_mo,
        'to_year': _to_yr,
        'to_month': _to_mo,
        'selected_distributor': _distributor,
        'years': years,
        'distributors': distributors,
        'months': months,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'report_cl',
        'group_segment': 'report',
        'crud': 'index',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='REPORT') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/report_cl.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='REPORT')
def report_cl_toxl(request, _from_yr, _from_mo, _to_yr, _to_mo, _distributor):
    from_date = datetime.date(int(_from_yr), int(
        _from_mo), 1) if _from_yr != '0' and _from_mo != '0' else datetime.date.today().replace(day=1)
    _to_date = datetime.date(int(_to_yr), int(
        _to_mo), 15) + datetime.timedelta(days=30) if _to_yr != '0' and _to_mo != '0' else datetime.date.today().replace(day=1)
    to_date = datetime.date(_to_date.year, _to_date.month,
                            1) if _to_yr != '0' and _to_mo != '0' else datetime.date.today().replace(day=1)

    if _distributor == 'all':
        cl = CLDetail.objects.filter(cl_id__area__in=AreaUser.objects.filter(user_id=request.user.user_id).values_list('area_id', flat=True),
                                     cl_id__cl_date__gte=from_date, cl_id__cl_date__lt=to_date)
    else:
        cl = CLDetail.objects.filter(cl_id__area__in=AreaUser.objects.filter(user_id=request.user.user_id).values_list('area_id', flat=True),
                                     cl_id__cl_date__gte=from_date, cl_id__cl_date__lt=to_date, cl_id__distributor_id=_distributor)

    # Create a HttpResponse object with the csv data
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    filename = 'cl_list_' + \
        _from_mo + '_' + _from_yr + '_to_' + _to_mo + '_' + \
        _to_yr + '_distributor_' + _distributor + '.xlsx'
    response['Content-Disposition'] = 'attachment; filename=' + filename

    # Create an XlsxWriter workbook object and add a worksheet.
    workbook = xlsxwriter.Workbook(response, {'in_memory': True})
    worksheet = workbook.add_worksheet()

    # Define column headers
    headers = ['No.', 'Area', 'CL No.', 'Date', 'Depo', 'Claim No.', 'Invoice No.',
               'Distributor', 'Claim Description', 'Amount', 'Status', 'Remarks']

    # Define cell formats
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#7eaa55',
        'font_color': 'white',
        'border': 1,
        'align': 'center',
    })
    cell_format = workbook.add_format({'border': 1})
    date_format = workbook.add_format(
        {'border': 1, 'num_format': 'dd/mm/yyyy'})
    num_format = workbook.add_format({'border': 1, 'num_format': '#,##0'})

    # Set column width
    worksheet.set_column('A:A', 5)
    worksheet.set_column('B:B', 10)
    worksheet.set_column('C:C', 26)
    worksheet.set_column('D:E', 10)
    worksheet.set_column('F:G', 29)
    worksheet.set_column('H:H', 28)
    worksheet.set_column('I:I', 50)
    worksheet.set_column('J:J', 14)
    worksheet.set_column('K:K', 10)
    worksheet.set_column('L:L', 30)

    # Write data to XlsxWriter Object
    for idx, record in enumerate(cl.values('cl_id__area_id', 'cl_id', 'cl_id__cl_date', 'claim_id__depo', 'claim_id', 'claim__invoice', 'cl_id__distributor__distributor_name', 'claim__remarks', 'claim__total_claim', 'cl_id__status')):
        for col_idx, (col_name, col_value) in enumerate(record.items()):
            if idx == 0:
                # Write the column headers on the first row
                worksheet.write(idx, col_idx, headers[col_idx], header_format)
                worksheet.write(idx, 10, headers[10], header_format)
                worksheet.write(idx, 11, headers[11], header_format)
            # Write the data rows
            if col_idx == 0:
                worksheet.write(idx + 1, col_idx, idx + 1, cell_format)
            if col_name == 'cl_id__cl_date':
                worksheet.write(idx + 1, col_idx + 1, col_value, date_format)
            elif col_name == 'claim__total_claim':
                worksheet.write(idx + 1, col_idx + 1, col_value, num_format)
            elif col_name == 'cl_id__status':
                worksheet.write(
                    idx + 1, col_idx + 1, 'COMPLETED' if col_value == 'OPEN' else col_value, cell_format)
            else:
                worksheet.write(idx + 1, col_idx + 1, col_value, cell_format)

            worksheet.write(idx + 1, 11, '', cell_format)

    # Close the workbook before sending the data.
    workbook.close()

    return response


@login_required(login_url='/login/')
@role_required(allowed_roles='REPORT')
def report_claim(request, _from_yr, _from_mo, _to_yr, _to_mo, _distributor):
    from_date = datetime.date(int(_from_yr), int(
        _from_mo), 1) if _from_yr != '0' and _from_mo != '0' else datetime.date.today().replace(day=1)
    _to_date = datetime.date(int(_to_yr), int(
        _to_mo), 15) + datetime.timedelta(days=30) if _to_yr != '0' and _to_mo != '0' else datetime.date.today().replace(day=1)
    to_date = datetime.date(_to_date.year, _to_date.month,
                            1) if _to_yr != '0' and _to_mo != '0' else datetime.date.today().replace(day=1)
    years = [str(year) for year in Claim.objects.dates(
        'claim_date', 'year').distinct().values_list('claim_date__year', flat=True)]
    distributors = Distributor.objects.all()
    months = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']

    if _distributor == 'all':
        claim = Claim.objects.filter(area__in=AreaUser.objects.filter(user_id=request.user.user_id).values_list('area_id', flat=True),
                                     claim_date__gte=from_date, claim_date__lt=to_date).annotate(
                                         approver=ClaimRelease.objects.filter(claim_id=OuterRef(
                                             'claim_id'), claim_approval_status='N').order_by('sequence').values('claim_approval_name')[:1],
                                         revise_note=ClaimRelease.objects.filter(claim_id=OuterRef(
                                             'claim_id'), claim_approval_status='N').order_by('sequence').values('revise_note')[:1],
                                         return_note=ClaimRelease.objects.filter(claim_id=OuterRef(
                                             'claim_id'), claim_approval_status='N').order_by('sequence').values('return_note')[:1],
                                         reject_note=ClaimRelease.objects.filter(claim_id=OuterRef(
                                             'claim_id'), claim_approval_status='N').order_by('sequence').values('reject_note')[:1]
        ).values_list('claim_id', 'invoice', 'claim_date', 'invoice_date', 'proposal__budget__budget_distributor__distributor_name', 'area', 'depo', 'proposal__channel', 'proposal_id', 'proposal__program_name', 'remarks', 'total_claim', 'status', 'approver', 'claim_period', 'revise_note', 'return_note', 'reject_note')
    else:
        claim = Claim.objects.filter(area__in=AreaUser.objects.filter(user_id=request.user.user_id).values_list('area_id', flat=True),
                                     claim_date__gte=from_date, claim_date__lt=to_date, proposal__budget__budget_distributor=_distributor).annotate(
                                         approver=ClaimRelease.objects.filter(claim_id=OuterRef(
                                             'claim_id'), claim_approval_status='N').order_by('sequence').values('claim_approval_name')[:1],
                                         revise_note=ClaimRelease.objects.filter(claim_id=OuterRef(
                                             'claim_id'), claim_approval_status='N').order_by('sequence').values('revise_note')[:1],
                                         return_note=ClaimRelease.objects.filter(claim_id=OuterRef(
                                             'claim_id'), claim_approval_status='N').order_by('sequence').values('return_note')[:1],
                                         reject_note=ClaimRelease.objects.filter(claim_id=OuterRef(
                                             'claim_id'), claim_approval_status='N').order_by('sequence').values('reject_note')[:1]
        ).values_list('claim_id', 'invoice', 'claim_date', 'invoice_date', 'proposal__budget__budget_distributor__distributor_name', 'area', 'depo', 'proposal__channel', 'proposal_id', 'proposal__program_name', 'remarks', 'total_claim', 'status', 'approver', 'claim_period', 'revise_note', 'return_note', 'reject_note')

    context = {
        'data': claim,
        'from_year': _from_yr,
        'from_month': _from_mo,
        'to_year': _to_yr,
        'to_month': _to_mo,
        'selected_distributor': _distributor,
        'years': years,
        'distributors': distributors,
        'months': months,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'report_claim',
        'group_segment': 'report',
        'crud': 'index',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='REPORT') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/report_claim.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='REPORT')
def report_claim_toxl(request, _from_yr, _from_mo, _to_yr, _to_mo, _distributor):
    from_date = datetime.date(int(_from_yr), int(
        _from_mo), 1) if _from_yr != '0' and _from_mo != '0' else datetime.date.today().replace(day=1)
    _to_date = datetime.date(int(_to_yr), int(
        _to_mo), 15) + datetime.timedelta(days=30) if _to_yr != '0' and _to_mo != '0' else datetime.date.today().replace(day=1)
    to_date = datetime.date(_to_date.year, _to_date.month,
                            1) if _to_yr != '0' and _to_mo != '0' else datetime.date.today().replace(day=1)

    if _distributor == 'all':
        claim = Claim.objects.filter(area__in=AreaUser.objects.filter(user_id=request.user.user_id).values_list('area_id', flat=True),
                                     claim_date__gte=from_date, claim_date__lt=to_date).annotate(
            approver=ClaimRelease.objects.filter(claim_id=OuterRef(
                'claim_id'), claim_approval_status='N').order_by('sequence').values('claim_approval_name')[:1],
            revise_note=ClaimRelease.objects.filter(claim_id=OuterRef(
                'claim_id'), claim_approval_status='N').order_by('sequence').values('revise_note')[:1],
            return_note=ClaimRelease.objects.filter(claim_id=OuterRef(
                'claim_id'), claim_approval_status='N').order_by('sequence').values('return_note')[:1],
            reject_note=ClaimRelease.objects.filter(claim_id=OuterRef(
                'claim_id'), claim_approval_status='N').order_by('sequence').values('reject_note')[:1]
        ).values_list('claim_id', 'invoice', 'claim_date', 'invoice_date', 'proposal__budget__budget_distributor__distributor_name', 'area_id', 'depo', 'proposal__channel', 'proposal_id', 'proposal__program_name', 'remarks', 'claim_period', 'total_claim', 'status', 'approver', 'revise_note', 'return_note', 'reject_note')
    else:
        claim = Claim.objects.filter(area__in=AreaUser.objects.filter(user_id=request.user.user_id).values_list('area_id', flat=True),
                                     claim_date__gte=from_date, claim_date__lt=to_date, proposal__budget__budget_distributor=_distributor).annotate(
            approver=ClaimRelease.objects.filter(claim_id=OuterRef(
                'claim_id'), claim_approval_status='N').order_by('sequence').values('claim_approval_name')[:1],
            revise_note=ClaimRelease.objects.filter(claim_id=OuterRef(
                'claim_id'), claim_approval_status='N').order_by('sequence').values('revise_note')[:1],
            return_note=ClaimRelease.objects.filter(claim_id=OuterRef(
                'claim_id'), claim_approval_status='N').order_by('sequence').values('return_note')[:1],
            reject_note=ClaimRelease.objects.filter(claim_id=OuterRef(
                'claim_id'), claim_approval_status='N').order_by('sequence').values('reject_note')[:1]
        ).values_list('claim_id', 'invoice', 'claim_date', 'invoice_date', 'proposal__budget__budget_distributor__distributor_name', 'area_id', 'depo', 'proposal__channel', 'proposal_id', 'proposal__program_name', 'remarks', 'claim_period', 'total_claim', 'status', 'approver', 'revise_note', 'return_note', 'reject_note')

    # Create a HttpResponse object with the csv data
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    filename = 'claim_list_' + \
        _from_mo + '_' + _from_yr + '_to_' + _to_mo + '_' + \
        _to_yr + '_distributor_' + _distributor + '.xlsx'
    response['Content-Disposition'] = 'attachment; filename=' + filename

    # Create an XlsxWriter workbook object and add a worksheet.
    workbook = xlsxwriter.Workbook(response, {'in_memory': True})
    worksheet = workbook.add_worksheet()

    # Define column headers
    headers = ['No.', 'Claim No.', 'Invoice No.', 'Claim Date', 'Invoice Date', 'Distributor', 'Area', 'Depo',
               'Channel', 'Proposal No.', 'Program Name', 'Invoice Description', 'Claim Period', 'Curr', 'Amount', 'Status', 'By', 'Note']

    # Define cell formats
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#7eaa55',
        'font_color': 'white',
        'border': 1,
        'align': 'center',
    })
    cell_format = workbook.add_format({'border': 1})
    date_format = workbook.add_format(
        {'border': 1, 'num_format': 'dd/mm/yyyy'})
    date_back_format = workbook.add_format(
        {'border': 1, 'num_format': 'dd/mm/yyyy', 'bg_color': '#e5eedc'})
    num_format = workbook.add_format({'border': 1, 'num_format': '#,##0'})
    num_back_format = workbook.add_format(
        {'border': 1, 'num_format': '#,##0', 'bg_color': '#e5eedc'})
    back_format = workbook.add_format({'border': 1, 'bg_color': '#e5eedc'})

    # Set column width
    worksheet.set_column('A:A', 5)
    worksheet.set_column('B:C', 29)
    worksheet.set_column('D:E', 11)
    worksheet.set_column('F:F', 28)
    worksheet.set_column('G:G', 9)
    worksheet.set_column('H:H', 11)
    worksheet.set_column('I:I', 9)
    worksheet.set_column('J:J', 29)
    worksheet.set_column('K:K', 78)
    worksheet.set_column('L:L', 50)
    worksheet.set_column('M:M', 16)
    worksheet.set_column('N:N', 6)
    worksheet.set_column('O:O', 14)
    worksheet.set_column('P:P', 11)
    worksheet.set_column('Q:Q', 30)
    worksheet.set_column('R:R', 50)

    # Write data to XlsxWriter Object
    for idx, record in enumerate(claim):
        for col_idx, col_value in enumerate(record):
            if idx == 0:
                # Write the column headers on the first row
                worksheet.write(idx, col_idx, headers[col_idx], header_format)
            # Write the data rows
            if col_idx == 0:
                worksheet.write(idx + 1, col_idx, idx + 1, cell_format) if idx % 2 == 0 else worksheet.write(
                    idx + 1, col_idx, idx + 1, back_format)
            if col_idx == 2 or col_idx == 3:
                worksheet.write(idx + 1, col_idx + 1, col_value, date_format) if idx % 2 == 0 else worksheet.write(
                    idx + 1, col_idx + 1, col_value, date_back_format)
            elif col_idx == 12:
                worksheet.write(idx + 1, col_idx + 2, col_value, num_format) if idx % 2 == 0 else worksheet.write(
                    idx + 1, col_idx + 2, col_value, num_back_format)
            elif col_idx == 13:
                worksheet.write(idx + 1, col_idx + 2, 'COMPLETED' if col_value == 'OPEN' else col_value, cell_format) if idx % 2 == 0 else worksheet.write(
                    idx + 1, col_idx + 2, 'COMPLETED' if col_value == 'OPEN' else col_value, back_format)
            elif col_idx == 14:
                if idx % 2 == 0:
                    worksheet.write(idx + 1, col_idx + 2, col_value, cell_format) if record[13] == 'IN APPROVAL' or record[13] == 'REJECTED' else worksheet.write(
                        idx + 1, col_idx + 2, '', cell_format)
                else:
                    worksheet.write(idx + 1, col_idx + 2, col_value, back_format) if record[13] == 'IN APPROVAL' or record[13] == 'REJECTED' else worksheet.write(
                        idx + 1, col_idx + 2, '', back_format)
            elif col_idx == 15:
                if idx % 2 == 0:
                    worksheet.write(idx + 1, 17, col_value, cell_format) if record[13] == 'IN APPROVAL' and record[15] else worksheet.write(
                        idx + 1, 17, '', cell_format)
                else:
                    worksheet.write(idx + 1, 17, col_value, back_format) if record[13] == 'IN APPROVAL' and record[15] else worksheet.write(
                        idx + 1, 17, '', back_format)
            elif col_idx == 16:
                if idx % 2 == 0:
                    worksheet.write(idx + 1, 17, col_value, cell_format) if record[13] == 'IN APPROVAL' and record[16] else worksheet.write(
                        idx + 1, 17, '', cell_format)
                else:
                    worksheet.write(idx + 1, 17, col_value, back_format) if record[13] == 'IN APPROVAL' and record[16] else worksheet.write(
                        idx + 1, 17, '', back_format)
            elif col_idx == 17:
                if idx % 2 == 0:
                    worksheet.write(idx + 1, 17, col_value, cell_format) if record[13] == 'REJECTED' and record[17] else worksheet.write(
                        idx + 1, 17, '', cell_format)
                else:
                    worksheet.write(idx + 1, 17, col_value, back_format) if record[13] == 'REJECTED' and record[17] else worksheet.write(
                        idx + 1, 17, '', back_format)
            else:
                worksheet.write(idx + 1, col_idx + 1, col_value, cell_format) if idx % 2 == 0 else worksheet.write(
                    idx + 1, col_idx + 1, col_value, back_format)

            worksheet.write(idx + 1, 13, 'IDR', cell_format) if idx % 2 == 0 else worksheet.write(
                idx + 1, 13, 'IDR', back_format)

    # Close the workbook before sending the data.
    workbook.close()

    return response


@login_required(login_url='/login/')
@role_required(allowed_roles='REPORT')
def report_proposal_claim(request, _from_yr, _from_mo, _to_yr, _to_mo, _distributor):
    from_date = datetime.date(int(_from_yr), int(
        _from_mo), 1) if _from_yr != '0' and _from_mo != '0' else datetime.date.today().replace(day=1)
    _to_date = datetime.date(int(_to_yr), int(
        _to_mo), 15) + datetime.timedelta(days=30) if _to_yr != '0' and _to_mo != '0' else datetime.date.today().replace(day=1)
    to_date = datetime.date(_to_date.year, _to_date.month,
                            1) if _to_yr != '0' and _to_mo != '0' else datetime.date.today().replace(day=1)
    years = [str(year) for year in Proposal.objects.dates(
        'proposal_date', 'year').distinct().values_list('proposal_date__year', flat=True)]
    distributors = Distributor.objects.all()
    months = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']

    if _distributor == 'all':
        # proposal = Proposal.objects.filter(area__in=AreaUser.objects.filter(user_id=request.user.user_id).values_list('area_id', flat=True),
        #                                    proposal_date__gte=from_date, proposal_date__lt=to_date).annotate(
        #     difference=F('proposal_claim') - F('parked_claim'),
        #     approver=ProposalRelease.objects.filter(proposal_id=OuterRef(
        #         'proposal_id'), proposal_approval_status='N').order_by('sequence').values('proposal_approval_name')[:1],
        #     revise_note=ProposalRelease.objects.filter(proposal_id=OuterRef(
        #         'proposal_id'), proposal_approval_status='N').order_by('sequence').values('revise_note')[:1],
        #     return_note=ProposalRelease.objects.filter(proposal_id=OuterRef(
        #         'proposal_id'), proposal_approval_status='N').order_by('sequence').values('return_note')[:1],
        #     reject_note=ProposalRelease.objects.filter(proposal_id=OuterRef(
        #         'proposal_id'), proposal_approval_status='N').order_by('sequence').values('reject_note')[:1],
        # ).values_list(
        #     'area', 'budget__budget_distributor__distributor_name', 'channel', 'proposal_id', 'program_name', 'division__division_name', 'period_start', 'period_end', 'total_cost', 'difference', 'parked_claim', 'proposal_claim', 'balance', 'status', 'approver', 'revise_note', 'return_note', 'reject_note'
        # )

        proposal_query = """
        SELECT 
            area, 
            distributor_name, 
            channel, 
            proposal_id, 
            program_name, 
            apps_division.division_name, 
            DATE(CONCAT(budget_year, budget_month, '01')) AS budget_period,
            period_start, 
            period_end, 
            total_cost, 
            proposal_claim - parked_claim AS difference, 
            parked_claim, 
            proposal_claim, 
            balance, 
            status, 
            (
                SELECT proposal_approval_name 
                FROM apps_proposalrelease 
                WHERE proposal_id = apps_proposal.proposal_id 
                AND proposal_approval_status = 'N' 
                ORDER BY sequence 
                LIMIT 1
            ) AS approver, 
            (
                SELECT revise_note 
                FROM apps_proposalrelease 
                WHERE proposal_id = apps_proposal.proposal_id 
                AND proposal_approval_status = 'N' 
                ORDER BY sequence 
                LIMIT 1
            ) AS revise_note, 
            (
                SELECT return_note 
                FROM apps_proposalrelease 
                WHERE proposal_id = apps_proposal.proposal_id 
                AND proposal_approval_status = 'N' 
                ORDER BY sequence 
                LIMIT 1
            ) AS return_note, 
            (
                SELECT reject_note 
                FROM apps_proposalrelease 
                WHERE proposal_id = apps_proposal.proposal_id 
                AND proposal_approval_status = 'N' 
                ORDER BY sequence 
                LIMIT 1
            ) AS reject_note, 
            apps_proposal.update_date AS closed_date
        FROM 
            apps_proposal 
            INNER JOIN apps_areauser ON apps_proposal.area = apps_areauser.area_id 
            INNER JOIN apps_budget ON apps_proposal.budget_id = apps_budget.budget_id 
            INNER JOIN apps_distributor ON apps_budget.budget_distributor_id = apps_distributor.distributor_id 
            INNER JOIN apps_division ON apps_proposal.division_id = apps_division.division_id 
        WHERE 
            apps_areauser.user_id = %(user_id)s 
            AND proposal_date >= %(from_date)s 
            AND proposal_date < %(to_date)s
        """

        proposal_params = {
            'user_id': request.user.user_id,
            'from_date': from_date,
            'to_date': to_date
        }

        proposal = Proposal.objects.raw(proposal_query, params=proposal_params)
    else:
        # proposal = Proposal.objects.filter(area__in=AreaUser.objects.filter(user_id=request.user.user_id).values_list('area_id', flat=True),
        #                                    proposal_date__gte=from_date, proposal_date__lt=to_date, budget__budget_distributor=_distributor).annotate(
        #     difference=F('proposal_claim') - F('parked_claim'),
        #     approver=ProposalRelease.objects.filter(proposal_id=OuterRef(
        #         'proposal_id'), proposal_approval_status='N').order_by('sequence').values('proposal_approval_name')[:1],
        #     revise_note=ProposalRelease.objects.filter(proposal_id=OuterRef(
        #         'proposal_id'), proposal_approval_status='N').order_by('sequence').values('revise_note')[:1],
        #     return_note=ProposalRelease.objects.filter(proposal_id=OuterRef(
        #         'proposal_id'), proposal_approval_status='N').order_by('sequence').values('return_note')[:1],
        #     reject_note=ProposalRelease.objects.filter(proposal_id=OuterRef(
        #         'proposal_id'), proposal_approval_status='N').order_by('sequence').values('reject_note')[:1]
        # ).values_list(
        #     'area', 'budget__budget_distributor__distributor_name', 'channel', 'proposal_id', 'program_name', 'division__division_name', 'period_start', 'period_end', 'total_cost', 'difference', 'parked_claim', 'proposal_claim', 'balance', 'status', 'approver', 'revise_note', 'return_note', 'reject_note'
        # )

        proposal_query = """
        SELECT 
            area, 
            distributor_name, 
            channel, 
            proposal_id, 
            program_name, 
            apps_division.division_name, 
            DATE(CONCAT(budget_year, budget_month, '01')) AS budget_period, 
            period_start, 
            period_end, 
            total_cost, 
            proposal_claim - parked_claim AS difference, 
            parked_claim, 
            proposal_claim, 
            balance, 
            status, 
            (
                SELECT proposal_approval_name 
                FROM apps_proposalrelease 
                WHERE proposal_id = apps_proposal.proposal_id 
                AND proposal_approval_status = 'N' 
                ORDER BY sequence 
                LIMIT 1
            ) AS approver, 
            (
                SELECT revise_note 
                FROM apps_proposalrelease 
                WHERE proposal_id = apps_proposal.proposal_id 
                AND proposal_approval_status = 'N' 
                ORDER BY sequence 
                LIMIT 1
            ) AS revise_note, 
            (
                SELECT return_note 
                FROM apps_proposalrelease 
                WHERE proposal_id = apps_proposal.proposal_id 
                AND proposal_approval_status = 'N' 
                ORDER BY sequence 
                LIMIT 1
            ) AS return_note, 
            (
                SELECT reject_note 
                FROM apps_proposalrelease 
                WHERE proposal_id = apps_proposal.proposal_id 
                AND proposal_approval_status = 'N' 
                ORDER BY sequence 
                LIMIT 1
            ) AS reject_note, 
            apps_proposal.update_date AS closed_date
        FROM 
            apps_proposal 
            INNER JOIN apps_areauser ON apps_proposal.area = apps_areauser.area_id 
            INNER JOIN apps_budget ON apps_proposal.budget_id = apps_budget.budget_id 
            INNER JOIN apps_distributor ON apps_budget.budget_distributor_id = apps_distributor.distributor_id 
            INNER JOIN apps_division ON apps_proposal.division_id = apps_division.division_id 
        WHERE 
            apps_areauser.user_id = %(user_id)s 
            AND proposal_date >= %(from_date)s 
            AND proposal_date < %(to_date)s
            AND apps_budget.budget_distributor_id = %(distributor_id)s
        """

        proposal_params = {
            'user_id': request.user.user_id,
            'from_date': from_date,
            'to_date': to_date,
            'distributor_id': _distributor
        }

        proposal = Proposal.objects.raw(proposal_query, params=proposal_params)

    context = {
        'data': proposal,
        'from_year': _from_yr,
        'from_month': _from_mo,
        'to_year': _to_yr,
        'to_month': _to_mo,
        'selected_distributor': _distributor,
        'years': years,
        'distributors': distributors,
        'months': months,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'report_proposal_claim',
        'group_segment': 'report',
        'crud': 'index',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='REPORT') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/report_proposal_claim.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='REPORT')
def report_proposal_claim_toxl(request, _from_yr, _from_mo, _to_yr, _to_mo, _distributor):
    from_date = datetime.date(int(_from_yr), int(
        _from_mo), 1) if _from_yr != '0' and _from_mo != '0' else datetime.date.today().replace(day=1)
    _to_date = datetime.date(int(_to_yr), int(
        _to_mo), 15) + datetime.timedelta(days=30) if _to_yr != '0' and _to_mo != '0' else datetime.date.today().replace(day=1)
    to_date = datetime.date(_to_date.year, _to_date.month,
                            1) if _to_yr != '0' and _to_mo != '0' else datetime.date.today().replace(day=1)

    if _distributor == 'all':
        # proposal = Proposal.objects.filter(area__in=AreaUser.objects.filter(user_id=request.user.user_id).values_list('area_id', flat=True),
        #                                    proposal_date__gte=from_date, proposal_date__lt=to_date).annotate(
        #     difference=F('proposal_claim') - F('parked_claim'),
        #     approver=ProposalRelease.objects.filter(proposal_id=OuterRef(
        #         'proposal_id'), proposal_approval_status='N').order_by('sequence').values('proposal_approval_name')[:1],
        #     revise_note=ProposalRelease.objects.filter(proposal_id=OuterRef(
        #         'proposal_id'), proposal_approval_status='N').order_by('sequence').values('revise_note')[:1],
        #     return_note=ProposalRelease.objects.filter(proposal_id=OuterRef(
        #         'proposal_id'), proposal_approval_status='N').order_by('sequence').values('return_note')[:1],
        #     reject_note=ProposalRelease.objects.filter(proposal_id=OuterRef(
        #         'proposal_id'), proposal_approval_status='N').order_by('sequence').values('reject_note')[:1],
        # ).values_list(
        #     'area', 'budget__budget_distributor__distributor_name', 'channel', 'proposal_id', 'program_name', 'division__division_name', 'period_start', 'period_end', 'total_cost', 'difference', 'parked_claim', 'proposal_claim', 'balance', 'status', 'approver', 'revise_note', 'return_note', 'reject_note'
        # )

        proposal_query = """
        SELECT 
            area, 
            distributor_name, 
            channel, 
            proposal_id, 
            program_name, 
            apps_division.division_name, 
            DATE(CONCAT(budget_year, budget_month, '01')) AS budget_period, 
            period_start, 
            period_end, 
            total_cost, 
            (proposal_claim - parked_claim) AS difference, 
            parked_claim, 
            proposal_claim, 
            balance, 
            status, 
            (
                SELECT proposal_approval_name 
                FROM apps_proposalrelease 
                WHERE proposal_id = apps_proposal.proposal_id 
                AND proposal_approval_status = 'N' 
                ORDER BY sequence 
                LIMIT 1
            ) AS approver, 
            (
                SELECT revise_note 
                FROM apps_proposalrelease 
                WHERE proposal_id = apps_proposal.proposal_id 
                AND proposal_approval_status = 'N' 
                ORDER BY sequence 
                LIMIT 1
            ) AS revise_note, 
            (
                SELECT return_note 
                FROM apps_proposalrelease 
                WHERE proposal_id = apps_proposal.proposal_id 
                AND proposal_approval_status = 'N' 
                ORDER BY sequence 
                LIMIT 1
            ) AS return_note, 
            (
                SELECT reject_note 
                FROM apps_proposalrelease 
                WHERE proposal_id = apps_proposal.proposal_id 
                AND proposal_approval_status = 'N' 
                ORDER BY sequence 
                LIMIT 1
            ) AS reject_note, 
            apps_proposal.update_date AS closed_date
        FROM 
            apps_proposal 
            INNER JOIN apps_areauser ON apps_proposal.area = apps_areauser.area_id 
            INNER JOIN apps_budget ON apps_proposal.budget_id = apps_budget.budget_id 
            INNER JOIN apps_distributor ON apps_budget.budget_distributor_id = apps_distributor.distributor_id 
            INNER JOIN apps_division ON apps_proposal.division_id = apps_division.division_id 
        WHERE 
            apps_areauser.user_id = %(user_id)s 
            AND proposal_date >= %(from_date)s 
            AND proposal_date < %(to_date)s
        """

        proposal_params = {
            'user_id': request.user.user_id,
            'from_date': from_date,
            'to_date': to_date
        }

        with connection.cursor() as cursor:
            cursor.execute(proposal_query, proposal_params)
            proposal = cursor.fetchall()
    else:
        # proposal = Proposal.objects.filter(area__in=AreaUser.objects.filter(user_id=request.user.user_id).values_list('area_id', flat=True),
        #                                    proposal_date__gte=from_date, proposal_date__lt=to_date, budget__budget_distributor=_distributor).annotate(
        #     difference=F('proposal_claim') - F('parked_claim'),
        #     approver=ProposalRelease.objects.filter(proposal_id=OuterRef(
        #         'proposal_id'), proposal_approval_status='N').order_by('sequence').values('proposal_approval_name')[:1],
        #     revise_note=ProposalRelease.objects.filter(proposal_id=OuterRef(
        #         'proposal_id'), proposal_approval_status='N').order_by('sequence').values('revise_note')[:1],
        #     return_note=ProposalRelease.objects.filter(proposal_id=OuterRef(
        #         'proposal_id'), proposal_approval_status='N').order_by('sequence').values('return_note')[:1],
        #     reject_note=ProposalRelease.objects.filter(proposal_id=OuterRef(
        #         'proposal_id'), proposal_approval_status='N').order_by('sequence').values('reject_note')[:1],
        # ).values_list(
        #     'area', 'budget__budget_distributor__distributor_name', 'channel', 'proposal_id', 'program_name', 'division__division_name', 'period_start', 'period_end', 'total_cost', 'difference', 'parked_claim', 'proposal_claim', 'balance', 'status', 'approver', 'revise_note', 'return_note', 'reject_note'
        # )

        proposal_query = """
        SELECT 
            area, 
            distributor_name, 
            channel, 
            proposal_id, 
            program_name, 
            apps_division.division_name, 
            DATE(CONCAT(budget_year, budget_month, '01')) AS budget_period, 
            period_start, 
            period_end, 
            total_cost, 
            (proposal_claim - parked_claim) AS difference, 
            parked_claim, 
            proposal_claim, 
            balance, 
            status, 
            (
                SELECT proposal_approval_name 
                FROM apps_proposalrelease 
                WHERE proposal_id = apps_proposal.proposal_id 
                AND proposal_approval_status = 'N' 
                ORDER BY sequence 
                LIMIT 1
            ) AS approver, 
            (
                SELECT revise_note 
                FROM apps_proposalrelease 
                WHERE proposal_id = apps_proposal.proposal_id 
                AND proposal_approval_status = 'N' 
                ORDER BY sequence 
                LIMIT 1
            ) AS revise_note, 
            (
                SELECT return_note 
                FROM apps_proposalrelease 
                WHERE proposal_id = apps_proposal.proposal_id 
                AND proposal_approval_status = 'N' 
                ORDER BY sequence 
                LIMIT 1
            ) AS return_note, 
            (
                SELECT reject_note 
                FROM apps_proposalrelease 
                WHERE proposal_id = apps_proposal.proposal_id 
                AND proposal_approval_status = 'N' 
                ORDER BY sequence 
                LIMIT 1
            ) AS reject_note, 
            apps_proposal.update_date AS closed_date
        FROM 
            apps_proposal 
            INNER JOIN apps_areauser ON apps_proposal.area = apps_areauser.area_id 
            INNER JOIN apps_budget ON apps_proposal.budget_id = apps_budget.budget_id 
            INNER JOIN apps_distributor ON apps_budget.budget_distributor_id = apps_distributor.distributor_id 
            INNER JOIN apps_division ON apps_proposal.division_id = apps_division.division_id 
        WHERE 
            apps_areauser.user_id = %(user_id)s 
            AND proposal_date >= %(from_date)s 
            AND proposal_date < %(to_date)s
            AND apps_budget.budget_distributor_id = %(distributor_id)s
        """

        proposal_params = {
            'user_id': request.user.user_id,
            'from_date': from_date,
            'to_date': to_date,
            'distributor_id': _distributor
        }

        with connection.cursor() as cursor:
            cursor.execute(proposal_query, proposal_params)
            proposal = cursor.fetchall()

    # Create a HttpResponse object with the csv data
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    filename = 'proposal_claim_' + \
        _from_mo + '_' + _from_yr + '_to_' + _to_mo + '_' + \
        _to_yr + '_distributor_' + _distributor + '.xlsx'
    response['Content-Disposition'] = 'attachment; filename=' + filename

    # Create an XlsxWriter workbook object and add a worksheet.
    workbook = xlsxwriter.Workbook(response, {'in_memory': True})
    worksheet = workbook.add_worksheet()

    # Define column headers
    headers = ['Area', 'Distributor', 'Channel', 'Proposal No.', 'Program Name',
               'Division', 'Budget Period', 'Start', 'End', 'Budget', 'Actual', 'Parked', 'Assigned', 'Return', 'Available', 'Status', 'By', 'Note', 'Closed Period']

    # Define cell formats
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#7eaa55',
        'font_color': 'white',
        'border': 1,
        'align': 'center',
    })
    cell_format = workbook.add_format({'border': 1})
    date_format = workbook.add_format(
        {'border': 1, 'num_format': 'dd/mm/yyyy', 'align': 'left'})
    period_format = workbook.add_format(
        {'border': 1, 'num_format': 'mmm yyyy', 'align': 'left'})
    num_format = workbook.add_format({'border': 1, 'num_format': '#,##0'})

    # Set column width
    worksheet.set_column('A:A', 9)
    worksheet.set_column('B:B', 32)
    worksheet.set_column('C:C', 9)
    worksheet.set_column('D:D', 29)
    worksheet.set_column('E:E', 80)
    worksheet.set_column('F:F', 16)
    worksheet.set_column('G:G', 12)
    worksheet.set_column('H:I', 11)
    worksheet.set_column('J:O', 14)
    worksheet.set_column('P:P', 10)
    worksheet.set_column('Q:Q', 30)
    worksheet.set_column('R:R', 50)
    worksheet.set_column('S:S', 16)

    # Write data to XlsxWriter Object
    for idx, record in enumerate(proposal):
        for col_idx, col_value in enumerate(record):
            if idx == 0 and col_idx < 19:
                # Write the column headers on the first row
                worksheet.write(idx, col_idx, headers[col_idx], header_format)
            # Write the data rows
            if col_idx == 6:
                worksheet.write(idx + 1, col_idx, col_value, period_format)
            elif col_idx == 7 or col_idx == 8:
                worksheet.write(idx + 1, col_idx, col_value, date_format)
            elif col_idx == 9 or col_idx == 10 or col_idx == 11 or col_idx == 12:
                worksheet.write(idx + 1, col_idx, col_value, num_format)
            elif col_idx == 13:
                worksheet.write(idx + 1, col_idx, col_value,
                                num_format) if record[14] == 'CLOSED' else worksheet.write(idx + 1, col_idx, 0, num_format)
                worksheet.write(idx + 1, 14, 0, num_format) if record[14] == 'CLOSED' else worksheet.write(
                    idx + 1, 14, col_value, num_format)
            elif col_idx == 14:
                worksheet.write(
                    idx + 1, col_idx + 1, 'COMPLETED' if col_value == 'OPEN' else col_value, cell_format)
            elif col_idx == 15:
                worksheet.write(idx + 1, col_idx + 1, col_value, cell_format) if record[14] == 'IN APPROVAL' or record[14] == 'REJECTED' else worksheet.write(
                    idx + 1, col_idx + 1, '', cell_format)
            elif col_idx == 16:
                worksheet.write(
                    idx + 1, 17, col_value, cell_format) if record[14] == 'IN APPROVAL' and record[16] else worksheet.write(idx + 1, 17, '', cell_format)
            elif col_idx == 17:
                worksheet.write(
                    idx + 1, 17, col_value, cell_format) if record[14] == 'IN APPROVAL' and record[17] else worksheet.write(idx + 1, 17, '', cell_format)
            elif col_idx == 18:
                worksheet.write(
                    idx + 1, 17, col_value, cell_format) if record[14] == 'REJECTED' and record[18] else worksheet.write(idx + 1, 17, '', cell_format)
            elif col_idx == 19:
                worksheet.write(
                    idx + 1, 18, col_value, period_format) if record[14] == 'CLOSED' else worksheet.write(idx + 1, 18, '', period_format)
            else:
                worksheet.write(idx + 1, col_idx, col_value, cell_format)

    # Close the workbook before sending the data.
    workbook.close()

    return response


@login_required(login_url='/login/')
@role_required(allowed_roles='REPORT')
def report_proposal(request, _from_yr, _from_mo, _to_yr, _to_mo, _distributor):
    from_date = datetime.date(int(_from_yr), int(
        _from_mo), 1) if _from_yr != '0' and _from_mo != '0' else datetime.date.today().replace(day=1)
    _to_date = datetime.date(int(_to_yr), int(
        _to_mo), 15) + datetime.timedelta(days=30) if _to_yr != '0' and _to_mo != '0' else datetime.date.today().replace(day=1)
    to_date = datetime.date(_to_date.year, _to_date.month,
                            1) if _to_yr != '0' and _to_mo != '0' else datetime.date.today().replace(day=1)
    years = [str(year) for year in Proposal.objects.dates(
        'proposal_date', 'year').distinct().values_list('proposal_date__year', flat=True)]
    distributors = Distributor.objects.all()
    months = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']

    if _distributor == 'all':
        # proposal = Proposal.objects.filter(area__in=AreaUser.objects.filter(user_id=request.user.user_id).values_list('area_id', flat=True),
        #                                    proposal_date__gte=from_date, proposal_date__lt=to_date).annotate(
        #     sum_swop_carton=Sum('incrementalsales__swop_carton'),
        #     sum_swop_nom=Sum('incrementalsales__swop_nom'),
        #     sum_swp_carton=Sum('incrementalsales__swp_carton'),
        #     sum_swp_nom=Sum('incrementalsales__swp_nom'),
        #     sum_incrp_carton=Sum('incrementalsales__incrp_carton'),
        #     sum_incrp_nom=Sum('incrementalsales__incrp_nom'),
        #     incpct_carton=Sum('incrementalsales__incrp_carton') /
        #     Sum('incrementalsales__swop_carton') * 100,
        #     incpct_nom=Sum('incrementalsales__incrp_nom') /
        #     Sum('incrementalsales__swop_nom') * 100
        # ).values_list(
        #     'area', 'budget__budget_distributor__distributor_name', 'channel', 'proposal_id', 'program_name', 'program__program_id', 'division__division_name', 'period_start', 'period_end', 'total_cost', 'sum_swop_carton', 'sum_swop_nom', 'sum_swp_carton', 'sum_swp_nom', 'sum_incrp_carton', 'sum_incrp_nom', 'incpct_carton', 'incpct_nom', 'status',
        #     ProposalRelease.objects.filter(proposal_id=OuterRef('proposal_id'), proposal_approval_status='N').order_by(
        #         'sequence').values('proposal_approval_name')[:1],
        #     ProposalRelease.objects.filter(proposal_id=OuterRef(
        #         'proposal_id'), proposal_approval_status='N').order_by('sequence').values('revise_note')[:1],
        #     ProposalRelease.objects.filter(proposal_id=OuterRef(
        #         'proposal_id'), proposal_approval_status='N').order_by('sequence').values('return_note')[:1],
        #     ProposalRelease.objects.filter(proposal_id=OuterRef(
        #         'proposal_id'), proposal_approval_status='N').order_by('sequence').values('reject_note')[:1]
        # )
        proposal = Proposal.objects.filter(area__in=AreaUser.objects.filter(user_id=request.user.user_id).values_list('area_id', flat=True),
                                           proposal_date__gte=from_date, proposal_date__lt=to_date).annotate(
            sum_swop_carton=Sum('incrementalsales__swop_carton'),
            sum_swop_nom=Sum('incrementalsales__swop_nom'),
            sum_swp_carton=Sum('incrementalsales__swp_carton'),
            sum_swp_nom=Sum('incrementalsales__swp_nom'),
            sum_incrp_carton=Sum('incrementalsales__incrp_carton'),
            sum_incrp_nom=Sum('incrementalsales__incrp_nom'),
            incpct_carton=Sum('incrementalsales__incrp_carton') /
            Sum('incrementalsales__swop_carton') * 100,
            incpct_nom=Sum('incrementalsales__incrp_nom') /
            Sum('incrementalsales__swop_nom') * 100
        ).values_list(
            'area', 'budget__budget_distributor__distributor_name', 'channel', 'proposal_id', 'program_name', 'program__program_id', 'division__division_name', 'period_start', 'period_end', 'total_cost', 'sum_swop_carton', 'sum_swop_nom', 'sum_swp_carton', 'sum_swp_nom', 'sum_incrp_carton', 'sum_incrp_nom', 'incpct_carton', 'incpct_nom', 'status',
            ProposalRelease.objects.filter(proposal_id=OuterRef('proposal_id'), proposal_approval_status='N').order_by(
                'sequence').values('proposal_approval_name')[:1],
            ProposalRelease.objects.filter(proposal_id=OuterRef(
                'proposal_id'), proposal_approval_status='N').order_by('sequence').values('revise_note')[:1],
            ProposalRelease.objects.filter(proposal_id=OuterRef(
                'proposal_id'), proposal_approval_status='N').order_by('sequence').values('return_note')[:1],
            ProposalRelease.objects.filter(proposal_id=OuterRef(
                'proposal_id'), proposal_approval_status='N').order_by('sequence').values('reject_note')[:1]
        )
    else:
        proposal = Proposal.objects.filter(area__in=AreaUser.objects.filter(user_id=request.user.user_id).values_list('area_id', flat=True),
                                           proposal_date__gte=from_date, proposal_date__lt=to_date, budget__budget_distributor=_distributor).annotate(
            sum_swop_carton=Sum('incrementalsales__swop_carton'),
            sum_swop_nom=Sum('incrementalsales__swop_nom'),
            sum_swp_carton=Sum('incrementalsales__swp_carton'),
            sum_swp_nom=Sum('incrementalsales__swp_nom'),
            sum_incrp_carton=Sum('incrementalsales__incrp_carton'),
            sum_incrp_nom=Sum('incrementalsales__incrp_nom'),
            incpct_carton=Sum('incrementalsales__incrp_carton') /
            Sum('incrementalsales__swop_carton') * 100,
            incpct_nom=Sum('incrementalsales__incrp_nom') /
            Sum('incrementalsales__swop_nom') * 100
        ).values_list(
            'area', 'budget__budget_distributor__distributor_name', 'channel', 'proposal_id', 'program_name', 'program__program_id', 'division__division_name', 'period_start', 'period_end', 'total_cost', 'sum_swop_carton', 'sum_swop_nom', 'sum_swp_carton', 'sum_swp_nom', 'sum_incrp_carton', 'sum_incrp_nom', 'incpct_carton', 'incpct_nom', 'status',
            ProposalRelease.objects.filter(proposal_id=OuterRef('proposal_id'), proposal_approval_status='N').order_by(
                'sequence').values('proposal_approval_name')[:1],
            ProposalRelease.objects.filter(proposal_id=OuterRef(
                'proposal_id'), proposal_approval_status='N').order_by('sequence').values('revise_note')[:1],
            ProposalRelease.objects.filter(proposal_id=OuterRef(
                'proposal_id'), proposal_approval_status='N').order_by('sequence').values('return_note')[:1],
            ProposalRelease.objects.filter(proposal_id=OuterRef(
                'proposal_id'), proposal_approval_status='N').order_by('sequence').values('reject_note')[:1]
        )

    context = {
        'data': proposal,
        'from_year': _from_yr,
        'from_month': _from_mo,
        'to_year': _to_yr,
        'to_month': _to_mo,
        'selected_distributor': _distributor,
        'years': years,
        'distributors': distributors,
        'months': months,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'report_proposal',
        'group_segment': 'report',
        'crud': 'index',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='REPORT') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/report_proposal.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='REPORT')
def report_proposal_toxl(request, _from_yr, _from_mo, _to_yr, _to_mo, _distributor):
    from_date = datetime.date(int(_from_yr), int(
        _from_mo), 1) if _from_yr != '0' and _from_mo != '0' else datetime.date.today().replace(day=1)
    _to_date = datetime.date(int(_to_yr), int(
        _to_mo), 15) + datetime.timedelta(days=30) if _to_yr != '0' and _to_mo != '0' else datetime.date.today().replace(day=1)
    to_date = datetime.date(_to_date.year, _to_date.month,
                            1) if _to_yr != '0' and _to_mo != '0' else datetime.date.today().replace(day=1)

    if _distributor == 'all':
        proposal = Proposal.objects.filter(area__in=AreaUser.objects.filter(user_id=request.user.user_id).values_list('area_id', flat=True),
                                           proposal_date__gte=from_date, proposal_date__lt=to_date).annotate(
            sum_swop_carton=Sum('incrementalsales__swop_carton'),
            sum_swop_nom=Sum('incrementalsales__swop_nom'),
            sum_swp_carton=Sum('incrementalsales__swp_carton'),
            sum_swp_nom=Sum('incrementalsales__swp_nom'),
            sum_incrp_carton=Sum('incrementalsales__incrp_carton'),
            sum_incrp_nom=Sum('incrementalsales__incrp_nom'),
            incpct_carton=Sum('incrementalsales__incrp_carton') /
            Sum('incrementalsales__swop_carton'),
            incpct_nom=Sum('incrementalsales__incrp_nom') /
            Sum('incrementalsales__swop_nom'),
            approver=ProposalRelease.objects.filter(proposal_id=OuterRef(
                'proposal_id'), proposal_approval_status='N').order_by('sequence').values('proposal_approval_name')[:1],
            revise_note=ProposalRelease.objects.filter(proposal_id=OuterRef(
                'proposal_id'), proposal_approval_status='N').order_by('sequence').values('revise_note')[:1],
            return_note=ProposalRelease.objects.filter(proposal_id=OuterRef(
                'proposal_id'), proposal_approval_status='N').order_by('sequence').values('return_note')[:1],
            reject_note=ProposalRelease.objects.filter(proposal_id=OuterRef(
                'proposal_id'), proposal_approval_status='N').order_by('sequence').values('reject_note')[:1],
        ).values_list(
            'area', 'budget__budget_distributor__distributor_name', 'channel', 'proposal_id', 'program_name', 'program__program_id', 'division__division_name', 'period_start', 'period_end', 'total_cost', 'sum_swop_carton', 'sum_swop_nom', 'sum_swp_carton', 'sum_swp_nom', 'sum_incrp_carton', 'sum_incrp_nom', 'incpct_carton', 'incpct_nom', 'status',
            'approver', 'revise_note', 'return_note', 'reject_note'
        )
    else:
        proposal = Proposal.objects.filter(area__in=AreaUser.objects.filter(user_id=request.user.user_id).values_list('area_id', flat=True),
                                           proposal_date__gte=from_date, proposal_date__lt=to_date, budget__budget_distributor=_distributor).annotate(
            sum_swop_carton=Sum('incrementalsales__swop_carton'),
            sum_swop_nom=Sum('incrementalsales__swop_nom'),
            sum_swp_carton=Sum('incrementalsales__swp_carton'),
            sum_swp_nom=Sum('incrementalsales__swp_nom'),
            sum_incrp_carton=Sum('incrementalsales__incrp_carton'),
            sum_incrp_nom=Sum('incrementalsales__incrp_nom'),
            incpct_carton=Sum('incrementalsales__incrp_carton') /
            Sum('incrementalsales__swop_carton'),
            incpct_nom=Sum('incrementalsales__incrp_nom') /
            Sum('incrementalsales__swop_nom'),
            approver=ProposalRelease.objects.filter(proposal_id=OuterRef(
                'proposal_id'), proposal_approval_status='N').order_by('sequence').values('proposal_approval_name')[:1],
            revise_note=ProposalRelease.objects.filter(proposal_id=OuterRef(
                'proposal_id'), proposal_approval_status='N').order_by('sequence').values('revise_note')[:1],
            return_note=ProposalRelease.objects.filter(proposal_id=OuterRef(
                'proposal_id'), proposal_approval_status='N').order_by('sequence').values('return_note')[:1],
            reject_note=ProposalRelease.objects.filter(proposal_id=OuterRef(
                'proposal_id'), proposal_approval_status='N').order_by('sequence').values('reject_note')[:1],
        ).values_list(
            'area', 'budget__budget_distributor__distributor_name', 'channel', 'proposal_id', 'program_name', 'program__program_id', 'division__division_name', 'period_start', 'period_end', 'total_cost', 'sum_swop_carton', 'sum_swop_nom', 'sum_swp_carton', 'sum_swp_nom', 'sum_incrp_carton', 'sum_incrp_nom', 'incpct_carton', 'incpct_nom', 'status',
            'approver', 'revise_note', 'return_note', 'reject_note'
        )

    # Create a HttpResponse object with the csv data
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    filename = 'proposal_' + \
        _from_mo + '_' + _from_yr + '_to_' + _to_mo + '_' + \
        _to_yr + '_distributor_' + _distributor + '.xlsx'
    response['Content-Disposition'] = 'attachment; filename=' + filename

    # Create an XlsxWriter workbook object and add a worksheet.
    workbook = xlsxwriter.Workbook(response, {'in_memory': True})
    worksheet = workbook.add_worksheet()

    # Define column headers
    headers = ['Area', 'Distributor', 'Channel', 'Proposal No.', 'Program Name', 'Program No.', 'Division', 'Start', 'End', 'Budget',
               'Sales Without Program (CTN)', 'Sales Without Program (Rp)', 'Sales With Program (CTN)', 'Sales With Program (Rp)', 'Incremental (CTN)', 'Incremental (Rp)', 'Incremental % (CTN)', 'Incremental % (Rp)', 'Status', 'By', 'Note']

    # Define cell formats
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#7eaa55',
        'font_color': 'white',
        'border': 1,
        'align': 'center',
    })
    cell_format = workbook.add_format({'border': 1})
    date_format = workbook.add_format(
        {'border': 1, 'num_format': 'dd/mm/yyyy'})
    num_format = workbook.add_format({'border': 1, 'num_format': '#,##0'})
    percent_format = workbook.add_format(
        {'border': 1, 'num_format': '#,##0.0%'})

    # Set column width
    worksheet.set_column('A:A', 9)
    worksheet.set_column('B:B', 32)
    worksheet.set_column('C:C', 9)
    worksheet.set_column('D:D', 29)
    worksheet.set_column('E:E', 80)
    worksheet.set_column('F:F', 29)
    worksheet.set_column('G:G', 16)
    worksheet.set_column('H:I', 11)
    worksheet.set_column('J:J', 14)
    worksheet.set_column('K:R', 24)
    worksheet.set_column('S:S', 12)
    worksheet.set_column('T:T', 30)
    worksheet.set_column('U:U', 50)

    # Write data to XlsxWriter Object
    for idx, record in enumerate(proposal):
        for col_idx, col_value in enumerate(record):
            if idx == 0 and col_idx < 21:
                # Write the column headers on the first row
                worksheet.write(idx, col_idx, headers[col_idx], header_format)
            # Write the data rows
            if col_idx == 7 or col_idx == 8:
                worksheet.write(idx + 1, col_idx, col_value, date_format)
            elif col_idx == 9 or col_idx == 10 or col_idx == 11 or col_idx == 12 or col_idx == 13 or col_idx == 14 or col_idx == 15:
                worksheet.write(idx + 1, col_idx, col_value, num_format)
            elif col_idx == 16:
                formula = f'=IFERROR({xlsxwriter.utility.xl_rowcol_to_cell(idx + 1, 14)} / {xlsxwriter.utility.xl_rowcol_to_cell(idx + 1, 10)}, 0)'
                worksheet.write(idx + 1, col_idx, formula, percent_format)
            elif col_idx == 17:
                formula = f'=IFERROR({xlsxwriter.utility.xl_rowcol_to_cell(idx + 1, 15)} / {xlsxwriter.utility.xl_rowcol_to_cell(idx + 1, 11)}, 0)'
                worksheet.write(idx + 1, col_idx, formula, percent_format)
            elif col_idx == 18:
                worksheet.write(
                    idx + 1, col_idx, 'COMPLETED' if col_value == 'OPEN' else col_value, cell_format)
            elif col_idx == 19:
                worksheet.write(idx + 1, col_idx, col_value, cell_format) if record[18] == 'IN APPROVAL' or record[18] == 'REJECTED' else worksheet.write(
                    idx + 1, col_idx, '', cell_format)
            elif col_idx == 20:
                worksheet.write(
                    idx + 1, 20, col_value, cell_format) if record[18] == 'IN APPROVAL' and record[20] else worksheet.write(idx + 1, 20, '', cell_format)
            elif col_idx == 21:
                worksheet.write(
                    idx + 1, 20, col_value, cell_format) if record[18] == 'IN APPROVAL' and record[21] else worksheet.write(idx + 1, 20, '', cell_format)
            elif col_idx == 22:
                worksheet.write(
                    idx + 1, 20, col_value, cell_format) if record[18] == 'REJECTED' and record[22] else worksheet.write(idx + 1, 20, '', cell_format)
            else:
                worksheet.write(idx + 1, col_idx, col_value, cell_format)

    # Close the workbook before sending the data.
    workbook.close()

    return response


@login_required(login_url='/login/')
@role_required(allowed_roles='REPORT')
def report_monthly_budget(request, _from_yr, _from_mo, _to_yr, _to_mo, _distributor):
    years = [str(year) for year in Budget.objects.filter(budget_status__in=[
        'OPEN', 'CLOSED', 'DRAFT', 'IN APPROVAL']).exclude(budget_status='DRAFT', budget_new=True).values_list('budget_year', flat=True).distinct()]
    distributors = Distributor.objects.all()
    months = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
    curr_bal = 0
    total_bal = 0

    if _distributor == 'all':
        max_name = Budget.objects.filter(budget_status__in=['OPEN', 'CLOSED', 'DRAFT', 'IN APPROVAL'], budget_year=_from_yr, budget_month='{:02d}'.format(
            int(_from_mo))).exclude(budget_status='DRAFT', budget_new=True).aggregate(max_length=Max(Length('budget_distributor__distributor_name')))
        max_len = max_name.get('max_length') if max_name.get(
            'max_length') else 0
        scrollX = True if max_len > 25 else False

        budgets = Budget.objects.filter(budget_status__in=['OPEN', 'CLOSED', 'DRAFT', 'IN APPROVAL'], budget_area__in=AreaUser.objects.filter(user_id=request.user.user_id).values_list('area_id', flat=True),
                                        budget_year=_from_yr, budget_month='{:02d}'.format(int(_from_mo))).exclude(budget_status='DRAFT', budget_new=True).annotate(
            proposed=F('budget_total') +
            Sum('budgetdetail__budget_remaining') - F('budget_balance'),
            draft_proposed=F('budget_amount') + Sum('budgetdetail__budget_remaining') - (Sum('budgetdetail__budget_amount') + Sum('budgetdetail__budget_transfer_plus') - Sum(
                'budgetdetail__budget_transfer_minus') - Sum('budgetdetail__budget_proposed') + Sum('budgetdetail__budget_remaining')),
            remaining=Sum('budgetdetail__budget_remaining'),
            draft_tot_bal=Sum('budgetdetail__budget_amount') + Sum('budgetdetail__budget_transfer_plus') - Sum(
                'budgetdetail__budget_transfer_minus') - Sum('budgetdetail__budget_proposed') + Sum('budgetdetail__budget_remaining'),
        ).prefetch_related(Prefetch('budgetdetail_set', BudgetDetail.objects.all().annotate(
            transfer=F('budget_transfer_plus') -
            F('budget_transfer_minus'),
            beginning_mo=F('budget_transfer_plus') -
            F('budget_transfer_minus') + F('budget_total'),
            draft_curr_bal=F('budget_amount') +
            F('budget_transfer_plus') - F('budget_transfer_minus'),
            draft_balance=F('budget_amount') + F('budget_transfer_plus') - F(
                'budget_transfer_minus') - F('budget_proposed') + F('budget_remaining'),
        ), to_attr='details'))

        total = Budget.objects.filter(budget_status__in=['OPEN', 'CLOSED', 'DRAFT', 'IN APPROVAL'], budget_area__in=AreaUser.objects.filter(user_id=request.user.user_id).values_list('area_id', flat=True),
                                      budget_year=_from_yr, budget_month='{:02d}'.format(int(_from_mo))).exclude(budget_status='DRAFT', budget_new=True).aggregate(
            begin_bal=Sum('budgetdetail__budget_amount'),
            proposed=Sum('budgetdetail__budget_total') + Sum(
                'budgetdetail__budget_remaining') - Sum('budgetdetail__budget_balance'),
            remaining=Sum('budgetdetail__budget_remaining'),
            balance=Sum('budgetdetail__budget_balance'))

        draft_total = Budget.objects.filter(budget_status__in=['OPEN', 'CLOSED'], budget_area__in=AreaUser.objects.filter(user_id=request.user.user_id).values_list('area_id', flat=True),
                                            budget_year=_from_yr, budget_month='{:02d}'.format(int(_from_mo))).aggregate(
            upping=Sum('budgetdetail__budget_upping'))
    else:
        max_name = Budget.objects.filter(budget_status__in=['OPEN', 'CLOSED', 'DRAFT', 'IN APPROVAL'], budget_year=_from_yr, budget_month='{:02d}'.format(int(_from_mo)), budget_distributor=_distributor).exclude(budget_status='DRAFT', budget_new=True).aggregate(
            max_length=Max(Length('budget_distributor__distributor_name')))
        max_len = max_name.get('max_length') if max_name.get(
            'max_length') else 0
        scrollX = True if max_len > 25 else False

        budgets = Budget.objects.filter(budget_distributor=_distributor, budget_status__in=['OPEN', 'CLOSED', 'DRAFT', 'IN APPROVAL'], budget_area__in=AreaUser.objects.filter(user_id=request.user.user_id).values_list('area_id', flat=True),
                                        budget_year=_from_yr, budget_month='{:02d}'.format(int(_from_mo))).exclude(budget_status='DRAFT', budget_new=True).annotate(
            proposed=F('budget_total') +
            Sum('budgetdetail__budget_remaining') - F('budget_balance'),
            draft_proposed=F('budget_amount') + Sum('budgetdetail__budget_remaining') - (Sum('budgetdetail__budget_amount') + Sum('budgetdetail__budget_transfer_plus') - Sum(
                'budgetdetail__budget_transfer_minus') - Sum('budgetdetail__budget_proposed') + Sum('budgetdetail__budget_remaining')),
            remaining=Sum('budgetdetail__budget_remaining'),
            draft_tot_bal=Sum('budgetdetail__budget_amount') + Sum('budgetdetail__budget_transfer_plus') - Sum(
                'budgetdetail__budget_transfer_minus') - Sum('budgetdetail__budget_proposed') + Sum('budgetdetail__budget_remaining'),
        ).prefetch_related(Prefetch('budgetdetail_set', BudgetDetail.objects.all().annotate(
            transfer=F('budget_transfer_plus') -
            F('budget_transfer_minus'),
            beginning_mo=F('budget_transfer_plus') -
            F('budget_transfer_minus') + F('budget_total'),
            draft_curr_bal=F('budget_amount') +
            F('budget_transfer_plus') - F('budget_transfer_minus'),
            draft_balance=F('budget_amount') + F('budget_transfer_plus') - F(
                'budget_transfer_minus') - F('budget_proposed') + F('budget_remaining'),
        ), to_attr='details'))

        total = Budget.objects.filter(budget_distributor=_distributor, budget_status__in=['OPEN', 'CLOSED', 'DRAFT', 'IN APPROVAL'], budget_area__in=AreaUser.objects.filter(user_id=request.user.user_id).values_list('area_id', flat=True),
                                      budget_year=_from_yr, budget_month='{:02d}'.format(int(_from_mo))).exclude(budget_status='DRAFT', budget_new=True).aggregate(
            begin_bal=Sum('budgetdetail__budget_amount'),
            proposed=Sum('budgetdetail__budget_total') + Sum(
                'budgetdetail__budget_remaining') - Sum('budgetdetail__budget_balance'),
            remaining=Sum('budgetdetail__budget_remaining'),
            balance=Sum('budgetdetail__budget_balance'))

        draft_total = Budget.objects.filter(budget_status__in=['OPEN', 'CLOSED'], budget_area__in=AreaUser.objects.filter(user_id=request.user.user_id).values_list('area_id', flat=True),
                                            budget_year=_from_yr, budget_month='{:02d}'.format(int(_from_mo))).aggregate(
            upping=Sum('budgetdetail__budget_upping'))

    if _from_yr != '0' and _from_mo != '0' and budgets:
        curr_bal = total.get('begin_bal') + draft_total.get(
            'upping') if draft_total.get('upping') else total.get('begin_bal')
        total_bal = curr_bal - total.get('proposed') + total.get('remaining')

    context = {
        'budgets': budgets,
        'total': total,
        'draft_total': draft_total,
        'curr_bal': curr_bal,
        'total_bal': total_bal,
        'scrollX': scrollX,
        'from_year': _from_yr,
        'from_month': _from_mo,
        'to_year': _to_yr,
        'to_month': _to_mo,
        'selected_distributor': _distributor,
        'years': years,
        'distributors': distributors,
        'months': months,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'report_budget_monthly',
        'group_segment': 'report',
        'crud': 'index',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='REPORT') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/report_monthly_budget.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='REPORT')
def report_monthly_budget_toxl(request, _from_yr, _from_mo, _to_yr, _to_mo, _distributor):
    if _distributor == 'all':
        budgets = Budget.objects.filter(budget_status__in=['OPEN', 'CLOSED', 'DRAFT', 'IN APPROVAL'], budget_area__in=AreaUser.objects.filter(user_id=request.user.user_id).values_list('area_id', flat=True),
                                        budget_year=_from_yr, budget_month='{:02d}'.format(int(_from_mo))).exclude(budget_status='DRAFT', budget_new=True).annotate(
            proposed=F('budget_total') +
            Sum('budgetdetail__budget_remaining') - F('budget_balance'),
            remaining=Sum('budgetdetail__budget_remaining'),
        ).prefetch_related(Prefetch('budgetdetail_set', BudgetDetail.objects.all().annotate(
            transfer=F('budget_transfer_plus') -
            F('budget_transfer_minus'),
            beginning_mo=F('budget_transfer_plus') -
            F('budget_transfer_minus') + F('budget_total'),
        ), to_attr='details'))
    else:
        budgets = Budget.objects.filter(budget_distributor=_distributor, budget_status__in=['OPEN', 'CLOSED', 'DRAFT', 'IN APPROVAL'], budget_area__in=AreaUser.objects.filter(user_id=request.user.user_id).values_list('area_id', flat=True),
                                        budget_year=_from_yr, budget_month='{:02d}'.format(int(_from_mo))).exclude(budget_status='DRAFT', budget_new=True).annotate(
            proposed=F('budget_total') +
            Sum('budgetdetail__budget_remaining') - F('budget_balance'),
            remaining=Sum('budgetdetail__budget_remaining'),
        ).prefetch_related(Prefetch('budgetdetail_set', BudgetDetail.objects.all().annotate(
            transfer=F('budget_transfer_plus') -
            F('budget_transfer_minus'),
            beginning_mo=F('budget_transfer_plus') -
            F('budget_transfer_minus') + F('budget_total'),
        ), to_attr='details'))

    # Create a HttpResponse object with the csv data
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    filename = 'monthly_budget_' + \
        _from_mo + '_' + _from_yr + '_distributor_' + _distributor + '.xlsx'
    response['Content-Disposition'] = 'attachment; filename=' + filename

    # Create an XlsxWriter workbook object and add a worksheet.
    workbook = xlsxwriter.Workbook(response, {'in_memory': True})
    worksheet = workbook.add_worksheet()

    # Define column headers
    headers = ['Year', 'Mo', 'Area', 'Distributor', 'Ch', '%', 'Begin Bal',
               'Upping Price', 'Transfer', 'Currennt Bal', 'Proposed', 'Remaining', 'Available Bal']

    # Define cell formats
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#7eaa55',
        'font_color': 'white',
        'border': 1,
        'align': 'center',
    })
    cell_format = workbook.add_format({'border': 1})
    num_format = workbook.add_format({'border': 1, 'num_format': '#,##0'})
    percent_format = workbook.add_format(
        {'border': 1, 'num_format': '#,##0%'})
    total_format = workbook.add_format(
        {'bold': True, 'border': 1})
    total_percent_format = workbook.add_format(
        {'bold': True, 'border': 1, 'num_format': '#,##0%'})
    total_num_format = workbook.add_format(
        {'bold': True, 'border': 1, 'num_format': '#,##0'})

    # Set column width
    worksheet.set_column('A:A', 5)
    worksheet.set_column('B:B', 3)
    worksheet.set_column('C:C', 9)
    worksheet.set_column('D:D', 32)
    worksheet.set_column('E:F', 5)
    worksheet.set_column('G:M', 14)

    worksheet.freeze_panes(1, 6)

    # Write column headers
    for col_idx, col_value in enumerate(headers):
        worksheet.write(0, col_idx, col_value, header_format)

    idx = 0

    # Convert budgets queryset to DataFrame
    df = pd.DataFrame(list(budgets.values('budget_id', 'budget_year', 'budget_month', 'budget_area_id', 'budget_distributor__distributor_name', 'budgetdetail__budget_channel_id', 'budgetdetail__budget_percent', 'budget_status',
                      'budgetdetail__budget_amount', 'budgetdetail__budget_upping', 'budgetdetail__budget_proposed', 'budgetdetail__budget_remaining', 'budgetdetail__budget_balance').annotate(transfer=F('budgetdetail__budget_transfer_plus') - F('budgetdetail__budget_transfer_minus'), beginning_mo=F('budgetdetail__budget_transfer_plus') - F('budgetdetail__budget_transfer_minus') + F('budgetdetail__budget_total'))))

    # Create a pivot table
    pivot_table = pd.pivot_table(df, index=['budget_id', 'budget_year', 'budget_month', 'budget_area_id', 'budget_distributor__distributor_name', 'budgetdetail__budget_channel_id', 'budgetdetail__budget_percent', 'budget_status'],
                                 values=['budgetdetail__budget_amount', 'budgetdetail__budget_upping', 'transfer', 'beginning_mo',
                                         'budgetdetail__budget_proposed', 'budgetdetail__budget_remaining', 'budgetdetail__budget_balance'],
                                 aggfunc='sum')

    _id = ''
    _distributor = ''
    total = 0
    header = 1
    start = 2
    end = 0

    # Write pivot table to XlsxWriter Object
    for idx, record in enumerate(pivot_table.iterrows()):
        if _id == record[1].name[0]:
            worksheet.write(idx + header + total, 0, '', cell_format)
            worksheet.write(idx + header + total, 1, '', cell_format)
            worksheet.write(idx + header + total, 2, '', cell_format)
            worksheet.write(idx + header + total, 3, '', cell_format)
            worksheet.write(idx + header + total, 4,
                            record[1].name[5], cell_format)
            worksheet.write(idx + header + total, 5,
                            record[1].name[6] / 100, percent_format)
            worksheet.write(
                idx + header + total, 6, record[1].budgetdetail__budget_amount, num_format)
            if record[1].name[7] == 'DRAFT' or record[1].name[7] == 'IN APPROVAL':
                worksheet.write(idx + header + total, 7, 0, num_format)
            else:
                worksheet.write(
                    idx + header + total, 7, record[1].budgetdetail__budget_upping, num_format)
            worksheet.write(idx + header + total, 8,
                            record[1].transfer, num_format)
            if record[1].name[7] == 'DRAFT' or record[1].name[7] == 'IN APPROVAL':
                worksheet.write(
                    idx + header + total, 9, record[1].budgetdetail__budget_amount + record[1].transfer, num_format)
            else:
                worksheet.write(idx + header + total, 9,
                                record[1].beginning_mo, num_format)
            worksheet.write(
                idx + header + total, 10, record[1].budgetdetail__budget_proposed, num_format)
            worksheet.write(
                idx + header + total, 11, record[1].budgetdetail__budget_remaining, num_format)
            if record[1].name[7] == 'DRAFT' or record[1].name[7] == 'IN APPROVAL':
                worksheet.write(idx + header + total, 12, record[1].budgetdetail__budget_amount + record[1].transfer -
                                record[1].budgetdetail__budget_proposed + record[1].budgetdetail__budget_remaining, num_format)
            else:
                worksheet.write(
                    idx + header + total, 12, record[1].budgetdetail__budget_balance, num_format)
        else:
            # Add Subtotal
            if idx > 0:
                end = idx + total + 1

                worksheet.write(idx + header + total, 0, '', cell_format)
                worksheet.write(idx + header + total, 1, '', cell_format)
                worksheet.write(idx + header + total, 2, 'TOTAL', total_format)
                worksheet.write(idx + header + total, 3,
                                _distributor, total_format)
                worksheet.write(idx + header + total, 4, '', cell_format)
                worksheet.write(idx + header + total, 5,
                                1, total_percent_format)
                worksheet.write_formula(
                    idx + header + total, 6, f'=SUBTOTAL(9, G{start}:G{end})', total_num_format)
                worksheet.write_formula(
                    idx + header + total, 7, f'=SUBTOTAL(9, H{start}:H{end})', total_num_format)
                worksheet.write_formula(
                    idx + header + total, 8, f'=SUBTOTAL(9, I{start}:I{end})', total_num_format)
                worksheet.write_formula(
                    idx + header + total, 9, f'=SUBTOTAL(9, J{start}:J{end})', total_num_format)
                worksheet.write_formula(
                    idx + header + total, 10, f'=SUBTOTAL(9, K{start}:K{end})', total_num_format)
                worksheet.write_formula(
                    idx + header + total, 11, f'=SUBTOTAL(9, L{start}:L{end})', total_num_format)
                worksheet.write_formula(
                    idx + header + total, 12, f'=SUBTOTAL(9, M{start}:M{end})', total_num_format)

                total += 1
                start = idx + total + header + 1

            worksheet.write(idx + header + total, 0,
                            record[1].name[1], cell_format)
            worksheet.write(idx + header + total, 1,
                            record[1].name[2], cell_format)
            worksheet.write(idx + header + total, 2,
                            record[1].name[3], cell_format)
            worksheet.write(idx + header + total, 3,
                            record[1].name[4], cell_format)
            worksheet.write(idx + header + total, 4,
                            record[1].name[5], cell_format)
            worksheet.write(
                idx + header + total, 5, record[1].name[6] / 100, percent_format)
            worksheet.write(
                idx + header + total, 6, record[1].budgetdetail__budget_amount, num_format)
            if record[1].name[7] == 'DRAFT' or record[1].name[7] == 'IN APPROVAL':
                worksheet.write(idx + header + total, 7, 0, num_format)
            else:
                worksheet.write(
                    idx + header + total, 7, record[1].budgetdetail__budget_upping, num_format)
            worksheet.write(idx + header + total, 8,
                            record[1].transfer, num_format)
            if record[1].name[7] == 'DRAFT' or record[1].name[7] == 'IN APPROVAL':
                worksheet.write(
                    idx + header + total, 9, record[1].budgetdetail__budget_amount + record[1].transfer, num_format)
            else:
                worksheet.write(
                    idx + header + total, 9, record[1].beginning_mo, num_format)
            worksheet.write(
                idx + header + total, 10, record[1].budgetdetail__budget_proposed, num_format)
            worksheet.write(
                idx + header + total, 11, record[1].budgetdetail__budget_remaining, num_format)
            if record[1].name[7] == 'DRAFT' or record[1].name[7] == 'IN APPROVAL':
                worksheet.write(idx + header + total, 12, record[1].budgetdetail__budget_amount + record[1].transfer -
                                record[1].budgetdetail__budget_proposed + record[1].budgetdetail__budget_remaining, num_format)
            else:
                worksheet.write(
                    idx + header + total, 12, record[1].budgetdetail__budget_balance, num_format)

        _id = record[1].name[0]
        _distributor = record[1].name[4]

    total += 1
    end = idx + total + 1

    worksheet.write(idx + header + total, 0, '', cell_format)
    worksheet.write(idx + header + total, 1, '', cell_format)
    worksheet.write(idx + header + total, 2, 'TOTAL', total_format)
    worksheet.write(idx + header + total, 3, _distributor, total_format)
    worksheet.write(idx + header + total, 4, '', cell_format)
    worksheet.write(idx + header + total, 5, 1, total_percent_format)
    worksheet.write_formula(
        idx + header + total, 6, f'=SUBTOTAL(9, G{start}:G{end})', total_num_format)
    worksheet.write_formula(idx + header + total, 7,
                            f'=SUBTOTAL(9, H{start}:H{end})', total_num_format)
    worksheet.write_formula(idx + header + total, 8,
                            f'=SUBTOTAL(9, I{start}:I{end})', total_num_format)
    worksheet.write_formula(idx + header + total, 9,
                            f'=SUBTOTAL(9, J{start}:J{end})', total_num_format)
    worksheet.write_formula(idx + header + total, 10,
                            f'=SUBTOTAL(9, K{start}:K{end})', total_num_format)
    worksheet.write_formula(idx + header + total, 11,
                            f'=SUBTOTAL(9, L{start}:L{end})', total_num_format)
    worksheet.write_formula(idx + header + total, 12,
                            f'=SUBTOTAL(9, M{start}:M{end})', total_num_format)

    total += 1
    start = idx + total + header + 1

    worksheet.write(idx + header + total, 0, '', cell_format)
    worksheet.write(idx + header + total, 1, '', cell_format)
    worksheet.write(idx + header + total, 2, '', cell_format)
    worksheet.write(idx + header + total, 3, 'GRAND TOTAL', total_format)
    worksheet.write(idx + header + total, 4, '', cell_format)
    worksheet.write(idx + header + total, 5, '', cell_format)
    worksheet.write_formula(
        idx + header + total, 6, f'=SUBTOTAL(9, G2:G{end})', total_num_format)
    worksheet.write_formula(idx + header + total, 7,
                            f'=SUBTOTAL(9, H2:H{end})', total_num_format)
    worksheet.write_formula(idx + header + total, 8,
                            f'=SUBTOTAL(9, I2:I{end})', total_num_format)
    worksheet.write_formula(idx + header + total, 9,
                            f'=SUBTOTAL(9, J2:J{end})', total_num_format)
    worksheet.write_formula(idx + header + total, 10,
                            f'=SUBTOTAL(9, K2:K{end})', total_num_format)
    worksheet.write_formula(idx + header + total, 11,
                            f'=SUBTOTAL(9, L2:L{end})', total_num_format)
    worksheet.write_formula(idx + header + total, 12,
                            f'=SUBTOTAL(9, M2:M{end})', total_num_format)

    # Close the workbook before sending the data.
    workbook.close()

    return response


@login_required(login_url='/login/')
@role_required(allowed_roles='REPORT')
def report_budget_summary(request, _from_yr, _from_mo, _to_yr, _to_mo, _distributor):
    years = [str(year) for year in Budget.objects.filter(budget_status__in=[
        'OPEN', 'CLOSED', 'DRAFT', 'IN APPROVAL']).exclude(budget_status='DRAFT', budget_new=True).values_list('budget_year', flat=True).distinct()]
    distributors = Distributor.objects.all()
    months = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']

    context = {
        'from_year': _from_yr,
        'from_month': _from_mo,
        'to_year': _to_yr,
        'to_month': _to_mo,
        'selected_distributor': _distributor,
        'years': years,
        'distributors': distributors,
        'months': months,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'report_budget_summary',
        'group_segment': 'report',
        'crud': 'index',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='REPORT') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/report_budget_summary.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='REPORT')
def report_budget_summary_toxl(request, _from_yr, _from_mo, _to_yr, _to_mo, _distributor):
    from_date = datetime.date(int(_from_yr), int(
        _from_mo), 1) if _from_yr != '0' and _from_mo != '0' else datetime.date.today().replace(day=1)
    _to_date = datetime.date(int(_to_yr), int(
        _to_mo), 15) + datetime.timedelta(days=30)
    to_date = datetime.date(_to_date.year, _to_date.month,
                            1) if _to_yr != '0' and _to_mo != '0' else datetime.date.today().replace(day=1)

    if _distributor == 'all':
        with connection.cursor() as cursor:

            # Spending = Budget Amount + Upping - Claim Amount <- Rumus Spending
            # cursor.execute(
            #     """
            #     SELECT budget_area_id, apps_budget.budget_id, distributor_name, region_name, (budget_amount + budget_upping - IFNULL(claim.claim_amount, 0)) as balance,
            #     DATE(CONCAT(budget_year, '-', budget_month, '-01')) as budget_date
            #     FROM apps_budget
            #     LEFT JOIN (SELECT SUM(proposal_claim) as claim_amount, budget_id FROM apps_proposal GROUP BY budget_id) as claim ON apps_budget.budget_id = claim.budget_id
            #     INNER JOIN apps_distributor ON budget_distributor_id = distributor_id
            #     INNER JOIN apps_regiondetail ON budget_area_id = area_id
            #     INNER JOIN apps_region ON apps_region.region_id = apps_regiondetail.region_id
            #     WHERE budget_status IN ('OPEN', 'CLOSED') AND budget_area_id IN (
            #         SELECT area_id FROM apps_areauser WHERE user_id = %s
            #     ) AND DATE(CONCAT(budget_year, '-', budget_month, '-01')) >= %s AND DATE(CONCAT(budget_year, '-', budget_month, '-01')) < %s
            #     """, [request.user.user_id, from_date, to_date]
            # )

            # Spending = Budget Amount + Upping - Proposal <- Rumus Spending
            cursor.execute(
                """
                SELECT budget_area_id, apps_budget.budget_id, distributor_name, region_name, IF(budget_status = 'DRAFT' OR budget_status = 'IN APPROVAL', (budget_amount + IFNULL(detail.remaining_amount, 0) - IFNULL(detail.proposed_amount, 0)), (budget_amount + budget_upping + IFNULL(detail.remaining_amount, 0) - IFNULL(detail.proposed_amount, 0))) as balance, 
                DATE(CONCAT(budget_year, '-', budget_month, '-01')) as budget_date 
                FROM apps_budget 
                LEFT JOIN (SELECT SUM(budget_proposed) as proposed_amount, SUM(budget_remaining) as remaining_amount, budget_id FROM apps_budgetdetail GROUP BY budget_id) as detail ON apps_budget.budget_id = detail.budget_id 
                INNER JOIN apps_distributor ON budget_distributor_id = distributor_id
                INNER JOIN apps_regiondetail ON budget_area_id = area_id 
                INNER JOIN apps_region ON apps_region.region_id = apps_regiondetail.region_id
                WHERE budget_status IN ('OPEN', 'CLOSED', 'DRAFT', 'IN APPROVAL') AND NOT (budget_status = 'DRAFT' AND budget_new = True) AND budget_area_id IN (
                    SELECT area_id FROM apps_areauser WHERE user_id = %s
                ) AND DATE(CONCAT(budget_year, '-', budget_month, '-01')) >= %s AND DATE(CONCAT(budget_year, '-', budget_month, '-01')) < %s
                """, [request.user.user_id, from_date, to_date]
            )
            budget_region = cursor.fetchall()
    else:
        with connection.cursor() as cursor:

            # Spending = Budget Amount + Upping - Claim Amount <- Rumus Spending
            # cursor.execute(
            #     """
            #     SELECT budget_area_id, budget_id, distributor_name, region_name, (budget_amount + budget_upping - IFNULL(claim.claim_amount, 0)) as balance,
            #     DATE(CONCAT(budget_year, '-', budget_month, '-01')) as budget_date
            #     FROM apps_budget
            #     LEFT JOIN (SELECT SUM(proposal_claim) as claim_amount, budget_id FROM apps_proposal GROUP BY budget_id) as claim ON apps_budget.budget_id = claim.budget_id
            #     INNER JOIN apps_distributor ON budget_distributor_id = distributor_id
            #     INNER JOIN apps_regiondetail ON budget_area_id = area_id
            #     INNER JOIN apps_region ON apps_region.region_id = apps_regiondetail.region_id
            #     WHERE budget_status IN ('OPEN', 'CLOSED') AND budget_area_id IN (
            #         SELECT area_id FROM apps_areauser WHERE user_id = %s
            #     ) AND DATE(CONCAT(budget_year, '-', budget_month, '-01')) >= %s AND DATE(CONCAT(budget_year, '-', budget_month, '-01')) < %s AND budget_distributor_id = %s
            #     """, [request.user.user_id, from_date, to_date, _distributor]
            # )

            # Spending = Budget Amount + Upping - Proposal <- Rumus Spending
            cursor.execute(
                """
                SELECT budget_area_id, apps_budget.budget_id, distributor_name, region_name, IF(budget_status = 'DRAFT' or budget_status = 'IN APPROVAL', (budget_amount + IFNULL(detail.remaining_amount, 0) - IFNULL(detail.proposed_amount, 0)), (budget_amount + budget_upping + IFNULL(detail.remaining_amount, 0) - IFNULL(detail.proposed_amount, 0))) as balance, 
                DATE(CONCAT(budget_year, '-', budget_month, '-01')) as budget_date
                FROM apps_budget
                LEFT JOIN (SELECT SUM(budget_proposed) as proposed_amount, SUM(budget_remaining) as remaining_amount, budget_id FROM apps_budgetdetail GROUP BY budget_id) as detail ON apps_budget.budget_id = detail.budget_id 
                INNER JOIN apps_distributor ON budget_distributor_id = distributor_id
                INNER JOIN apps_regiondetail ON budget_area_id = area_id
                INNER JOIN apps_region ON apps_region.region_id = apps_regiondetail.region_id
                WHERE budget_status IN ('OPEN', 'CLOSED', 'DRAFT', 'IN APPROVAL') AND NOT (budget_status = 'DRAFT' AND budget_new = True) AND budget_area_id IN (
                    SELECT area_id FROM apps_areauser WHERE user_id = %s
                ) AND DATE(CONCAT(budget_year, '-', budget_month, '-01')) >= %s AND DATE(CONCAT(budget_year, '-', budget_month, '-01')) < %s AND budget_distributor_id = %s
                """, [request.user.user_id, from_date, to_date, _distributor]
            )
            budget_region = cursor.fetchall()

    if not budget_region:
        return render(request, 'home/report_budget_summary.html', {'error': 'No region data available'})

    # Convert budgets queryset to DataFrame
    df = pd.DataFrame(budget_region, columns=[
        'budget_area', 'budget_id', 'budget_distributor__distributor_name', 'region_name', 'balance', 'budget_date'])

    # Create a pivot table
    pivot_table = pd.pivot_table(df, index=['budget_area', 'budget_distributor__distributor_name'],
                                 values=['balance'], columns=['budget_date'],
                                 aggfunc='sum', fill_value=0)

    pivot_region = pd.pivot_table(df, index=['region_name'], values=[
                                  'balance'], columns=['budget_date'], aggfunc='sum', fill_value=0)
    print(pivot_region)

    # Create a HttpResponse object with the csv data
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    filename = 'budget_summary_' + \
        _from_mo + '_' + _from_yr + '_to_' + _to_mo + '_' + \
        _to_yr + '_distributor_' + _distributor + '.xlsx'
    response['Content-Disposition'] = 'attachment; filename=' + filename

    # Create an XlsxWriter workbook object and add a worksheet.
    workbook = xlsxwriter.Workbook(response, {'in_memory': True})
    worksheet = workbook.add_worksheet()

    # Define column headers
    headers = ['Area', 'Distributor']
    headers.extend(
        [f'{pd.to_datetime(date).strftime("%b-%Y")}' for date in pivot_table.columns.levels[1]])

    # Define cell formats
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#7eaa55',
        'font_color': 'white',
        'border': 1,
        'align': 'center',
    })
    cell_format = workbook.add_format({'border': 1, 'num_format': '#,##0'})
    bold_format = workbook.add_format({'bold': True})
    total_format = workbook.add_format({'bold': True, 'border': 1})
    total_num_format = workbook.add_format(
        {'bold': True, 'border': 1, 'num_format': '#,##0'})

    # Set column width
    worksheet.set_column('A:A', 9)
    worksheet.set_column('B:B', 32)
    worksheet.set_column('C:Z', 14)

    worksheet.freeze_panes(4, 2)

    worksheet.write(0, 0, 'PT ABC President Indonesia', bold_format)
    worksheet.write(1, 0, 'Selmar Budget Summary Report')

    gap = 3
    foot = 0

    # Write column headers
    for col_idx, col_value in enumerate(headers):
        worksheet.write(0 + gap, col_idx, col_value, header_format)

    # Initialize variables for subtotals
    subtotal_start_row = gap + 1
    current_area = None

    # Write pivot table to XlsxWriter Object
    for idx, record in enumerate(pivot_table.iterrows()):
        # Check if area has changed (i.e., we've moved to a new area)
        if current_area != record[0][0]:
            # If this is not the first area, write the subtotal for the previous area
            if current_area is not None:
                worksheet.merge_range(
                    idx + gap + 1, 0, idx + gap + 1, 1, 'Subtotal for ' + current_area, total_format)
                for col_idx, col_value in enumerate(pivot_table.columns.levels[1]):
                    worksheet.write_formula(idx + gap + 1, col_idx + 2,
                                            f'=SUBTOTAL(9, {xlsxwriter.utility.xl_rowcol_to_cell(subtotal_start_row, col_idx + 2)}:{xlsxwriter.utility.xl_rowcol_to_cell(idx + gap, col_idx + 2)})', total_num_format)
                gap += 1  # Increase gap to account for the new subtotal row

            # Update current area and reset start row for subtotals
            current_area = record[0][0]
            subtotal_start_row = idx + gap + 1

        # Write the record
        worksheet.write(idx + 1 + gap, 0, record[0][0], cell_format)
        worksheet.write(idx + 1 + gap, 1, record[0][1], cell_format)
        for col_idx, col_value in enumerate(record[1]):
            worksheet.write(idx + 1 + gap, col_idx + 2, col_value, cell_format)

    foot = len(pivot_table) + gap + 1
    # Write the subtotal for the last area
    worksheet.merge_range(foot, 0, foot, 1,
                          'Subtotal for ' + current_area, total_format)
    for col_idx, col_value in enumerate(pivot_table.columns.levels[1]):
        worksheet.write_formula(foot, col_idx + 2,
                                f'=SUBTOTAL(9, {xlsxwriter.utility.xl_rowcol_to_cell(subtotal_start_row, col_idx + 2)}:{xlsxwriter.utility.xl_rowcol_to_cell(idx + gap + 1, col_idx + 2)})', total_num_format)

    foot += 1
    # Write Grand Total
    worksheet.merge_range(foot, 0, foot, 1, 'Grand Total', total_format)
    for col_idx, col_value in enumerate(pivot_table.sum()):
        worksheet.write(foot, col_idx + 2, col_value, total_num_format)

    # Write Total by Region
    foot += 2
    if pivot_region.empty:
        worksheet.merge_range(
            foot, 0, foot, 1, 'Region data not found', total_format)
    else:
        for idx, record in enumerate(pivot_region.iterrows()):
            worksheet.merge_range(idx + foot, 0, idx + foot,
                                  1, record[0], cell_format)
            for col_idx, col_value in enumerate(record[1]):
                worksheet.write(idx + foot, col_idx + 2,
                                col_value, cell_format)

    # Write Grand Total by Region
    foot += len(pivot_region)
    worksheet.merge_range(foot, 0, foot, 1, 'Grand Total', total_format)
    for col_idx, col_value in enumerate(pivot_region.sum()):
        worksheet.write(foot, col_idx + 2, col_value, total_num_format)

    # Close the workbook before sending the data.
    workbook.close()
    return response


@login_required(login_url='/login/')
@role_required(allowed_roles='REPORT')
def report_budget_detail(request, _from_yr, _from_mo, _to_yr, _to_mo, _distributor):
    years = [str(year) for year in Budget.objects.filter(budget_status__in=[
        'OPEN', 'CLOSED', 'DRAFT', 'IN APPROVAL']).exclude(budget_status='DRAFT', budget_new=True).values_list('budget_year', flat=True).distinct()]
    distributors = Distributor.objects.all()
    months = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']

    context = {
        'from_year': _from_yr,
        'from_month': _from_mo,
        'to_year': _to_yr,
        'to_month': _to_mo,
        'selected_distributor': _distributor,
        'years': years,
        'distributors': distributors,
        'months': months,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'report_budget_detail',
        'group_segment': 'report',
        'crud': 'index',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='REPORT') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/report_budget_detail.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='REPORT')
def report_budget_detail_toxl(request, _from_yr, _from_mo, _to_yr, _to_mo, _distributor):
    from_date = datetime.date(int(_from_yr), int(
        _from_mo), 1) if _from_yr != '0' and _from_mo != '0' else datetime.date.today().replace(day=1)
    _to_date = datetime.date(int(_to_yr), int(
        _to_mo), 15) + datetime.timedelta(days=30)
    to_date = datetime.date(_to_date.year, _to_date.month,
                            1) if _to_yr != '0' and _to_mo != '0' else datetime.date.today().replace(day=1)

    if _distributor == 'all':
        with connection.cursor() as cursor:

            # Spending = Budget Amount + Upping - Claim Amount <- Rumus Spending
            # cursor.execute(
            #     """
            #     SELECT apps_budget.budget_id, distributor_name, region_name, budget_area_id, budget_amount AS 1_opening, budget_upping AS 2_upping, IFNULL(claim.claim_amount, 0) AS 3_claim, (budget_amount + budget_upping - IFNULL(claim.claim_amount, 0)) AS 4_balance,
            #     DATE(CONCAT(budget_year, '-', budget_month, '-01')) as budget_date
            #     FROM apps_budget
            #     LEFT JOIN (SELECT SUM(proposal_claim) as claim_amount, budget_id FROM apps_proposal GROUP BY budget_id) as claim ON apps_budget.budget_id = claim.budget_id
            #     INNER JOIN apps_distributor ON budget_distributor_id = distributor_id
            #     INNER JOIN apps_regiondetail ON budget_area_id = area_id
            #     INNER JOIN apps_region ON apps_region.region_id = apps_regiondetail.region_id
            #     WHERE budget_status IN ('OPEN', 'CLOSED') AND budget_area_id IN (
            #         SELECT area_id FROM apps_areauser WHERE user_id = %s
            #     ) AND DATE(CONCAT(budget_year, '-', budget_month, '-01')) >= %s AND DATE(CONCAT(budget_year, '-', budget_month, '-01')) < %s
            #     """, [request.user.user_id, from_date, to_date]
            # )

            # Spending = Budget Amount + Upping - Proposal <- Rumus Spending
            cursor.execute(
                """
                SELECT apps_budget.budget_id, distributor_name, region_name, budget_area_id, budget_amount AS 1_opening, IF(budget_status = 'DRAFT' OR budget_status = 'IN APPROVAL', 0, budget_upping) AS 2_upping, IFNULL(detail.proposed_amount, 0) AS 3_proposed, IF(budget_status = 'DRAFT' OR budget_status = 'IN APPROVAL', (budget_amount + IFNULL(detail.remaining_amount, 0) - IFNULL(detail.proposed_amount, 0)), (budget_amount + budget_upping + IFNULL(detail.remaining_amount, 0) - IFNULL(detail.proposed_amount, 0))) AS 4_balance, 
                DATE(CONCAT(budget_year, '-', budget_month, '-01')) as budget_date
                FROM apps_budget 
                LEFT JOIN (SELECT SUM(budget_proposed) as proposed_amount, SUM(budget_remaining) as remaining_amount, budget_id FROM apps_budgetdetail GROUP BY budget_id) as detail ON apps_budget.budget_id = detail.budget_id 
                INNER JOIN apps_distributor ON budget_distributor_id = distributor_id
                INNER JOIN apps_regiondetail ON budget_area_id = area_id
                INNER JOIN apps_region ON apps_region.region_id = apps_regiondetail.region_id
                WHERE budget_status IN ('OPEN', 'CLOSED', 'DRAFT', 'IN APPROVAL') AND NOT (budget_status = 'DRAFT' AND budget_new = True) AND budget_area_id IN (
                    SELECT area_id FROM apps_areauser WHERE user_id = %s
                ) AND DATE(CONCAT(budget_year, '-', budget_month, '-01')) >= %s AND DATE(CONCAT(budget_year, '-', budget_month, '-01')) < %s
                """, [request.user.user_id, from_date, to_date]
            )
            budget_detail = cursor.fetchall()
    else:
        with connection.cursor() as cursor:

            # Spending = Budget Amount + Upping - Claim Amount <- Rumus Spending
            # cursor.execute(
            #     """
            #     SELECT apps_budget.budget_id, distributor_name, region_name, budget_area_id, budget_amount AS 1_opening, budget_upping AS 2_upping, IFNULL(claim.claim_amount, 0) AS 3_claim, (budget_amount + budget_upping - IFNULL(claim.claim_amount, 0)) AS 4_balance,
            #     DATE(CONCAT(budget_year, '-', budget_month, '-01')) as budget_date
            #     FROM apps_budget
            #     LEFT JOIN (SELECT SUM(proposal_claim) as claim_amount, budget_id FROM apps_proposal GROUP BY budget_id) as claim ON apps_budget.budget_id = claim.budget_id
            #     INNER JOIN apps_distributor ON budget_distributor_id = distributor_id
            #     INNER JOIN apps_regiondetail ON budget_area_id = area_id
            #     INNER JOIN apps_region ON apps_region.region_id = apps_regiondetail.region_id
            #     WHERE budget_status IN ('OPEN', 'CLOSED') AND budget_area_id IN (
            #         SELECT area_id FROM apps_areauser WHERE user_id = %s
            #     ) AND DATE(CONCAT(budget_year, '-', budget_month, '-01')) >= %s AND DATE(CONCAT(budget_year, '-', budget_month, '-01')) < %s AND budget_distributor_id = %s
            #     """, [request.user.user_id, from_date, to_date, _distributor]
            # )

            # Spending = Budget Amount + Upping - Proposal <- Rumus Spending
            cursor.execute(
                """
                SELECT apps_budget.budget_id, distributor_name, region_name, budget_area_id, budget_amount AS 1_opening, IF(budget_status = 'DRAFT' OR budget_status = 'IN APPROVAL', 0, budget_upping) AS 2_upping, IFNULL(detail.proposed_amount, 0) AS 3_proposed, IF(budget_status = 'DRAFT' OR budget_status = 'IN APPROVAL', (budget_amount + IFNULL(detail.remaining_amount, 0) - IFNULL(detail.proposed_amount, 0)), (budget_amount + budget_upping + IFNULL(detail.remaining_amount, 0) - IFNULL(detail.proposed_amount, 0))) AS 4_balance, 
                DATE(CONCAT(budget_year, '-', budget_month, '-01')) as budget_date
                FROM apps_budget
                LEFT JOIN (SELECT SUM(budget_proposed) as proposed_amount, SUM(budget_remaining) as remaining_amount, budget_id FROM apps_budgetdetail GROUP BY budget_id) as detail ON apps_budget.budget_id = detail.budget_id
                INNER JOIN apps_distributor ON budget_distributor_id = distributor_id
                INNER JOIN apps_regiondetail ON budget_area_id = area_id
                INNER JOIN apps_region ON apps_region.region_id = apps_regiondetail.region_id
                WHERE budget_status IN ('OPEN', 'CLOSED', 'DRAFT', 'IN APPROVAL') AND NOT (budget_status = 'DRAFT' AND budget_new = True) AND budget_area_id IN (
                    SELECT area_id FROM apps_areauser WHERE user_id = %s
                ) AND DATE(CONCAT(budget_year, '-', budget_month, '-01')) >= %s AND DATE(CONCAT(budget_year, '-', budget_month, '-01')) < %s AND budget_distributor_id = %s
                """, [request.user.user_id, from_date, to_date, _distributor]
            )
            budget_detail = cursor.fetchall()

    if not budget_detail:
        return render(request, 'home/report_budget_detail.html', {'error': 'No region data available'})

    # Convert budgets queryset to DataFrame
    df = pd.DataFrame(budget_detail, columns=[
        'budget_id', 'distributor_name', 'region_name', 'budget_area_id', '1_opening', '2_upping', '3_proposed', '4_balance', 'budget_date'])

    # Create a pivot table
    pivot_table = (pd.pivot_table(df,
                                  index=['budget_date'],
                                  columns=['distributor_name', 'region_name'],
                                  values=['1_opening', '2_upping',
                                          '3_proposed', '4_balance'],
                                  aggfunc='sum', fill_value=0)).T.swaplevel(1, 0).swaplevel(2, 1).sort_index(level=0)

    pivot_total = (pd.pivot_table(df,
                                  index=['budget_date'],
                                  values=['1_opening', '2_upping',
                                          '3_proposed', '4_balance'],
                                  aggfunc='sum', fill_value=0)).T

    pivot_region = pd.pivot_table(df,
                                  index=['region_name'],
                                  columns=['budget_date'],
                                  values=['4_balance'],
                                  aggfunc='sum', fill_value=0)

    # Create a HttpResponse object with the csv data
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    filename = 'budget_detail_' + \
        _from_mo + '_' + _from_yr + '_to_' + _to_mo + '_' + \
        _to_yr + '_distributor_' + _distributor + '.xlsx'
    response['Content-Disposition'] = 'attachment; filename=' + filename

    # Create an XlsxWriter workbook object and add a worksheet.
    workbook = xlsxwriter.Workbook(response, {'in_memory': True})
    worksheet = workbook.add_worksheet()

    # Define column headers
    headers = ['Distributor', 'Region', '']
    headers.extend(
        [f'{pd.to_datetime(date).strftime("%b-%Y")}' for date in pivot_table.columns])

    # Define cell formats
    header_format = workbook.add_format({
        'bold': True,
        'bg_color': '#7eaa55',
        'font_color': 'white',
        'border': 1,
        'align': 'center',
    })
    cell_format = workbook.add_format(
        {'border': 1, 'num_format': '_(* #,##0_);_(* (#,##0);_(* "-"_);_(@_)', 'valign': 'vcenter'})
    back_format = workbook.add_format(
        {'border': 1, 'num_format': '_(* #,##0_);_(* (#,##0);_(* "-"_);_(@_)', 'bg_color': '#e5eedc', 'valign': 'vcenter'})
    bold_format = workbook.add_format({'bold': True})
    total_format = workbook.add_format({'bold': True, 'border': 1})
    back_total_format = workbook.add_format(
        {'bold': True, 'border': 1, 'bg_color': '#e5eedc'})
    total_num_format = workbook.add_format(
        {'bold': True, 'border': 1, 'num_format': '_(* #,##0_);_(* (#,##0);_(* "-"_);_(@_)'})
    back_total_num_format = workbook.add_format(
        {'bold': True, 'border': 1, 'num_format': '_(* #,##0_);_(* (#,##0);_(* "-"_);_(@_)', 'bg_color': '#e5eedc'})

    # Set column width
    worksheet.set_column('A:A', 32)
    worksheet.set_column('B:B', 8)
    worksheet.set_column('C:C', 16)
    worksheet.set_column('D:Z', 14)

    worksheet.freeze_panes(5, 3)

    worksheet.write(0, 0, 'PT ABC President Indonesia', bold_format)
    worksheet.write(1, 0, 'Selmar Budget Report')
    worksheet.write(2, 0, from_date.strftime('%b %Y') if _from_yr !=
                    _to_yr else from_date.strftime('%b') + ' to ' + (to_date - timedelta(days=1)).strftime('%b %Y'))

    gap = 4
    foot = 0
    back = False

    # Write column headers
    for col_idx, col_value in enumerate(headers):
        worksheet.write(0 + gap, col_idx, col_value, header_format)

    # Write dataframes to XlsxWriter Object
    for idx, record in enumerate(pivot_table.iterrows()):
        if idx % 4 == 0:
            back = not back
            worksheet.merge_range(
                idx + 1 + gap, 0, idx + 4 + gap, 0, record[0][0], cell_format if not back else back_format)
            worksheet.merge_range(
                idx + 1 + gap, 1, idx + 4 + gap, 1, record[0][1], cell_format if not back else back_format)

        if record[0][2] == '1_opening':
            worksheet.write(idx + 1 + gap, 2, 'Opening Balance',
                            total_format if not back else back_total_format)
        elif record[0][2] == '2_upping':
            worksheet.write(idx + 1 + gap, 2, 'Upping Price',
                            cell_format if not back else back_format)
        elif record[0][2] == '3_proposed':
            worksheet.write(idx + 1 + gap, 2, 'Spending',
                            cell_format if not back else back_format)
        elif record[0][2] == '4_balance':
            worksheet.write(idx + 1 + gap, 2, 'Ending Balance',
                            total_format if not back else back_total_format)

        for col_idx, col_value in enumerate(record[1]):
            if record[0][2] == '1_opening' or record[0][2] == '4_balance':
                worksheet.write(idx + 1 + gap, col_idx + 3,
                                col_value, total_num_format if not back else back_total_num_format)
            else:
                worksheet.write(idx + 1 + gap, col_idx +
                                3, col_value, cell_format if not back else back_format)

            if record[0][2] == '3_proposed':
                worksheet.write(idx + 1 + gap, col_idx + 3,
                                col_value * -1, cell_format if not back else back_format)

    foot = len(pivot_table) + gap + 2
    # Write Grand Total
    for idx, record in enumerate(pivot_total.iterrows()):
        worksheet.write(foot + idx, 1, 'Total', total_format)
        if record[0] == '1_opening':
            worksheet.write(foot + idx, 2, 'Opening Balance', cell_format)
        elif record[0] == '2_upping':
            worksheet.write(foot + idx, 2, 'Upping Price', cell_format)
        elif record[0] == '3_proposed':
            worksheet.write(foot + idx, 2, 'Spending', cell_format)
        elif record[0] == '4_balance':
            worksheet.write(foot + idx, 2, 'Ending Balance', total_num_format)
        for col_idx, col_value in enumerate(record[1]):
            if record[0] == '4_balance':
                worksheet.write(foot + idx, col_idx + 3,
                                col_value, total_num_format)
            else:
                worksheet.write(foot + idx, col_idx + 3,
                                col_value, cell_format)

    foot += len(pivot_total) + 1
    # Write Total by Region
    for idx, record in enumerate(pivot_region.iterrows()):
        worksheet.write(foot + idx, 1, record[0], total_format)
        worksheet.write(foot + idx, 2, 'Ending Balance', cell_format)
        for col_idx, col_value in enumerate(record[1]):
            worksheet.write(foot + idx, col_idx + 3, col_value, cell_format)

    # Write Grand Total by Region
    foot += len(pivot_region)
    worksheet.write(foot, 1, 'Total', total_format)
    worksheet.write(foot, 2, 'Ending Balance', total_num_format)
    for idx, record in enumerate(pivot_region.sum()):
        worksheet.write(foot, idx + 3, record, total_num_format)

    # Close the workbook before sending the data.
    workbook.close()
    return response


@login_required(login_url='/login/')
@role_required(allowed_roles='MESSAGE')
def welcome_message(request):
    message = WelcomeMessage.objects.all().first()

    if request.method == 'POST':
        form = FormWelcomeMessage(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('welcome-message'))

    form = FormWelcomeMessage(instance=message)

    context = {
        'form': form,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'welcome-message',
        'group_segment': 'master',
        'crud': 'view',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='MESSAGE') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/welcome_message_view.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='MESSAGE')
def welcome_message_update(request):
    message = WelcomeMessage.objects.all().first()

    if request.method == 'POST':
        form = FormWelcomeMessageUpdate(request.POST, instance=message)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('welcome-message'))

    form = FormWelcomeMessageUpdate(instance=message)

    context = {
        'form': form,
        'budget_notif': budget_notification(request),
        'proposal_notif': proposal_notification(request),
        'program_notif': program_notification(request),
        'claim_notif': claim_notification(request),
        'cl_notif': cl_notification(request),
        'segment': 'welcome-message',
        'group_segment': 'master',
        'crud': 'update',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='MESSAGE') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/welcome_message_view.html', context)
