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
from django.core.mail import send_mail
from core.settings import EMAIL_HOST_USER
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
    area = AreaUser.objects.filter(
        user_id=request.user.user_id).values_list('area_id', 'area__area_name')
    selected_area = _area
    name = AreaSales.objects.get(
        area_id=selected_area) if selected_area != 'NONE' else None
    distributor = Distributor.objects.filter(
        distributor_id__in=AreaSalesDetail.objects.filter(area_id=selected_area).values_list('distributor_id', flat=True))
    message = ''
    if request.POST:
        form = FormBudget(request.POST, request.FILES)
        if form.is_valid():
            _id = 'UBS/' + \
                request.POST.get('budget_area') + '/' + \
                request.POST.get('budget_distributor') + '/' + request.POST.get(
                    'budget_month') + '/' + request.POST.get('budget_year')
            try:
                budget = Budget.objects.get(budget_id=_id)
                if budget:
                    message = 'Budget already exist'
            except Budget.DoesNotExist:
                parent = form.save(commit=False)
                parent.budget_status = 'DRAFT'
                parent.save()
                area = parent.budget_area.area_id
                approvers = BudgetApproval.objects.filter(
                    area_id=area).order_by('sequence')
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

                return HttpResponseRedirect(reverse('budget-view', args=[parent.budget_id, 'NONE']))
    else:
        form = FormBudget(
            initial={'budget_year': datetime.datetime.now().year, 'budget_month': datetime.datetime.now().month, 'budget_amount': 0, 'budget_upping': 0, 'budget_total': 0})
    context = {
        'message': message,
        'form': form,
        'area': area,
        'distributor': distributor,
        'selected_area': selected_area,
        'name': name,
        'segment': 'budget',
        'group_segment': 'budget',
        'crud': 'add',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='BUDGET') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/budget_add.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='BUDGET')
def budget_index(request):
    budgets = Budget.objects.all()

    context = {
        'data': budgets,
        'segment': 'budget',
        'group_segment': 'budget',
        'crud': 'index',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='BUDGET') if not request.user.is_superuser else Auth.objects.all(),
    }

    return render(request, 'home/budget_index.html', context)


# Update Budget
@login_required(login_url='/login/')
@role_required(allowed_roles='BUDGET')
def budget_update(request, _id):
    budgets = Budget.objects.get(budget_id=_id)
    budgets.budget_amount = '{:,}'.format(budgets.budget_amount)
    budgets.budget_total = '{:,}'.format(budgets.budget_total)
    budget_detail = BudgetDetail.objects.filter(budget_id=_id)

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
            return HttpResponseRedirect(reverse('budget-view', args=[_id, 'NONE']))
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
        'segment': 'budget',
        'group_segment': 'budget',
        'crud': 'update',
        'message': message if message else 'NONE',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='BUDGET') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/budget_view.html', context)


# Delete Budget
@login_required(login_url='/login/')
@role_required(allowed_roles='BUDGET')
def budget_delete(request, _id):
    budgets = Budget.objects.get(budget_id=_id)

    budgets.delete()
    return HttpResponseRedirect(reverse('budget-index'))


@login_required(login_url='/login/')
@role_required(allowed_roles='BUDGET')
def budget_view(request, _id, _msg):
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

    context = {
        'form': form,
        'data': budget,
        'status': budget.budget_status,
        'year': YEAR_CHOICES,
        'month': MONTH_CHOICES,
        'budget_detail': budget_detail,
        'approval': approval,
        'message': _msg,
        'channel': channel,
        'segment': 'budget',
        'group_segment': 'budget',
        'crud': 'view',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='BUDGET') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/budget_view.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles='BUDGET')
def budget_detail_update(request, _id):
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
            message = 'Dear ' + approver[0] + ',\n\nYou have a budget to approve. Please check your dashboard.\n\n' + \
                'Click this link to approve, revise or return the budget. http://127.0.0.1:8000/budget/release/' + \
                '\n\nThank you.'
            send_email(subject, message, [email[0]])

            return HttpResponseRedirect(reverse('budget-view', args=[_id, 'NONE']))
        else:
            msg = 'Total budget percentage you entered is not 100%'

    return HttpResponseRedirect(reverse('budget-view', args=[_id, msg, ]))


