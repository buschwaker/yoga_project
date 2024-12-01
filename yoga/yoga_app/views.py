from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render

from yoga_app.constants import BASE
from yoga_users.constants import TRAINEE
from yoga_app.models import Training


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
    base_trainings = Training.objects.filter(type=BASE)
    if not request.user.is_authenticated:
        return render(request, 'yoga/main.html', context={"base_trainings": base_trainings})


@role_required(TRAINEE)
def get_trainings(request):
    user = request.user
    trainings = user.trainings.all()
    context = {
        "trainings": trainings,

    }
    return render(request, 'yoga/trainings.html', context)
