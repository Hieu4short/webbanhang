from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('tools/bmi/', views.bmi_calculator, name='bmi'), 
    path('admin/', admin.site.urls),
    path('tools/bmr/', views.bmr_calculator, name='bmr'),
    path('tools/food-lookup/', views.food_lookup, name='food_lookup'),
]
