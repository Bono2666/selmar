from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render
from .forms import LoginForm


def login_view(request):
    form = LoginForm(request.POST or None)

    msg = None

    if request.method == "POST":

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                msg = 'User/Password tidak valid'
        else:
            msg = 'Kesalahan validasi'

    return render(request, "accounts/login.html", {"form": form, "msg": msg})


def forbidden_view(request):
    return render(request, "home/forbidden.html")
