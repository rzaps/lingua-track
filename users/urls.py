from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth import views as auth_views
from .forms import EmailAuthenticationForm

app_name = 'users'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('telegram-link/', views.telegram_link, name='telegram_link'),

    # --- AUTH: сброс пароля ---
    path('password_reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset_form.html',
             success_url=reverse_lazy('users:password_reset_done'),
             email_template_name='registration/password_reset_email.html'
         ),
         name='password_reset'),
    
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ),
         name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html',
             success_url=reverse_lazy('users:password_reset_complete')
         ),
         name='password_reset_confirm'),
    
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ),
         name='password_reset_complete'),
    
    path('login/', 
         auth_views.LoginView.as_view(
             template_name='registration/login.html',
             authentication_form=EmailAuthenticationForm
         ),
         name='login'),
    
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
] 