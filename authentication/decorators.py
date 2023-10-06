from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse


def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated:
                role = request.user.position_id

                if role not in allowed_roles and request.user.is_superuser == False:
                    return redirect(reverse('forbidden-view'))  # Change 'forbidden_view' to the name of the view that handles forbidden access

            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator
