from django.contrib.auth.decorators import login_required
from django.db import connection
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from apps.forms import *
from apps.models import *


@login_required(login_url='/login/')
def home(request):
    context = {
        'segment': 'index',
    }
    return render(request, 'home/index.html', context)


@login_required(login_url='/login/')
def user_index(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT auth_user.id, username, name FROM auth_user INNER JOIN auth_user_groups "
                       "ON auth_user.id = auth_user_groups.user_id INNER JOIN auth_group "
                       "ON auth_user_groups.group_id = auth_group.id")
        users = cursor.fetchall()

    context = {
        'data': users,
        'segment': 'user',
        'crud': 'index',
    }

    return render(request, 'home/user_index.html', context)


@login_required(login_url='/login/')
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
            }
            return render(request, 'home/user_add.html', context)
    else:
        form = FormUser()
        context = {
            'form': form,
            'segment': 'user',
            'crud': 'add',
        }
        return render(request, 'home/user_add.html', context)


# Update User
@login_required(login_url='/login/')
def user_update(request, _id):
    users = AuthUser.objects.get(id=_id)
    if request.POST:
        form = FormUser(request.POST, request.FILES, instance=users)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('user-index'))
        else:
            message = form.errors
            context = {
                'form': form,
                'data': users,
                'segment': 'user',
                'crud': 'update',
                'message': message,
            }
            return render(request, 'home/user_view.html', context)
    else:
        form = FormUser(instance=users)
        context = {
            'form': form,
            'data': users,
            'segment': 'user',
            'crud': 'update',
        }
        return render(request, 'home/user_view.html', context)


# Delete User
@login_required(login_url='/login/')
def user_delete(request, _id):
    users = AuthUser.objects.get(id=_id)

    users.delete()
    return HttpResponseRedirect(reverse('user-index'))


@login_required(login_url='/login/')
def icon(request):
    return render(request, 'home/icons.html')


@login_required(login_url='/login/')
def profile(request):
    return render(request, 'home/profile.html')


@login_required(login_url='/login/')
def table(request):
    return render(request, 'home/tables.html')
