from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import BaseListView
from django.views.generic import DetailView, UpdateView

from blogicum.settings import NUMBER_OF_POSTS_ON_MAINPAGE
from .forms import AuthUserCreationForm, AuthUserUpdateForm
from blog.models import Post

User = get_user_model()


class AuthUserCreateView(CreateView):
    template_name = 'registration/registration_form.html'
    form_class = AuthUserCreationForm
    success_url = reverse_lazy('blog:index')


class UserDetailView(DetailView, BaseListView):
    template_name = 'users/profile.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    paginate_by = NUMBER_OF_POSTS_ON_MAINPAGE

    def get_queryset(self):
        return User.objects.all()

    def get_context_data(self, **kwargs):
        self.object_list = Post.objects.filter(
            author=User.objects.get(
                username=self.kwargs['username']
            )
        )
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['profile'] = self.get_object(self.get_queryset())
        return context


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'users/user.html'
    form_class = AuthUserUpdateForm
    object = None

    def dispatch(self, request, *args, **kwargs):
        self.kwargs[self.pk_url_kwarg] = self.request.user.id
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method.lower() == 'get':
            context['form'] = self.form_class(instance=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, instance=self.request.user)
        if form.is_valid():
            return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'users:profile',
            kwargs={'username': self.object.username}
        )
