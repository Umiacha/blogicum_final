from django.urls import path, include

from . import views

app_name = 'users'

urlpatterns = [
    path(
        'profile/edit/',
        views.UserUpdateView.as_view(),
        name='edit_profile'
    ),
    path(
        'profile/<slug:username>/',
        views.UserDetailView.as_view(),
        name='profile'
    ),
]
