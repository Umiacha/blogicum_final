from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models.functions import Now
from django.views.generic import (
    DetailView, TemplateView, CreateView, UpdateView,
)
from django.views.generic.list import BaseListView
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist

from .models import Post, Category, Comment
from .forms import PostForm, CommentForm

User = get_user_model()


class Homepage(BaseListView, TemplateView):
    template_name = 'blog/index.html'
    paginate_by = settings.NUMBER_OF_POSTS_ON_MAINPAGE
    ordering = '-pub_date'
    queryset = Post.objects.filter(
        pub_date__lte=Now(),
        is_published=True,
        category__is_published=True
    )


class CategoryDetailView(DetailView, BaseListView):
    template_name = 'blog/category.html'
    paginate_by = settings.NUMBER_OF_POSTS_ON_MAINPAGE
    slug_url_kwarg = 'category_slug'

    def get_queryset(self):
        return self.object.posts.select_related(
            'author', 'category', 'location'
        ).filter(
            pub_date__lte=Now(),
            is_published=True,
            category__is_published=True,
        )

    def get_object(self, queryset=None):
        return get_object_or_404(
            Category,
            slug=self.kwargs['category_slug'],
            is_published=True
        )

    def get_context_data(self, **kwargs):
        self.object_list = self.get_queryset()
        context = super().get_context_data(**kwargs)
        context['category'] = self.get_object()
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self) -> str:
        return reverse_lazy(
            'users:profile',
            kwargs={'username': self.request.user.username}
        )


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def post(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except ObjectDoesNotExist:
            return redirect('blog:post_detail', post_id=kwargs['post_id'])
        return super().post(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        try:
            self.object = self.get_object()
        except ObjectDoesNotExist:
            return redirect('blog:post_detail', post_id=kwargs['post_id'])
        return self.render_to_response(self.get_context_data())

    def get_object(self, queryset=None):
        instance = get_object_or_404(Post, pk=self.kwargs['post_id'])
        if instance.author != self.request.user:
            raise ObjectDoesNotExist
        return instance

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

    def get_object(self, queryset=None):
        instance = get_object_or_404(
            self.model,
            pk=self.kwargs['post_id']
        )
        queryset = self.model.objects.select_related(
            'author', 'category', 'location'
        )
        if self.request.user != instance.author:
            queryset = queryset.filter(
                pub_date__lte=Now(),
                is_published=True,
                category__is_published=True
            )
        return get_object_or_404(
            queryset,
            pk=self.kwargs['post_id']
        )

    def get_context_data(self, **kwargs):
        context = {'post': self.get_object()}
        context['comments'] = context['post'].comments.select_related('author')
        context.update(**self.extra_context)
        return context


def post_delete(request, post_id):
    context = {}
    instance = get_object_or_404(Post, pk=post_id)
    if instance.author != request.user:
        return redirect('blog:post_detail', post_id=post_id)
    if request.method == 'GET':
        context['form'] = PostForm(instance=instance)
        return render(request, 'blog/create.html', context)
    if request.method == 'POST':
        instance.delete()
        return redirect('users:profile', instance.author.username)


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


def comment_delete(request, post_id, comment_id):
    instance = get_object_or_404(
        Comment,
        pk=comment_id
    )
    if instance.author != request.user:
        raise PermissionDenied
    if request.method == 'GET':
        context = {
            'user': request.user,
            'comment': instance,
        }
        return render(request, 'blog/comment.html', context)
    if request.method == 'POST':
        instance.delete()
        return redirect('blog:post_detail', post_id)
