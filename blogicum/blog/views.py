from django.shortcuts import render, get_object_or_404
from django.db.models.functions import Now

from .models import Post, Category

NUMBER_OF_POSTS_ON_MAINPAGE = 5
# А можете ли вы что-то сказать по улучшению кода?
# Или при текущих требованиях к проекту всё оптимально?

# И спасибо за вашу работу!


def index(request):
    post_list = Post.objects.all(
    ).select_related(
        'author', 'category', 'location'
    ).filter(
        pub_date__lte=Now(),
        is_published=True,
        category__is_published=True
    ).order_by('-pub_date')[:NUMBER_OF_POSTS_ON_MAINPAGE]
    context = {'post_list': post_list}
    return render(request, 'blog/index.html', context)


def post_detail(request, post_pk):
    post = get_object_or_404(
        Post.objects.select_related(
            'author', 'category', 'location'
        ).filter(
            pub_date__lte=Now(),
            is_published=True,
            category__is_published=True
        ),
        pk=post_pk
    )
    context = {
        'post': post,
    }
    return render(request, 'blog/detail.html', context)


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category.objects.filter(is_published=True),
        slug=category_slug
    )
    post_list = Post.objects.all(
    ).select_related(
        'author', 'category', 'location'
    ).filter(
        pub_date__lte=Now(),
        is_published=True,
        category__slug=category_slug
    ).order_by('-pub_date')
    context = {
        'category': category,
        'post_list': post_list,
    }
    return render(request, 'blog/category.html', context)
