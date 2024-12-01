from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseForbidden
from django.shortcuts import render

from yoga_app.models import User
from yoga_users.constants import TRAINEE


def role_required(role):
    def decorator(view_func):
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if request.user.role != role:
                return HttpResponseForbidden("You do not have permission to view this page")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def index(request):
    if not request.user.is_authenticated:
        # base_trainings = Training.objects.filter(type='BASE')
        return render(request, 'yoga/main.html')
    # users = User.objects.all()
    # context = {
    #     "users": [user.username for user in users],
    #
    # }


@role_required(TRAINEE)
def get_trainings(request):
    user = request.user
    trainings = user.trainings.all()
    context = {
        "trainings": trainings,

    }
    return render(request, 'yoga/trainings.html', context)
