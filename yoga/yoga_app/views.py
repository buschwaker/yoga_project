from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render

from yoga_app.constants import BASE
from yoga_users.constants import TRAINEE, COACH
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
    context = {"base_trainings": base_trainings}
    if not request.user.is_authenticated:
        context = context
    elif request.user.role == COACH:
        trainees = request.user.trainees.all()
        context = {"trainees": trainees, "COACH": True}
    elif request.user.role == TRAINEE:
        personal_trainings = Training.objects.filter(request__trainee_id=request.user.id)
        context.update({"personal_trainings": personal_trainings, "TRAINEE": True})
    return render(request, 'yoga/main.html', context=context)

@role_required(TRAINEE)
def get_trainings(request):
    user = request.user
    trainings = user.trainings.all()
    context = {
        "trainings": trainings,

    }
    return render(request, 'yoga/trainings.html', context)
