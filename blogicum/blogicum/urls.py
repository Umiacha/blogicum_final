from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static
from django.urls import path, include

from users.views import AuthUserCreateView

urlpatterns = [
    path('', include('blog.urls', namespace='blog')),
    path('', include('users.urls', namespace='users')),
    path('pages/', include('pages.urls', namespace='pages')),
    path('admin/', admin.site.urls),
    path('auth/', include('django.contrib.auth.urls')),
    path(
        'auth/registration/',
        AuthUserCreateView.as_view(),
        name='registration'
    ),
]
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.not_corresponding'
