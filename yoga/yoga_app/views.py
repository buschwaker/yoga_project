from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from yoga_app.models import User


@login_required
def index(request):
    users = User.objects.all()
    context = {
        "users": [user.username for user in users],

    }
    return render(request, 'yoga/main.html', context)
