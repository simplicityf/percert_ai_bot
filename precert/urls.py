"""
URL configuration for precert project.

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
from django.urls import path
from home import views as home_views

urlpatterns = [
    path('', home_views.HomeAPIView.as_view(), name='home'),
    path('login', home_views.LoginAPIView.as_view(), name='login'),
    path('verify-email', home_views.VerifyOTPAPIView.as_view(), name='verify-email'),
    path('profile', home_views.ProfileAPIView.as_view(), name='profile'),
    path('profile/update', home_views.UpdateProfileAPIView.as_view(), name='update-profile'),
    path('logout', home_views.LogoutAPIView.as_view(), name='logout'),
    path('register', home_views.RegisterAPIView.as_view(), name='register'),
    path('admin/', admin.site.urls),
]
