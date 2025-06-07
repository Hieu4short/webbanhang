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
    path('update_avatar/', views.update_avatar, name="update_avatar"),
    path('recipes/', views.recipes, name='recipes'),
    path('favorites/', views.favorite_recipes, name='favorite_recipes'),
    path('toggle_favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('recipes/<str:meal_id>/', views.recipe_detail, name='recipe_detail'),
    path('about/', views.about, name='about'),
    path('articles/', views.articles_list, name='articles_list'),
    path('articles/<slug:slug>/', views.article_detail, name='article_detail'),
    path('submit-article/', views.submit_article, name='submit_article'),
    path('saved-article/<int:article_id>', views.save_article, name='save_article'),
    path('unsaved-article/<int:article_id>', views.unsave_article, name='unsave_article'),
    path('saved-articles/', views.saved_articles, name='saved_articles'),
    path('careers/', views.careers, name='careers'),
    path('terms/', views.terms_of_service, name='terms_of_service'),
    path('faqs/', views.faqs, name='faqs'),
    path('contact/', views.contact_us, name='contact_us'),
    path('privacy/', views.privacy_policy, name='privacy_policy'),
    path('subscribe/', views.subscribe_newsletter, name='subscribe_newsletter'),
]
