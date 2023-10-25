from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse
from apps.models import Auth


def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                role = Auth.objects.filter(
                    user_id=request.user.user_id).values_list('menu_id', flat=True)

                if allowed_roles not in role and request.user.is_superuser == False:
                    # Change 'forbidden_view' to the name of the view that handles forbidden access
                    return redirect(reverse('forbidden-view'))

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator
