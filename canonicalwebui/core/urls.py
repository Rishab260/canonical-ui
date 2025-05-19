from __future__ import annotations

from django.contrib.auth import views as auth_views
from django.urls import path

from . import views
from .forms import CustomAuthenticationForm
from .views import logout_view


app_name = 'core'

urlpatterns = [
    path(
        'login/',
        views.login_and_register,  # Use your combined view here
        name='login',
    ),
    path('', views.landing_page, name='landing_page'),
    path('logout/', logout_view, name='logout'),
    path('submit-app/', views.submit_app, name='submit_app'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('approve-app/<int:app_id>/', views.approve_app, name='approve_app'),
    path(
        'view-app-details/<int:app_id>/',
        views.view_app_details, name='view_app_details',
    ),
    path('app/<int:id>/', views.view_app, name='view_app'),

]
