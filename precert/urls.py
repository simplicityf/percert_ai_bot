from django.contrib import admin
from django.urls import path
from home import views as home_views
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('login', home_views.login_view, name='login'),
    path('register', home_views.register, name='register'),
    path('verify-email', home_views.verify_registration, name='verify_email'),
    path('profile', home_views.profile, name='profile'),
    path('profile/update', home_views.update_profile, name='update_profile'),
    path('profile/verify-email-update', home_views.verify_email_update, name='verify_email_update'),
    path('forgot-password', home_views.forgot_password, name='forgot_password'),
    path('verify-forgot-password', home_views.verify_forgot_password, name='verify_forgot_password'),
    path('change-password', home_views.change_password, name='change_password'),
    path('verify-change-password', home_views.verify_change_password, name='verify_change_password'),
    path('', home_views.home, name='home'),
    path('chat', home_views.chat_view, name='chats'),
    path('logout', home_views.logout_view, name='logout'),
    path('admin/', admin.site.urls),
]
