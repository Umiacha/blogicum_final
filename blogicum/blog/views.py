from typing import Any, Dict

from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.functions import Now
from django.views.generic import (
    DetailView, TemplateView, CreateView, UpdateView, DeleteView,
)
from django.views.generic.list import BaseListView
from django.core.exceptions import PermissionDenied

from .models import Post, Category, Comment
from .forms import PostForm, CommentForm, UserForm

NUMBER_OF_POSTS_ON_MAINPAGE = 10

User = get_user_model()


class Homepage(BaseListView, TemplateView):
    template_name = 'blog/index.html'
    paginate_by = NUMBER_OF_POSTS_ON_MAINPAGE
    ordering = '-pub_date'
    queryset = Post.objects.all().filter(
        pub_date__lte=Now(),
        is_published=True,
        category__is_published=True
    )


class CategoryDetailView(DetailView, BaseListView):
    model = Category
    template_name = 'blog/category.html'
    paginate_by = NUMBER_OF_POSTS_ON_MAINPAGE
    # ordering = '-pub_date'
    slug_url_kwarg = 'category_slug'

    def dispatch(self, request, *args, **kwargs):
        self.category = get_object_or_404(
            self.model,
            slug=kwargs['category_slug'],
            is_published=True
        )
        self.object_list = self.category.post_category.select_related(
            'author', 'category', 'location'
        ).filter(
            pub_date__lte=Now(),
            is_published=True,
            category__is_published=True
        ).order_by('-pub_date')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        return context


class UserDetailView(DetailView, BaseListView):
    model = User
    template_name = 'blog/profile.html'
    slug_field = 'username'
    slug_url_kwarg = 'username'
    paginate_by = NUMBER_OF_POSTS_ON_MAINPAGE
    profile = None
    object_list = None

    def dispatch(self, request, *args, **kwargs):
        self.object_list = Post.objects.filter(
            author=User.objects.get(
                username=kwargs['username']
            )
        ).order_by('-pub_date',)
        self.profile = get_object_or_404(User, username=kwargs['username'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(
            object_list=self.object_list, **kwargs
        )
        context['user'] = self.request.user
        context['profile'] = self.profile
        return context


class UserUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    form_class = UserForm
    object = None

    def get_object(self, queryset=None):
        return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method.lower() == 'get':
            context['form'] = self.form_class(instance=self.request.user)
        return context

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST, instance=self.request.user)
        if form.is_valid():
            return super().form_valid(form)
        else:
            return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        # form = self.form_class(self.request.POST)
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def dispatch(self, request, *args, **kwargs):
        self.instance = get_object_or_404(Post, pk=kwargs['post_id'])
        if self.instance.author != request.user:
            return redirect('blog:post_detail', post_id=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'
    pk_url_kwarg = 'post_id'
    extra_context = {'form': CommentForm()}

    def dispatch(self, request, *args, **kwargs):
        self.post = get_object_or_404(
            Post.objects.select_related(
                'author', 'category', 'location'
            ).filter(
                pub_date__lte=Now(),
                is_published=True,
                category__is_published=True
            ),
            pk=self.kwargs['post_id']
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.commentpost.select_related('author')
        return context


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    pk_url_kwarg = 'post_id'
    template_name = 'blog/create.html'
    form_class = PostForm

    def dispatch(self, request, *args, **kwargs):
        self.instance = get_object_or_404(self.model, pk=kwargs['post_id'])
        if self.instance.author != request.user:
            return redirect('blog:post_detail', post_id=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class(instance=self.instance)
        return context

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    template_name = 'includes/comments.html'
    form_class = CommentForm
    pk_url_kwarg = 'post_id'
    post_object = None

    def dispatch(self, request, *args, **kwargs):
        self.post_object = get_object_or_404(Post, pk=kwargs['post_id'])
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = self.post_object
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.post_object.pk}
        )


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(
            Comment,
            pk=kwargs['comment_id']
        )
        if instance.author != self.request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )


class CommentDeleteView(DeleteView):
    model = Comment
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'comment_id'

    def dispatch(self, request, *args, **kwargs):
        instance = get_object_or_404(
            Comment,
            pk=kwargs['comment_id']
        )
        if instance.author != self.request.user:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self) -> str:
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.kwargs['post_id']}
        )
