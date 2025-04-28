from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from yoga_users.forms import CreationForm
from django.shortcuts import render
from django.views.generic import ListView
from .models import User


class CreateUser(CreateView):
    form_class = CreationForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("yoga_users:thankyou")


class ThankYouView(TemplateView):
    template_name = "registration/thankyou.html"


class CoachesListView(ListView):
    model = User
    template_name = 'yoga/coach/coaches_list.html'
    context_object_name = 'coaches'
    paginate_by = 6  # Количество тренеров на странице

    def get_queryset(self):
        return User.objects.filter(role='coach').select_related('info')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            if self.request.user.role == 'coach':
                context['coach'] = True
            elif self.request.user.role == 'trainee':
                context['trainee'] = True
        return context


def coach_profile(request, coach_id):
    coach = get_object_or_404(User, id=coach_id, role='coach')
    return render(request, 'yoga/coach/coach_card.html', {'coach': coach})