@login_required(login_url='/login/')
@role_required(allowed_roles='UPLOAD')
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
                    for i in range(col, col+(channels.count())):
                        hundreds += data[i]
                    if hundreds == 100:
                        for channel in channels:
                            try:
                                rec = BudgetDetail.objects.get(
                                    budget_id=data[4], budget_channel_id=channel.channel_id)
                                rec.budget_percent = data[col]
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
                message = 'Dear ' + mail_to[0] + ',\n\nYou have a budget to approve. Please check your dashboard.\n\n' + \
                    'Click this link to approve, revise or return the budget. http://127.0.0.1:8000/budget/release/' + \
                    '\n\nThank you.'
                send_email(subject, message, mail_to[1])

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
@role_required(allowed_roles='UPLOAD')
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

    context = {
        'form': form,
        'data': budget,
        'year': YEAR_CHOICES,
        'month': MONTH_CHOICES,
        'budget_detail': budget_detail,
        'message': _msg,
        'channel': channel,
        'is_revise': _is_revise,
        'segment': 'budget_release',
        'group_segment': 'budget',
        'crud': 'view',
        'role': Auth.objects.filter(user_id=request.user.user_id).values_list('menu_id', flat=True),
        'btn': Auth.objects.get(user_id=request.user.user_id, menu_id='BUDGET-RELEASE') if not request.user.is_superuser else Auth.objects.all(),
    }
    return render(request, 'home/budget_release_view.html', context)


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
                    "SELECT budget_approval_email FROM apps_budgetrelease WHERE budget_id = '" + str(_id) + "' AND budget_approval_status = 'Y'")
                approver_mail = cursor.fetchone()
                recipients.append(approver_mail)

            subject = 'Upping Price Revised'
            message = 'Dear All,\n\nThe following is Upping Price update for Budget No. ' + \
                str(_id) + ':\n\nValue before: ' + \
                '{:,}'.format(upping_before) + '\nValue after: ' + \
                '{:,}'.format(update.budget_upping) + '\n\nNote: ' + \
                str(release.upping_note) + '\n\nClick the following link to view the budget. http://127.0.0.1:8000/budget/view/' + \
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
                    "SELECT budget_approval_email FROM apps_budgetrelease WHERE budget_id = '" + str(_id) + "' AND budget_approval_status = 'Y'")
                approver_mail = cursor.fetchone()
                recipients.append(approver_mail[0])

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
                str(release.percentage_note) + '\n\nClick the following link to view the budget. http://127.0.0.1:8000/budget/view/' + \
                str(_id) + '/NONE/' + \
                '\n\nThank you.'
            recipient_list = list(dict.fromkeys(recipients))
            send_email(subject, message, recipient_list)

            return HttpResponseRedirect(reverse('budget-release-view', args=[_id, 'NONE', 0]))
        else:
            msg = 'Total budget percentage you entered is not 100%'

    return HttpResponseRedirect(reverse('budget-release-view', args=[_id, msg, 1]))


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
                "SELECT username FROM apps_budgetrelease INNER JOIN apps_user ON apps_budgetrelease.budget_approval_id = apps_user.user_id WHERE budget_id = '" + str(_id) + "' AND budget_approval_status = 'N' ORDER BY sequence LIMIT 1")
            approver = cursor.fetchone()

        subject = 'Budget Approval'
        message = 'Dear ' + approver[0] + ',\n\nYou have a budget to approve. Please check your dashboard.\n\n' + \
            'Click this link to approve, revise or return the budget. http://127.0.0.1:8000/budget/release/' + \
            '\n\nThank you.'
        send_email(subject, message, [email[0]])

    budget.save()

    return HttpResponseRedirect(reverse('budget-release-index'))


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
            "SELECT budget_approval_email FROM apps_budgetrelease WHERE budget_id = '" + str(_id) + "' AND budget_approval_status = 'Y'")
        approver_mail = cursor.fetchone()
        recipients.append(approver_mail)

    print(recipients)

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
        str(note.return_note) + '\n\nClick the following link to revise the budget. http://127.0.0.1:8000/budget/view/' + \
        str(_id) + '/NONE/' + \
        '\n\nThank you.'
    recipient_list = list(dict.fromkeys(recipients))
    send_email(subject, message, recipient_list)

    return HttpResponseRedirect(reverse('budget-release-index'))


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
@role_required(allowed_roles='BUDGET-APPROVAL')
def budget_approval_update(request, _id, _approver):
    approvers = BudgetApproval.objects.get(area=_id, approver_id=_approver)

    if request.POST:
        approvers.sequence = request.POST.get('sequence')
        approvers.save()

        return HttpResponseRedirect(reverse('budget-approval-view', args=[_id, ]))

    return render(request, 'home/budget_approval_view.html')


@login_required(login_url='/login/')
@role_required(allowed_roles='BUDGET-APPROVAL')
def budget_approval_delete(request, _id, _arg):
    approvers = BudgetApproval.objects.get(area=_id, approver_id=_arg)
    approvers.delete()

    return HttpResponseRedirect(reverse('budget-approval-view', args=[_id, ]))
