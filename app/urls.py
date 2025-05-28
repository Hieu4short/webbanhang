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
    path('profile/', views.profile, name='profile'),
    path('change_password/', auth_views.PasswordChangeView.as_view(
        template_name='app/change_password.html',
        success_url ='/profile'), name='change_password' 
    ),
    path('recipes/', views.recipes, name='recipes'),
    path('recipes/<int:meal_id>/', views.recipe_detail, name='recipe_detail'),
    path('favorites/', views.favorite_recipes, name='favorite_recipes'),
    path('toggle-favorite/', views.toggle_favorite, name='toggle_favorite'),
]
