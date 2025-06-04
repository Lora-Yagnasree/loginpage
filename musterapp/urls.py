# urls.py
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views  


urlpatterns = [
    path('', views.CustomLoginView.as_view(), name='login'),
    path('employee/dashboard/', views.employee_dashboard, name='employee_dashboard'),
    path('manager/dashboard/', views.manager_dashboard, name='manager_dashboard'),
    path('clock-in/', views.clock_in, name='clock_in'),
    path('clock-out/', views.clock_out, name='clock_out'),
    path('reset_password/', views.reset_password, name='reset_password'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),


]
