from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.db import connection, IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.forms.models import modelformset_factory
from apps.forms import *
from apps.models import *
from authentication.decorators import role_required


@login_required(login_url='/login/')
def home(request):
    context = {
        'segment': 'index',
        'role': request.user.position_id,
    }
    return render(request, 'home/index.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles=['ADMIN'])
def user_index(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT user_id, username, email, position_name FROM apps_user INNER JOIN apps_position ON apps_user.position_id = apps_position.position_id")
        users = cursor.fetchall()

    context = {
        'data': users,
        'segment': 'user',
        'crud': 'index',
        'role': request.user.position_id,
    }

    return render(request, 'home/user_index.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles=['ADMIN'])
def user_add(request):
    position = Position.objects.all()
    if request.POST:
        form = FormUser(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('user-index'))
        else:
            message = form.errors
            context = {
                'form': form,
                'position': position,
                'segment': 'user',
                'crud': 'add',
                'message': message,
                'role': request.user.position_id,
            }
            return render(request, 'home/user_add.html', context)
    else:
        form = FormUser()
        context = {
            'form': form,
            'position': position,
            'segment': 'user',
            'crud': 'add',
            'role': request.user.position_id,
        }
        return render(request, 'home/user_add.html', context)


# View User
@login_required(login_url='/login/')
@role_required(allowed_roles=['ADMIN'])
def user_view(request, _id):
    users = User.objects.get(user_id=_id)
    form = FormUserView(instance=users)
    position = Position.objects.all()

    context = {
        'form': form,
        'data': users,
        'positions': position,
        'segment': 'user',
        'crud': 'view',
        'role': request.user.position_id,
    }
    return render(request, 'home/user_view.html', context)


# Update User
@login_required(login_url='/login/')
@role_required(allowed_roles=['ADMIN'])
def user_update(request, _id):
    users = User.objects.get(user_id=_id)
    position = Position.objects.all()
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
        'segment': 'user',
        'crud': 'update',
        'message': message,
        'role': request.user.position_id,
    }
    return render(request, 'home/user_view.html', context)


# Delete User
@login_required(login_url='/login/')
@role_required(allowed_roles=['ADMIN'])
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
        'role': request.user.position_id,
    }
    return render(request, 'home/user_change_password.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles=['ADMIN'])
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
        'crud': 'update',
        'message': message,
        'role': request.user.position_id,
    }
    return render(request, 'home/user_set_password.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles=['ADMIN'])
def distributor_index(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT distributor_id, distributor_name FROM apps_distributor")
        distributors = cursor.fetchall()

    context = {
        'data': distributors,
        'segment': 'distributor',
        'crud': 'index',
        'role': request.user.position_id,
    }

    return render(request, 'home/distributor_index.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles=['ADMIN'])
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
                'crud': 'add',
                'message': message,
                'role': request.user.position_id,
            }
            return render(request, 'home/distributor_add.html', context)
    else:
        form = FormDistributor()
        context = {
            'form': form,
            'segment': 'distributor',
            'crud': 'add',
            'role': request.user.position_id,
        }
        return render(request, 'home/distributor_add.html', context)
    

# View Distributor
@login_required(login_url='/login/')
@role_required(allowed_roles=['ADMIN'])
def distributor_view(request, _id):
    distributors = Distributor.objects.get(distributor_id=_id)
    form = FormDistributorView(instance=distributors)

    context = {
        'form': form,
        'data': distributors,
        'segment': 'distributor',
        'crud': 'view',
        'role': request.user.position_id,
    }
    return render(request, 'home/distributor_view.html', context)


# Update Distributor
@login_required(login_url='/login/')
@role_required(allowed_roles=['ADMIN'])
def distributor_update(request, _id):
    distributors = Distributor.objects.get(distributor_id=_id)
    if request.POST:
        form = FormDistributorUpdate(request.POST, request.FILES, instance=distributors)
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
        'crud': 'update',
        'message': message,
        'role': request.user.position_id,
    }
    return render(request, 'home/distributor_view.html', context)


# Delete Distributor
@login_required(login_url='/login/')
@role_required(allowed_roles=['ADMIN'])
def distributor_delete(request, _id):
    distributors = Distributor.objects.get(distributor_id=_id)

    distributors.delete()
    return HttpResponseRedirect(reverse('distributor-index'))


@login_required(login_url='/login/')
@role_required(allowed_roles=['ADMIN'])
def area_sales_index(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT area_id, area_name, manager FROM apps_areasales")
        area_sales = cursor.fetchall()

    context = {
        'data': area_sales,
        'segment': 'area_sales',
        'crud': 'index',
        'role': request.user.position_id,
    }

    return render(request, 'home/area_sales_index.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles=['ADMIN'])
def area_sales_add(request):
    AreaSalesDetailFormSet = modelformset_factory(AreaSalesDetail, form=FormAreaSalesDetail, extra=0, can_delete=True, can_delete_extra=True)
    distributor = Distributor.objects.all()

    if request.POST:
        form = FormAreaSales(request.POST, request.FILES)
        formset = AreaSalesDetailFormSet(request.POST, queryset=AreaSalesDetail.objects.none())

        if all([form.is_valid(), formset.is_valid()]):
            try:
                parent = form.save(commit=False)
                parent.save()
                for form in formset:
                    if form.cleaned_data.get('distributor') is None:
                        if form.cleaned_data.get('DELETE'):
                            continue
                        else:
                            continue
                    else:
                        if form.cleaned_data.get('DELETE'):
                            form.instance.delete()
                            continue
                        
                    child = form.save(commit=False)
                    child.area = parent
                    child.save()
                return HttpResponseRedirect(reverse('area-sales-index'))
            except Exception:
                return HttpResponseRedirect(reverse('area-sales-index'))
        else:
            message = form.errors
            context = {
                'form': form,
                'segment': 'area_sales',
                'crud': 'add',
                'message': message,
                'role': request.user.position_id,
            }
            return render(request, 'home/area_sales_add.html', context)
    else:
        form = FormAreaSales()
        formset = AreaSalesDetailFormSet(queryset=AreaSalesDetail.objects.none())

        message = form.errors
        context = {
            'form': form,
            'formset': formset,
            'segment': 'area_sales',
            'crud': 'add',
            'message': message,
            'role': request.user.position_id,
            'distributors': distributor,
        }
        return render(request, 'home/area_sales_add.html', context)
    

# View Area Sales
@login_required(login_url='/login/')
@role_required(allowed_roles=['ADMIN'])
def area_sales_view(request, _id):
    area_sales = AreaSales.objects.get(area_id=_id)
    AreaSalesDetailFormSet = modelformset_factory(AreaSalesDetail, form=FormAreaSalesDetailView, extra=0)
    qs = area_sales.areasalesdetail_set.all()
    distributor = Distributor.objects.all()
    form = FormAreaSalesView(instance=area_sales)
    formset = AreaSalesDetailFormSet(queryset=qs)

    context = {
        'form': form,
        'formset': formset,
        'data': area_sales,
        'segment': 'area_sales',
        'crud': 'view',
        'role': request.user.position_id,
        'distributors': distributor,
    }
    return render(request, 'home/area_sales_view.html', context)


# Update Area Sales
@login_required(login_url='/login/')
@role_required(allowed_roles=['ADMIN'])
def area_sales_update(request, _id):
    area_sales = AreaSales.objects.get(area_id=_id)
    AreaSalesDetailFormSet = modelformset_factory(AreaSalesDetail, form=FormAreaSalesDetail, extra=0, can_delete=True, can_delete_extra=True)
    qs = area_sales.areasalesdetail_set.all()
    distributor = Distributor.objects.all()
    if request.POST:
        form = FormAreaSalesUpdate(request.POST, request.FILES, instance=area_sales)
        formset = AreaSalesDetailFormSet(request.POST, queryset=qs)
        if all([form.is_valid(), formset.is_valid()]):
            try:
                parent = form.save(commit=False)
                parent.save()
                for form in formset:
                    if form.cleaned_data.get('distributor') is None:
                        if form.cleaned_data.get('DELETE'):
                            continue
                        else:
                            continue
                    else:
                        if form.cleaned_data.get('DELETE'):
                            form.instance.delete()
                            continue
                        
                    child = form.save(commit=False)
                    child.area = parent
                    child.save()
                return HttpResponseRedirect(reverse('area-sales-view', args=[_id, ]))
            except Exception:
                return HttpResponseRedirect(reverse('area-sales-view', args=[_id, ]))
    else:
        form = FormAreaSalesUpdate(instance=area_sales)
        formset = AreaSalesDetailFormSet(queryset=qs)

    message = form.errors
    context = {
        'form': form,
        'formset': formset,
        'data': area_sales,
        'segment': 'area_sales',
        'crud': 'update',
        'message': message,
        'role': request.user.position_id,
        'distributors': distributor,
    }
    return render(request, 'home/area_sales_view.html', context)


# Delete Area Sales
@login_required(login_url='/login/')
@role_required(allowed_roles=['ADMIN'])
def area_sales_delete(request, _id):
    area_sales = AreaSales.objects.get(area_id=_id)

    area_sales.delete()
    return HttpResponseRedirect(reverse('area-sales-index'))


@login_required(login_url='/login/')
@role_required(allowed_roles=['ADMIN'])
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
                'crud': 'add',
                'message': message,
                'role': request.user.position_id,
            }
            return render(request, 'home/position_add.html', context)
    else:
        form = FormPosition()
        context = {
            'form': form,
            'segment': 'position',
            'crud': 'add',
            'role': request.user.position_id,
        }
        return render(request, 'home/position_add.html', context)
    

@login_required(login_url='/login/')
@role_required(allowed_roles=['ADMIN'])
def position_index(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT position_id, position_name FROM apps_position")
        positions = cursor.fetchall()

    context = {
        'data': positions,
        'segment': 'position',
        'crud': 'index',
        'role': request.user.position_id,
    }

    return render(request, 'home/position_index.html', context)


# Update Position
@login_required(login_url='/login/')
@role_required(allowed_roles=['ADMIN'])
def position_update(request, _id):
    positions = Position.objects.get(position_id=_id)
    if request.POST:
        form = FormPositionUpdate(request.POST, request.FILES, instance=positions)
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
        'crud': 'update',
        'message': message,
        'role': request.user.position_id,
    }
    return render(request, 'home/position_view.html', context)


# Delete Position
@login_required(login_url='/login/')
@role_required(allowed_roles=['ADMIN'])
def position_delete(request, _id):
    positions = Position.objects.get(position_id=_id)

    positions.delete()
    return HttpResponseRedirect(reverse('position-index'))


@login_required(login_url='/login/')
@role_required(allowed_roles=['ADMIN'])
def position_view(request, _id):
    positions = Position.objects.get(position_id=_id)
    form = FormPositionView(instance=positions)

    context = {
        'form': form,
        'data': positions,
        'segment': 'position',
        'crud': 'view',
        'role': request.user.position_id,
    }
    return render(request, 'home/position_view.html', context)
