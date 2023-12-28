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
from django.db.models import Sum
from django.db.models import Max
from django.db.models import Min
from . import host
from reportlab.pdfgen import canvas
from django.http import FileResponse
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import landscape, A4
from django.db.models import Count
from PyPDF2 import PdfReader
from PyPDF2 import PdfFileMerger
from PyPDF2 import PdfMerger
import requests
import os
import requests
import requests
import base64
from django.conf import settings


@login_required(login_url='/login/')
def home(request):
    context = {
        'segment': 'index',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
    }
    return render(request, 'home/index.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='USER')
def user_index(request):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT user_id, username, email, position_name FROM apps_user INNER JOIN apps_position ON apps_user.position_id = apps_position.position_id")
        users = cursor.fetchall()

    context = {
        'data': users,
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
                my_file = user.signature
                filename = '../../www/selmar/apps/media/' + my_file.name
                with open(filename, 'wb+') as temp_file:
                    for chunk in my_file.chunks():
                        temp_file.write(chunk)

            return HttpResponseRedirect(reverse('user-view', args=[form.instance.user_id, ]))
        else:
            message = form.errors
            context = {
                'form': form,
                'position': position,
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
                my_file = users.signature
                filename = '../../www/selmar/apps/media/' + my_file.name
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
            "SELECT area_id, area_name, username FROM apps_areasales INNER JOIN apps_user ON apps_areasales.manager = apps_user.user_id")
        area_sales = cursor.fetchall()

    context = {
        'data': area_sales,
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
            form.save()
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
            budget_month=datetime.datetime.now().month,
            budget_year=datetime.datetime.now().year
        ).values_list('budget_distributor', flat=True)
    )
    month = '{:02d}'.format(int(request.POST.get('budget_month'))) if request.POST.get(
        'budget_month') else '{:02d}'.format(int(datetime.datetime.now().month))
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
        if period[0].month_open == str(datetime.datetime.now().month) and period[0].year_open == str(datetime.datetime.now().year):
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
        else:
            closing = 'False'

    form = FormBudget(
        initial={'budget_year': datetime.datetime.now().year, 'budget_month': month, 'budget_amount': 0, 'budget_upping': 0, 'budget_total': 0})

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
    pendings = Budget.objects.filter(budget_status='PENDING', budget_area__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-budget_year', '-budget_month').all
    pendings_count = Budget.objects.filter(budget_status='PENDING', budget_area__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-budget_year', '-budget_month').count
    inapprovals = Budget.objects.filter(budget_status='IN APPROVAL', budget_area__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-budget_year', '-budget_month').all
    inapprovals_count = Budget.objects.filter(budget_status='IN APPROVAL', budget_area__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-budget_year', '-budget_month').count
    opens = Budget.objects.filter(budget_status='OPEN', budget_area__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-budget_year', '-budget_month').all
    opens_count = Budget.objects.filter(budget_status='OPEN', budget_area__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-budget_year', '-budget_month').count

    context = {
        'drafts': drafts,
        'drafts_count': draft_count,
        'pendings': pendings,
        'pendings_count': pendings_count,
        'inapprovals': inapprovals,
        'inapprovals_count': inapprovals_count,
        'opens': opens,
        'opens_count': opens_count,
        'tab': _tab,
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

    if request.POST:
        form = FormBudgetUpdate(
            request.POST, request.FILES, instance=budgets)
        if form.is_valid():
            update = form.save(commit=False)
            update.budget_year = budgets.budget_year
            update.budget_month = budgets.budget_month
            update.budget_balance = update.budget_amount + \
                int(request.POST.get('budget_upping'))
            update.save()
            for i in budget_detail:
                i.budget_upping = (i.budget_percent/100) * \
                    budgets.budget_upping
                i.save()

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
        form = FormBudgetUpdate(instance=budgets)

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
        'tab': _tab,
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
        'status': budget.budget_status,
        'year': YEAR_CHOICES,
        'month': MONTH_CHOICES,
        'budget_detail': budget_detail,
        'approval': approval,
        'message': _msg,
        'tab': _tab,
        'channel': channel,
        'segment': 'budget',
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

            budget.budget_status = 'PENDING'
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

            return HttpResponseRedirect(reverse('budget-view', args=['pending', _id, 'NONE']))
        else:
            msg = 'Total budget percentage you entered is not 100%'

    return HttpResponseRedirect(reverse('budget-view', args=[_tab, _id, msg, ]))


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
                                budget.budget_status = 'PENDING'
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
@role_required(allowed_roles='BUDGET-RELEASE')
def budget_release_index(request):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT apps_budget.budget_id, apps_distributor.distributor_name, apps_budget.budget_amount, apps_budget.budget_upping, apps_budget.budget_total, apps_budget.budget_status, apps_budgetrelease.sequence FROM apps_distributor INNER JOIN apps_budget ON apps_distributor.distributor_id = apps_budget.budget_distributor_id INNER JOIN apps_budgetrelease ON apps_budget.budget_id = apps_budgetrelease.budget_id INNER JOIN (SELECT budget_id, MIN(sequence) AS seq FROM apps_budgetrelease WHERE budget_approval_status = 'N' GROUP BY budget_id ORDER BY sequence ASC) AS q_group ON apps_budgetrelease.budget_id = q_group.budget_id AND apps_budgetrelease.sequence = q_group.seq WHERE (apps_budget.budget_status = 'PENDING' OR apps_budget.budget_status = 'IN APPROVAL') AND apps_budgetrelease.budget_approval_id = '" + str(request.user.user_id) + "'")
        release = cursor.fetchall()

    context = {
        'data': release,
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
            "SELECT apps_proposal.proposal_id, apps_proposal.proposal_date, apps_proposal.channel, apps_division.division_name, apps_proposal.total_cost, apps_proposal.status, apps_proposalrelease.sequence FROM apps_division INNER JOIN apps_proposal ON apps_division.division_id = apps_proposal.division_id INNER JOIN apps_proposalrelease ON apps_proposal.proposal_id = apps_proposalrelease.proposal_id INNER JOIN (SELECT proposal_id, MIN(sequence) AS seq FROM apps_proposalrelease WHERE proposal_approval_status = 'N' GROUP BY proposal_id ORDER BY sequence ASC) AS q_group ON apps_proposalrelease.proposal_id = q_group.proposal_id AND apps_proposalrelease.sequence = q_group.seq WHERE (apps_proposal.status = 'PENDING' OR apps_proposal.status = 'IN APPROVAL') AND apps_proposalrelease.proposal_approval_id = '" + str(request.user.user_id) + "'")
        release = cursor.fetchall()

    context = {
        'data': release,
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
        'year': YEAR_CHOICES,
        'month': MONTH_CHOICES,
        'budget_detail': budget_detail,
        'message': _msg,
        'channel': channel,
        'is_revise': _is_revise,
        'approved': approved,
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
    form = FormProposalView(instance=proposal)
    divs = Division.objects.all()
    form_incremental = FormIncrementalSales()
    incremental = IncrementalSales.objects.filter(proposal_id=_id)
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
    form_cost = FormProjectedCost()
    cost = ProjectedCost.objects.filter(proposal_id=_id)
    total_cost = ProjectedCost.objects.filter(
        proposal_id=_id).aggregate(Sum('cost'))
    add_cost = True if budget.budget_balance > 0 else False
    approved = ProposalRelease.objects.get(
        proposal_id=_id, proposal_approval_id=request.user.user_id).proposal_approval_status

    context = {
        'form': form,
        'divs': divs,
        'formInc': form_incremental,
        'incremental': incremental,
        'data': proposal,
        'budget': budget,
        'formCost': form_cost,
        'cost': cost,
        'total': total,
        'total_inc': total['incrp_nom__sum'] if total['incrp_nom__sum'] else 0,
        'total_cost': total_cost['cost__sum'] if total_cost['cost__sum'] else 0,
        'sub_id': _sub_id,
        'action': _act,
        'message': _msg,
        'approved': approved,
        'is_revise': _is_revise,
        'status': proposal.status,
        'add_cost': add_cost,
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
    budgets.budget_amount = '{:,}'.format(budgets.budget_amount)
    budgets.budget_total = '{:,}'.format(budgets.budget_total)
    budget_detail = BudgetDetail.objects.filter(budget_id=_id)
    upping_before = budgets.budget_upping

    if request.POST:
        form = FormBudgetUpdate(
            request.POST, request.FILES, instance=budgets)
        if form.is_valid():
            update = form.save(commit=False)
            update.budget_year = budgets.budget_year
            update.budget_month = budgets.budget_month
            update.save()
            for i in budget_detail:
                i.budget_upping = (i.budget_percent/100) * \
                    budgets.budget_upping
                i.save()

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

            subject = 'Upping Price Revised'
            message = 'Dear All,\n\nThe following is Upping Price update for Budget No. ' + \
                str(_id) + ':\n\nValue before: ' + \
                '{:,}'.format(upping_before) + '\nValue after: ' + \
                '{:,}'.format(update.budget_upping) + '\n\nNote: ' + \
                str(release.upping_note) + '\n\nClick the following link to view the budget.\n' + host.url + 'budget/view/draft/' + \
                str(_id) + '/NONE/' + \
                '\n\nThank you.'
            recipient_list = list(dict.fromkeys(recipients))
            send_email(subject, message, recipient_list)

            return HttpResponseRedirect(reverse('budget-release-view', args=[_id, 'NONE', 0]))
    else:
        form = FormBudgetUpdate(instance=budgets)

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
        'year': YEAR_CHOICES,
        'month': MONTH_CHOICES,
        'budget_detail': budget_detail,
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
    _att = proposal.attachment.name if proposal.attachment else None

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
                attachment = _att if form.cleaned_data['attachment'] != _att else None
                form.save()

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
                if attachment:
                    msg += 'Attachment: ' + str(_att) + '\n'
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
                if attachment:
                    msg += 'Attachment: ' + \
                        str(form.cleaned_data['attachment']) + '\n'
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
        'incremental': incremental,
        'cost': cost,
        'total': total,
        'total_inc': total['incrp_nom__sum'] if total['incrp_nom__sum'] else 0,
        'total_cost': total_cost['cost__sum'] if total_cost['cost__sum'] else 0,
        'data': proposal,
        'divs': divs,
        'msg': msg,
        'message': message,
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
                incremental.swop_nom_carton = int(
                    request.POST.get('swop_nom_carton'))
                incremental.swp_nom_carton = int(
                    request.POST.get('swp_nom_carton'))
                incremental.swop_nom = int(
                    request.POST.get('swop_nom_carton')) * swop_carton
                incremental.swp_nom = int(
                    request.POST.get('swp_nom_carton')) * swp_carton
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
            swop_nom_carton = update.swop_nom_carton
            swp_nom_carton = update.swp_nom_carton
            update.swop_carton = int(request.POST.get('swop_carton'))
            update.swp_carton = int(request.POST.get('swp_carton'))
            update.swop_nom_carton = int(request.POST.get('swop_nom_carton'))
            update.swp_nom_carton = int(request.POST.get('swp_nom_carton'))
            update.save()
            if update.incrp_nom < 0:
                message = 'Incremental Sales must be greater than 0'
                update.swop_carton = swop_carton
                update.swp_carton = swp_carton
                update.swop_nom_carton = swop_nom_carton
                update.swp_nom_carton = swp_nom_carton
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
    message = '0'
    if form.is_valid():
        try:
            check = ProjectedCost.objects.get(
                proposal_id=_id, activities=request.POST.get('activities'))
            if check:
                message = 'Activity already exist'
        except ProjectedCost.DoesNotExist:
            cost = form.save(commit=False)
            if cost.cost > budget_detail.budget_balance:
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
                proposal.status = 'PENDING'
                proposal.save()
                sum_cost = Proposal.objects.filter(budget=proposal.budget, channel=proposal.channel).aggregate(Sum('total_cost'))[
                    'total_cost__sum'] if Proposal.objects.filter(budget=proposal.budget, channel=proposal.channel).exists() else 0
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
    proposal.save()
    sum_cost = Proposal.objects.filter(
        budget=proposal.budget, channel=proposal.channel).aggregate(Sum('total_cost'))['total_cost__sum'] if Proposal.objects.filter(budget=proposal.budget, channel=proposal.channel).exists() else 0
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
    update = ProjectedCost.objects.get(
        proposal_id=_id, id=_activities)
    message = '0'
    if request.POST:
        cost = update.cost
        if int(request.POST.get('cost')) > budget_detail.budget_balance + cost:
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
            proposal.save()
            sum_cost = Proposal.objects.filter(budget=proposal.budget, channel=proposal.channel).aggregate(Sum('total_cost'))[
                'total_cost__sum'] if Proposal.objects.filter(budget=proposal.budget, channel=proposal.channel).exists() else 0
            budget_detail.budget_proposed = sum_cost
            budget_detail.save()
            sum_balance = BudgetDetail.objects.filter(budget=proposal.budget).aggregate(Sum('budget_balance'))[
                'budget_balance__sum'] if BudgetDetail.objects.filter(budget=proposal.budget).exists() else 0
            budget = Budget.objects.get(budget_id=proposal.budget)
            budget.budget_balance = sum_balance
            budget.save()

    return HttpResponseRedirect(reverse('proposal-view', args=[_id, _activities, 'upd-cost', message, 0]))


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
    logo_path = 'https://ksisolusi.com/apps/static/img/favicon.png'
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
    pdf_file.setFont("Helvetica-Bold", 8)
    pdf_file.drawString(25, y, "Objectives")
    pdf_file.drawString(90, y, ":")
    pdf_file.setFont("Helvetica", 8)

    styles = getSampleStyleSheet()
    normal_style = styles["Normal"]
    normal_style.fontSize = 8  # Set font size to 8
    objectives = proposal.objectives.split('\n')
    y -= 4
    for line in objectives:
        objectives_paragraph = Paragraph(line, normal_style)
        objectives_paragraph.wrapOn(pdf_file, page_width - 125, 100)
        objectives_paragraph.drawOn(pdf_file, 100, y)
        y -= 10

    y += 4
    pdf_file.setFont("Helvetica-Bold", 8)
    pdf_file.drawString(25, y, "Mechanism")
    pdf_file.drawString(90, y, ":")
    pdf_file.setFont("Helvetica", 8)
    mechanism = proposal.mechanism.split('\n')
    y -= 4
    for line in mechanism:
        mechanism_paragraph = Paragraph(line, normal_style)
        mechanism_paragraph.wrapOn(pdf_file, page_width - 125, 100)
        mechanism_paragraph.drawOn(pdf_file, 100, y)
        y -= 10

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
    if proposal.attachment:
        pdf_file.drawString(100, y, proposal.attachment.name)
    else:
        pdf_file.drawString(100, y, 'None')

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
        total['incpst_carton__ratio']))
    pdf_file.rect(746, y - 5, 71, 15, stroke=True)
    pdf_file.drawRightString(
        814, y, "{:.1f}%".format(total['incpst_nom__ratio']))

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
    title = 'Proposed By'
    title_width = pdf_file.stringWidth(title, "Helvetica", 8)
    title_x = 25 + ((col_width * (proposer_count + 1)) - title_width) / 2
    pdf_file.drawString(title_x, y, title)

    pdf_file.rect(
        25 + (col_width * (proposer_count + 1)), y - 5, col_width * checker_count, 15, stroke=True)
    title = 'Checked By'
    title_x = 25 + (col_width * (proposer_count + 1)) + \
        ((col_width * checker_count) - title_width) / 2
    pdf_file.drawString(title_x, y, title)

    pdf_file.rect(
        25 + (col_width * (proposer_count + 1)) + (col_width * checker_count), y - 5, col_width * approvers_count, 15, stroke=True)
    title = 'Approved By'
    title_x = 25 + (col_width * (proposer_count + 1)) + \
        (col_width * checker_count) + \
        ((col_width * approvers_count) - title_width) / 2
    pdf_file.drawString(title_x, y, title)

    pdf_file.rect(
        25 + (col_width * (proposer_count + 1)) + (col_width * checker_count) + (col_width * approvers_count), y - 5, col_width * validator_count, 15, stroke=True)
    title = 'Validated By'
    title_x = 25 + (col_width * (proposer_count + 1)) + (col_width * checker_count) + \
        (col_width * approvers_count) + \
        ((col_width * validator_count) - title_width) / 2
    pdf_file.drawString(title_x, y, title)

    pdf_file.rect(
        25 + (col_width * (proposer_count + 1)) + (col_width * checker_count) + (col_width * approvers_count) + (col_width * validator_count), y - 5, col_width * finalizer_count, 15, stroke=True)
    title = 'Approved By'
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

    # Assuming `proposal.attachment` contains the file path of the attachment
    attachment_path = proposal.attachment.path if proposal.attachment else ''

    if attachment_path:
        # Create a PdfFileMerger object
        merger = PdfMerger()

        # Add the existing PDF file to the merger
        merger.append(filename)

        # Add the attachment page to the merger
        merger.append(attachment_path)

        # Save the merged PDF file
        merger.write(filename)

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

    proposal = Proposal.objects.get(proposal_id=_id)
    if release.sequence == approval.sequence:
        proposal.status = 'OPEN'

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

    proposal.save()

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
            proposal_id=_id, sequence__lt=ProposalRelease.objects.get(proposal_id=_id, proposal_approval_id=request.user.user_id).sequence)
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
    msg += host.url + 'proposal_archive/view/reject/' + str(_id) + \
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
                    area_id=_id, approver_id=i[0]).delete()

        return HttpResponseRedirect(reverse('proposal-matrix-view', args=[_id, _channel]))

    context = {
        'data': area,
        'channels': channels,
        'users': users,
        'approvers': approvers,
        'channel': _channel,
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
    approvers = ProposalMatrix.objects.get(area=_id, approver_id=_approver)

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
    approvers = ProposalMatrix.objects.get(area=_id, approver_id=_arg)
    approvers.delete()

    return HttpResponseRedirect(reverse('proposal-matrix-view', args=[_id, _channel]))


@login_required(login_url='/login/')
@role_required(allowed_roles='CLOSING-PERIOD')
def closing_index(request):
    periods = Closing.objects.all()

    context = {
        'data': periods,
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
        'segment': 'closing_period',
        'group_segment': 'master',
        'crud': 'view',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id,
                                menu_id='CLOSING-PERIOD') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/closing_view.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='CLOSING')
def closing(request):
    period = Closing.objects.get(document='BUDGET')
    budgets = Budget.objects.filter(budget_status='OPEN')

    if request.POST:
        period.year_closed = request.POST.get('year_closed')
        period.month_closed = request.POST.get('month_closed')
        next_month = (datetime.datetime(int(period.year_closed),
                      int(period.month_closed), 1) + datetime.timedelta(days=32)).month
        next_year = (datetime.datetime(int(period.year_closed),
                     int(period.month_closed), 1) + datetime.timedelta(days=32)).year
        period.year_open = next_year
        period.month_open = next_month
        period.save()
        for budget in budgets:
            detail = BudgetDetail.objects.filter(budget_id=budget.budget_id)
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
            'segment': 'closing',
            'group_segment': 'budget',
            'crud': 'index',
            'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
            'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='CLOSING') if not request.user.is_superuser else Auth.objects.all(),
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
        'segment': 'closing',
        'years': YEAR_CHOICES,
        'months': MONTH_CHOICES,
        'group_segment': 'budget',
        'crud': 'index',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='CLOSING') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/closing.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='DIVISION')
def division_index(request):
    divisions = Division.objects.all()

    context = {
        'data': divisions,
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
    pendings = Proposal.objects.filter(status='PENDING', area__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-proposal_id').all
    pending_count = Proposal.objects.filter(status='PENDING', area__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-proposal_id').count
    inapprovals = Proposal.objects.filter(status='IN APPROVAL', area__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-proposal_id').all
    inapproval_count = Proposal.objects.filter(status='IN APPROVAL', area__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-proposal_id').count
    opens = Proposal.objects.filter(status='OPEN', area__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-proposal_id').all
    open_count = Proposal.objects.filter(status='OPEN', area__in=AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', flat=True)).order_by('-proposal_id').count

    context = {
        'drafts': drafts,
        'draft_count': draft_count,
        'pendings': pendings,
        'pending_count': pending_count,
        'inapprovals': inapprovals,
        'inapproval_count': inapproval_count,
        'opens': opens,
        'open_count': open_count,
        'tab': _tab,
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
    budgets = Budget.objects.filter(budget_balance__gt=0, budget_status='OPEN',
                                    budget_area=selected_area) if selected_area != '0' else None
    budget_detail = BudgetDetail.objects.filter(
        budget_id=selected_budget) if selected_budget != '0' else None
    distributor = Budget.objects.get(
        budget_id=selected_budget).budget_distributor_id if selected_budget != '0' else None
    message = ''
    no_save = False
    if selected_area != '0' and selected_channel != '0':
        approvers = ProposalMatrix.objects.filter(
            area_id=_area, channel_id=_channel).order_by('sequence')
        if approvers.count() == 0:
            message = "No proposal's approver found for this area and channel."
            no_save = True

    try:
        _no = Proposal.objects.all().order_by('seq_number').last()
    except Proposal.DoesNotExist:
        _no = None
    if _no is None:
        format_no = '{:04d}'.format(1)
    else:
        format_no = '{:04d}'.format(_no.seq_number + 1)

    _id = 'PBS-2' + format_no + '/' + selected_channel + '/' + selected_area + '/' + \
        str(distributor) + '/' + \
        str(datetime.datetime.now().month) + \
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
                parent.attachment = form.cleaned_data['attachment']
                parent.status = 'DRAFT'
                parent.seq_number = _no.seq_number + 1 if _no else 1
                parent.entry_pos = request.user.position.position_id
                parent.save()

                if not settings.DEBUG:
                    proposal = Proposal.objects.get(
                        proposal_id=parent.proposal_id)
                    my_file = proposal.attachment
                    filename = '../../www/selmar/apps/media/' + my_file.name
                    with open(filename, 'wb+') as temp_file:
                        for chunk in my_file.chunks():
                            temp_file.write(chunk)

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
        'msg': msg,
        'message': message,
        'no_save': no_save,
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
    form = FormProposalView(instance=proposal)
    divs = Division.objects.all()
    form_incremental = FormIncrementalSales()
    incremental = IncrementalSales.objects.filter(proposal_id=_id)
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
    form_cost = FormProjectedCost()
    cost = ProjectedCost.objects.filter(proposal_id=_id)
    total_cost = ProjectedCost.objects.filter(
        proposal_id=_id).aggregate(Sum('cost'))
    add_cost = True if budget.budget_balance > 0 else False

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

    context = {
        'data': proposal,
        'budget': budget,
        'form': form,
        'divs': divs,
        'formInc': form_incremental,
        'incremental': incremental,
        'formCost': form_cost,
        'cost': cost,
        'total': total,
        'total_inc': total['incrp_nom__sum'] if total['incrp_nom__sum'] else 0,
        'total_cost': total_cost['cost__sum'] if total_cost['cost__sum'] else 0,
        'tab': _tab,
        'sub_id': _sub_id,
        'action': _act,
        'approval': approval,
        'message': _msg,
        'status': proposal.status,
        'add_cost': add_cost,
        'segment': 'proposal',
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
                incremental.swop_nom_carton = int(
                    request.POST.get('swop_nom_carton'))
                incremental.swp_nom_carton = int(
                    request.POST.get('swp_nom_carton'))
                incremental.swop_nom = int(
                    request.POST.get('swop_nom_carton')) * swop_carton
                incremental.swp_nom = int(
                    request.POST.get('swp_nom_carton')) * swp_carton
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
    message = '0'
    if form.is_valid():
        try:
            check = ProjectedCost.objects.get(
                proposal_id=_id, activities=request.POST.get('activities'))
            if check:
                message = 'Activity already exist'
        except ProjectedCost.DoesNotExist:
            cost = form.save(commit=False)
            if cost.cost > budget_detail.budget_balance:
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
                proposal.status = 'PENDING' if proposal.status == 'DRAFT' else proposal.status
                proposal.save()
                sum_cost = Proposal.objects.filter(budget=proposal.budget, channel=proposal.channel).aggregate(Sum('total_cost'))[
                    'total_cost__sum'] if Proposal.objects.filter(budget=proposal.budget, channel=proposal.channel).exists() else 0
                budget_detail.budget_proposed = sum_cost
                budget_detail.save()
                sum_balance = BudgetDetail.objects.filter(budget=proposal.budget).aggregate(Sum('budget_balance'))[
                    'budget_balance__sum'] if BudgetDetail.objects.filter(budget=proposal.budget).exists() else 0
                budget = Budget.objects.get(budget_id=proposal.budget)
                budget.budget_balance = sum_balance
                budget.save()

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

    return HttpResponseRedirect(reverse('proposal-view', args=[_tab, _id, '0', 'add-cost', message]))


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
    proposal.save()
    sum_cost = Proposal.objects.filter(
        budget=proposal.budget, channel=proposal.channel).aggregate(Sum('total_cost'))['total_cost__sum'] if Proposal.objects.filter(budget=proposal.budget, channel=proposal.channel).exists() else 0
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
    proposal = Proposal.objects.get(proposal_id=_id)
    proposal.attachment = None
    proposal.save()
    return HttpResponseRedirect(reverse('proposal-view', args=[_tab, _id, '0', '0', '0']))


@login_required(login_url='/login/')
@role_required(allowed_roles='PROPOSAL-RELEASE')
def remove_release_attachment(request, _id):
    proposal = Proposal.objects.get(proposal_id=_id)
    proposal.attachment = None
    proposal.save()
    return render(request, 'home/proposal_release_view.html')


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
            swop_nom_carton = update.swop_nom_carton
            swp_nom_carton = update.swp_nom_carton
            update.swop_carton = int(request.POST.get('swop_carton'))
            update.swp_carton = int(request.POST.get('swp_carton'))
            update.swop_nom_carton = int(request.POST.get('swop_nom_carton'))
            update.swp_nom_carton = int(request.POST.get('swp_nom_carton'))
            update.save()
            if update.incrp_nom < 0:
                message = 'Incremental Sales must be greater than 0'
                update.swop_carton = swop_carton
                update.swp_carton = swp_carton
                update.swop_nom_carton = swop_nom_carton
                update.swp_nom_carton = swp_nom_carton
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
    update = ProjectedCost.objects.get(
        proposal_id=_id, id=_activities)
    message = '0'
    if request.POST:
        cost = update.cost
        if int(request.POST.get('cost')) > budget_detail.budget_balance + cost:
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
            proposal.status = 'PENDING' if proposal.status == 'DRAFT' else proposal.status
            proposal.save()
            sum_cost = Proposal.objects.filter(budget=proposal.budget, channel=proposal.channel).aggregate(Sum('total_cost'))[
                'total_cost__sum'] if Proposal.objects.filter(budget=proposal.budget, channel=proposal.channel).exists() else 0
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
                parent.save()
                if not settings.DEBUG:
                    my_file = proposal.attachment
                    filename = '../../www/selmar/apps/media/' + my_file.name
                    with open(filename, 'wb+') as temp_file:
                        for chunk in my_file.chunks():
                            temp_file.write(chunk)
                return HttpResponseRedirect(reverse('proposal-view', args=[_tab, _id, '0', '0', '0']))
    else:
        form = FormProposalUpdate(instance=proposal)

    context = {
        'form': form,
        'data': proposal,
        'divs': divs,
        'incremental': incremental,
        'cost': cost,
        'total': total,
        'total_inc': total['incrp_nom__sum'] if total['incrp_nom__sum'] else 0,
        'total_cost': total_cost['cost__sum'] if total_cost['cost__sum'] else 0,
        'tab': _tab,
        'message': message,
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
    sum_cost = Proposal.objects.filter(
        budget=proposal.budget, channel=proposal.channel).aggregate(Sum('total_cost'))['total_cost__sum'] if Proposal.objects.filter(budget=proposal.budget, channel=proposal.channel).exists() else 0
    budget_detail.budget_proposed = sum_cost
    budget_detail.save()
    sum_balance = BudgetDetail.objects.filter(budget=proposal.budget).aggregate(Sum('budget_balance'))[
        'budget_balance__sum'] if BudgetDetail.objects.filter(budget=proposal.budget).exists() else 0
    budget = Budget.objects.get(budget_id=proposal.budget)
    budget.budget_balance = sum_balance
    budget.save()

    return HttpResponseRedirect(reverse('proposal-index', args=[_tab, ]))
