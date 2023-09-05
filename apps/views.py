from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from apps.forms import *
from apps.models import *
from authentication.decorators import role_required


@login_required(login_url='/login/')
def home(request):
    context = {
        'segment': 'index',
        'role': request.user.role,
    }
    return render(request, 'home/index.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles=['Admin'])
def user_index(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT apps_user.id, username, role FROM apps_user")
        users = cursor.fetchall()

    context = {
        'data': users,
        'segment': 'user',
        'crud': 'index',
        'role': request.user.role,
    }

    return render(request, 'home/user_index.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles=['Admin'])
def user_add(request):
    if request.POST:
        form = FormUser(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('user-index'))
        else:
            message = form.errors
            context = {
                'form': form,
                'segment': 'user',
                'crud': 'add',
                'message': message,
                'role': request.user.role,
            }
            return render(request, 'home/user_add.html', context)
    else:
        form = FormUser()
        context = {
            'form': form,
            'segment': 'user',
            'crud': 'add',
            'role': request.user.role,
        }
        return render(request, 'home/user_add.html', context)


# Update User
@login_required(login_url='/login/')
@role_required(allowed_roles=['Admin'])
def user_update(request, _id):
    users = User.objects.get(id=_id)
    if request.POST:
        form = FormUserUpdate(request.POST, request.FILES, instance=users)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('user-index'))
    else:
        form = FormUserUpdate(instance=users)

    message = form.errors
    context = {
        'form': form,
        'data': users,
        'segment': 'user',
        'crud': 'update',
        'message': message,
        'role': request.user.role,
    }
    return render(request, 'home/user_view.html', context)


# Delete User
@login_required(login_url='/login/')
@role_required(allowed_roles=['Admin'])
def user_delete(request, _id):
    users = User.objects.get(id=_id)

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
        'role': request.user.role,
    }
    return render(request, 'home/user_change_password.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles=['Admin'])
def set_password(request, _id):
    users = User.objects.get(id=_id)
    if request.POST:
        form = FormSetPassword(data=request.POST, user=users)
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return HttpResponseRedirect(reverse('user-index'))
    else:
        form = FormSetPassword(user=users)

    message = form.errors
    context = {
        'form': form,
        'data': users,
        'segment': 'user',
        'crud': 'update',
        'message': message,
        'role': request.user.role,
    }
    return render(request, 'home/user_set_password.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles=['Admin'])
def setup(request):
    data = Setup.objects.get(id=1)
    if request.POST:
        form = FormSetup(request.POST, request.FILES, instance=data)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('home'))
    else:
        form = FormSetup(instance=data)

    message = form.errors
    context = {
        'form': form,
        'data': data,
        'segment': 'setup',
        'crud': 'update',
        'message': message,
        'role': request.user.role,
    }
    return render(request, 'home/setup.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles=['Admin'])
def cab_index(request):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT apps_cabang.id, nama, manager, telp FROM apps_cabang")
        cabang = cursor.fetchall()

    context = {
        'data': cabang,
        'segment': 'cabang',
        'crud': 'index',
        'role': request.user.role,
    }

    return render(request, 'home/cab_index.html', context)


@login_required(login_url='/login/')
@role_required(allowed_roles=['Admin'])
def cab_add(request):
    if request.POST:
        form = FormCabang(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('cab-index'))
        else:
            message = form.errors
            context = {
                'form': form,
                'segment': 'cabang',
                'crud': 'add',
                'message': message,
                'role': request.user.role,
            }
            return render(request, 'home/cab_add.html', context)
    else:
        form = FormCabang()
        context = {
            'form': form,
            'segment': 'cabang',
            'crud': 'add',
            'role': request.user.role,
        }
        return render(request, 'home/cab_add.html', context)


# Update Cabang
@login_required(login_url='/login/')
@role_required(allowed_roles=['Admin'])
def cab_update(request, _id):
    cabang = Cabang.objects.get(id=_id)
    if request.POST:
        form = FormCabang(request.POST, request.FILES, instance=cabang)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('cab-index'))
    else:
        form = FormCabang(instance=cabang)

    message = form.errors
    context = {
        'form': form,
        'data': cabang,
        'segment': 'cabang',
        'crud': 'update',
        'message': message,
        'role': request.user.role,
    }
    return render(request, 'home/cab_view.html', context)


# Delete Cabang
@login_required(login_url='/login/')
@role_required(allowed_roles=['Admin'])
def cab_delete(request, _id):
    cabang = Cabang.objects.get(id=_id)
    cabang.delete()
    return HttpResponseRedirect(reverse('cab-index'))


# List Paket
@login_required(login_url='/login/')
@role_required(allowed_roles=['Admin'])
def paket_index(request):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT id, nama FROM apps_paket")
        paket = cursor.fetchall()

    context = {
        'data': paket,
        'segment': 'paket',
        'crud': 'index',
        'role': request.user.role,
    }

    return render(request, 'home/paket_index.html', context)


# Add Paket
@login_required(login_url='/login/')
@role_required(allowed_roles=['Admin'])
def paket_add(request):
    if request.POST:
        form = FormPaket(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('paket-index'))
        else:
            message = form.errors
            context = {
                'form': form,
                'segment': 'paket',
                'crud': 'add',
                'message': message,
                'role': request.user.role,
            }
            return render(request, 'home/paket_add.html', context)
    else:
        form = FormPaket()
        context = {
            'form': form,
            'segment': 'paket',
            'crud': 'add',
            'role': request.user.role,
        }
        return render(request, 'home/paket_add.html', context)


# Update Paket
@login_required(login_url='/login/')
@role_required(allowed_roles=['Admin'])
def paket_update(request, _id):
    paket = Paket.objects.get(id=_id)
    if request.POST:
        form = FormPaket(request.POST, request.FILES, instance=paket)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('paket-index'))
    else:
        form = FormPaket(instance=paket)

    message = form.errors
    context = {
        'form': form,
        'data': paket,
        'segment': 'paket',
        'crud': 'update',
        'message': message,
        'role': request.user.role,
    }
    return render(request, 'home/paket_view.html', context)


# Delete Paket
@login_required(login_url='/login/')
@role_required(allowed_roles=['Admin'])
def paket_delete(request, _id):
    paket = Paket.objects.get(id=_id)
    paket.delete()
    return HttpResponseRedirect(reverse('paket-index'))


# List Kategori Item
@login_required(login_url='/login/')
@role_required(allowed_roles=['Admin'])
def kategori_item_index(request):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT id, nama FROM apps_kategoriitem")
        kategori_item = cursor.fetchall()

    context = {
        'data': kategori_item,
        'segment': 'kategori-item',
        'crud': 'index',
        'role': request.user.role,
    }

    return render(request, 'home/kat_item_index.html', context)


# Add Kategori Item
@login_required(login_url='/login/')
@role_required(allowed_roles=['Admin'])
def kategori_item_add(request):
    if request.POST:
        form = FormKategoriItem(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('kat-item-index'))
        else:
            message = form.errors
            context = {
                'form': form,
                'segment': 'kategori-item',
                'crud': 'add',
                'message': message,
                'role': request.user.role,
            }
            return render(request, 'home/kat_item_add.html', context)
    else:
        form = FormKategoriItem()
        context = {
            'form': form,
            'segment': 'kategori-item',
            'crud': 'add',
            'role': request.user.role,
        }
        return render(request, 'home/kat_item_add.html', context)
    

# Update Kategori Item
@login_required(login_url='/login/')
@role_required(allowed_roles=['Admin'])
def kategori_item_update(request, _id):
    kategori_item = KategoriItem.objects.get(id=_id)
    if request.POST:
        form = FormKategoriItem(request.POST, request.FILES, instance=kategori_item)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('kat-item-index'))
    else:
        form = FormKategoriItem(instance=kategori_item)

    message = form.errors
    context = {
        'form': form,
        'data': kategori_item,
        'segment': 'kategori-item',
        'crud': 'update',
        'message': message,
        'role': request.user.role,
    }
    return render(request, 'home/kat_item_view.html', context)


# Delete Kategori Item
@login_required(login_url='/login/')
@role_required(allowed_roles=['Admin'])
def kategori_item_delete(request, _id):
    kategori_item = KategoriItem.objects.get(id=_id)
    kategori_item.delete()
    return HttpResponseRedirect(reverse('kat-item-index'))


@login_required(login_url='/login/')
def icon(request):
    return render(request, 'home/icons.html')


@login_required(login_url='/login/')
def profile(request):
    return render(request, 'home/profile.html')


@login_required(login_url='/login/')
def table(request):
    return render(request, 'home/tables.html')
