from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView

from .forms import CustomUserCreationForm


def about(request):
    template = 'pages/about.html'
    return render(request, template)


def rules(request):
    template = 'pages/rules.html'
    return render(request, template)

def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)

def not_corresponding(request):
    return render(request, 'pages/500.html', status=500)

def csrf_failure(
    request, reason='csrf error', template_name='pages/403csrf.html'
    ):
    return render(request, )


class UserCreateView(CreateView):
    template_name = 'registration/registration_form.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('blog:views')
