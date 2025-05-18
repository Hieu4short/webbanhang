from django.contrib import admin
from django.urls import path
from . import views
from django.contrib.auth import views as auth_views



urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='app/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register, name='register'),
    path('', views.home, name='home'),
    path('tools/bmi/', views.bmi_calculator, name='bmi'), 
    path('admin/', admin.site.urls),
    path('tools/bmr/', views.bmr_calculator, name='bmr'),
    path('tools/food-lookup/', views.food_lookup, name='food_lookup'),
]
