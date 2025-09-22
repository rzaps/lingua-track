"""
URL configuration for lingua_track project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.contrib.auth import views as auth_views
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('words.urls', namespace='words')),
    # path('accounts/', include('django.contrib.auth.urls')),  # Отключено, чтобы использовать только свои шаблоны
    path('quiz/', include('quiz.urls', namespace='quiz')),
    path('stats/', include('stats.urls', namespace='stats')),
    path('users/', include('users.urls', namespace='users')),
    path('feedback/', include('feedback.urls', namespace='feedback')),
]
