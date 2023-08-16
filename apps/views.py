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
def icon(request):
    return render(request, 'home/icons.html')


@login_required(login_url='/login/')
def profile(request):
    return render(request, 'home/profile.html')


@login_required(login_url='/login/')
def table(request):
    return render(request, 'home/tables.html')
