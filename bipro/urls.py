"""
URL configuration for bipro project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from .views import index, login, logout, signup, signup_successfully
from django.conf.urls.static import static
from django.conf import settings
from ads.views import OrderListView
from django.views.i18n import JavaScriptCatalog

admin.site.site_header = settings.ADMIN_SITE_HEADER

urlpatterns = [
    path('admin/', admin.site.urls),
    path('index', index),
    path('', OrderListView.as_view()),
    path('login', login, name='login'),
    path('logout', logout, name='login'),
    path("signup", signup, name="signup"),
    path("signup_successfully", signup_successfully, name="signup_successfully"),
    path('ads/', include('ads.urls')),

    path('jsi18n/', JavaScriptCatalog.as_view(), name='javascript-catalog'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
