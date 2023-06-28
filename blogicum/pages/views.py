from django.shortcuts import render
from django.views.generic import TemplateView



class About(TemplateView):
    template_name = 'pages/about.html'


class Rules(TemplateView):
    template_name = 'pages/rules.html'


def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)


def not_corresponding(request):
    return render(request, 'pages/500.html', status=500)


def csrf_failure(
    request, reason='csrf error', template_name='pages/403csrf.html'
):
    return render(request, )
