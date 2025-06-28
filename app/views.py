from django.shortcuts import render, redirect, get_object_or_404
import requests
import string
import json
import os
import random
from django.http import HttpResponse
from django.http import JsonResponse
from django.contrib.auth import views as auth_views         
from django.contrib.auth.forms import UserCreationForm      
from django.contrib.auth.models import User                 
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required                        
from .models import BMILog, BMRLog
from .forms import AvatarUpdateForm
from .models import UserProfile
from django.core.paginator import Paginator
from .models import FavoriteRecipe
from django.views.decorators.http import require_POST
from .models import Article
from .forms import ArticleForm
from django.utils.text import slugify
from django.contrib import messages
from django.utils.crypto import get_random_string
from .models import SavedArticle
from django.core.mail import send_mail
from .forms import NewsletterForm


# Create your views here.

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
        
    return render(request, 'app/register.html', {'form': form})

@login_required
def profile(request):
    bmi_logs = BMILog.objects.filter(user=request.user).order_by('created_at')[:5]
    bmr_logs = BMRLog.objects.filter(user=request.user).order_by('created_at')[:5]
    return render(request, 'app/profile.html', {
        'bmi_logs': bmi_logs,
        'bmr_logs': bmr_logs
    })


def home(request):
    return render(request, 'app/home.html')

def bmi_calculator(request):
    bmi = None
    category = None
    suggested_meals = []

    if request.method == 'POST':
        weight = float(request.POST['weight'])
        height_cm = float(request.POST['height'])
        height_m = height_cm / 100
        bmi = round(weight / (height_m ** 2), 2)

        if bmi <= 18.5:
            category = "Underweight"
            suggested_meals = get_suggested_meals(bmi)
        elif bmi < 25:
            category = "Normal"
            suggested_meals = get_suggested_meals(bmi)
        elif bmi < 30:
            category = "Overweight"
            suggested_meals = get_suggested_meals(bmi)
        else:
            category = "Obese"
            suggested_meals = get_suggested_meals(bmi)

        BMILog.objects.create(
            user=request.user,
            weight=weight,
            height=height_cm,
            bmi_value=bmi,
            category=category
        )

    return render(request, 'app/bmi.html', {
        'bmi': bmi,
        'category': category,
        'suggested_meals': suggested_meals,
    })

def bmr_calculator(request):
    bmr = None
    suggested_meals = []

    if request.method == 'POST':
        weight = float(request.POST.get('weight'))
        height = float(request.POST.get('height'))
        age = int(request.POST.get('age'))
        gender = request.POST.get('gender')

        if gender == 'male':
            bmr = round(10 * weight + 6.25 * height - 5 * age + 5, 2)
        elif gender == 'female':
            bmr = round(10 * weight + 6.25 * height - 5 * age - 161, 2)

        # Save the BMR log to the database
        BMRLog.objects.create(
            user=request.user,
            gender=gender,
            weight=weight,
            height=height,
            age=age,
            bmr_value=bmr
        )

        suggested_meals = get_suggested_meals_by_bmr(bmr)

    return render(request, 'app/bmr.html', {
        'bmr': bmr,
        'suggested_meals': suggested_meals
    })

def food_lookup(request):
    query = request.GET.get('q')
    results = []

    if query:
        api_key = "MoRhxfYGwSTkKuF4FZgIkSShq9xyq83V8PmjchLz"  
        url = "https://api.nal.usda.gov/fdc/v1/foods/search"
        params = {
            "query": query,
            "api_key": api_key,
            "pageSize": 2
        }

        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            for food in data.get('foods', []):
                nutrients = food.get('foodNutrients', [])
                
                def get_nutrient(keyword):
                    for n in nutrients:
                        if keyword.lower() in n['nutrientName'].lower():
                            value = n.get('value', 0)
                            unit = n.get('unitName', '')
                            return f"{value} {unit}"
                    return "N/A"


                results.append({
                    'description': food.get('description', 'N/A'),
                    'energy': get_nutrient("Energy"),
                    'protein': get_nutrient("Protein"),
                    'carbs': get_nutrient("Carbohydrate, by difference"),
                    'fat': get_nutrient("Total lipid (fat)"),
                    'water': get_nutrient("Water"),
                    'ash': get_nutrient("Ash"),
                    'calcium': get_nutrient("Calcium, Ca"),
                    'iron': get_nutrient("Iron, Fe"),
                    'magnesium': get_nutrient("Magnesium, Mg"),
                    'phosphorus': get_nutrient("Phosphorus, P"),
                    'potassium': get_nutrient("Potassium, K"),
                    'sodium': get_nutrient("Sodium, Na"),
                    'zinc': get_nutrient("Zinc, Zn"),
                    'copper': get_nutrient("Copper, Cu"),
                    'manganese': get_nutrient("Manganese, Mn"),
                    'cholesterol': get_nutrient("Cholesterol"),
                })

    return render(request, 'app/food_lookup.html', {'results': results})

@login_required
def update_avatar(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = AvatarUpdateForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = AvatarUpdateForm(instance=profile)

    return render(request, 'app/update_avatar.html', {'form': form})
        

def recipes(request):
    category = request.GET.get('category')
    area = request.GET.get('area')
    tag = request.GET.get('tag')
    search = request.GET.get('search')
    page_number = request.GET.get('page', 1)

    with open('cached_meals.json', 'r', encoding='utf-8') as f:
        all_meals = json.load(f)

    meals = all_meals.copy()

    if category:
        meals = [meal for meal in meals if meal.get('strCategory') == category]

    if area:
        meals = [meal for meal in meals if meal.get('strArea') == area]

    if tag:
        meals = [meal for meal in meals if meal.get('strTags') and tag.lower() in meal.get('strTags', '').lower()]

    if search:
        meals = [meal for meal in meals if search.lower() in meal.get('strMeal', '').lower()]

    paginator = Paginator(meals, 8)
    page_obj = paginator.get_page(page_number)

    categories = sorted(set(m.get('strCategory') for m in all_meals if m.get('strCategory')))
    areas = sorted(set(m.get('strArea') for m in all_meals if m.get('strArea')))
    all_tags = set()
    for m in all_meals:
        tags_str = m.get('strTags')
        if tags_str:
            for t in tags_str.split(','):
                all_tags.add(t.strip())
    tags = sorted(all_tags)

    favorite_ids = []
    if request.user.is_authenticated:
        favorite_ids =FavoriteRecipe.objects.filter(user=request.user).values_list('meal_id', flat=True)


    return render(request, 'app/recipes.html', {
        'page_obj': page_obj,
        'categories': categories,
        'areas': areas,
        'tags': tags,
        'category': category,
        'area': area,
        'tag': tag,
        'search': search,
        'favorite_ids': favorite_ids,
    })
    



@login_required
@require_POST
def toggle_favorite(request):
    if request.method == 'POST':
        meal_id = request.POST.get('meal_id')
        meal_name = request.POST.get('meal_name')
        meal_thumb = request.POST.get('meal_thumb')

        favorite, created = FavoriteRecipe.objects.get_or_create(
            user=request.user,
            meal_id=meal_id,
            defaults={'meal_name': meal_name, 'meal_thumb': meal_thumb}
        )

        if not created:
            favorite.delete()
            return JsonResponse({'status': 'removed'})
        return JsonResponse({'status': 'added'})

    return JsonResponse({'error': 'Invalid request'}, status=400)


def recipe_detail(request, meal_id):
    url = f'https://www.themealdb.com/api/json/v1/1/lookup.php?i={meal_id}'
    response = requests.get(url)
    data = response.json()
    meal = data['meals'][0] if data['meals'] else None
    ingredients = []
    is_favorite = False

    if meal:
        for i in range(1, 21):
            ingredient = meal.get(f'strIngredient{i}')
            measure = meal.get(f'strMeasure{i}')
            if ingredient and ingredient.strip():
                ingredients.append({'ingredient': ingredient.strip(), 'measure': measure.strip() if measure else ''})
        if request.user.is_authenticated:
            is_favorite = FavoriteRecipe.objects.filter(user=request.user, meal_id=meal_id).exists()

    return render(request, 'app/recipe_detail.html', {
        'meal': meal,
        'ingredients': ingredients,
        'is_favorite': is_favorite,
    })

@login_required
def favorite_recipes(request):
    favorites = FavoriteRecipe.objects.filter(user=request.user)
    return render(request, 'app/favorite_recipes.html', {'favorites': favorites})


def about(request):
    return render(request, 'app/about.html')

def articles_list(request):
    category = request.GET.get('category')
    if category:
        articles = Article.objects.filter(is_approved=True, category=category).order_by('-created_at')
    else:
        articles = Article.objects.filter(is_approved=True).order_by('-created_at')
    categories = Article._meta.get_field('category').choices
    saved_ids = []
    if request.user.is_authenticated:
        saved_ids = list(SavedArticle.objects.filter(user=request.user).values_list('article_id', flat=True))

    return render(request, 'app/articles.html', {
        'articles': articles, 
        'categories': categories,
        'current_category': category,
        'saved_ids': saved_ids,
        })


def article_detail(request, slug):
    article = get_object_or_404(Article, slug=slug, is_approved=True)
    is_saved = False
    if request.user.is_authenticated:
        is_saved = SavedArticle.objects.filter(user=request.user, article=article).exists()

    return render(request, 'app/article_detail.html', {
        'article': article,
        'is_saved': is_saved
        })

@login_required
def submit_article(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            base_slug = slugify(article.title)
            slug = base_slug
            count = 1
            while Article.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{get_random_string(4)}"
            article.slug = slug
            article.save()
            messages.success(request, "Your article has been submitted successfully and is pending approval!")
            return redirect('articles_list')
    else:
        form = ArticleForm()
    return render(request, 'app/submit_article.html', {'form': form})



@login_required
def save_article(request, article_id):
    article= get_object_or_404(Article, pk=article_id, is_approved=True)
    SavedArticle.objects.create(user=request.user, article=article)
    messages.success(request, "Article saved successfully!")
    return redirect(request.META.get('HTTP_REFERER', 'articles_list'))

@login_required
def unsave_article(request, article_id):
    article = get_object_or_404(Article, pk=article_id)
    SavedArticle.objects.filter(user=request.user, article=article).delete()
    messages.success(request, "Article removed from saved list!")
    return redirect(request.META.get('HTTP_REFERER', 'articles_list'))

@login_required
def saved_articles(request):
    saved = SavedArticle.objects.filter(user=request.user).select_related('article').order_by('-saved_at')
    return render(request, 'app/saved_articles.html', {'saved_articles': saved})

def careers(request):
    return render(request, 'app/careers.html')

def terms_of_service(request):
    return render(request, 'app/terms_of_service.html')

def faqs(request):
    return render(request, 'app/faqs.html')

def contact_us(request):
    return render(request, 'app/contact_us.html')

def privacy_policy(request):
    return render(request, 'app/privacy_policy.html')

def subscribe_newsletter(request):
    if request.method == 'POST':
        form = NewsletterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']

            send_mail(
                subject='Thanks for subcribing!',
                message='You have been subscribed to NutriHealth newsletter!',
                from_email='hieu.haminh2255@gmail.com',
                recipient_list=[email],
                fail_silently=False,
            )

            messages.success(request, 'Subscription successful. Please check your inbox!')
            return redirect('home')
    return redirect('home')

def get_user_bmi_category(bmi):
    if bmi < 18.5:
        return 'Underweight'
    elif 18.5 <= bmi < 25:
        return 'Normal'
    elif 25 <= bmi < 30:
        return 'Overweight'
    else:
        return 'Obese'
    

def get_suggested_meals(bmi):
    with open('cached_meals.json', 'r') as f:
        data = json.load(f)

    def filter_meals(tags):
        return [m for m in data if any(tag.lower() in (m.get('strTags') or '').lower() for tag in tags)]

    if bmi < 18.5:
        meals = filter_meals(['Beef', 'Pasta', 'Egg', 'Lamb', 'Pork'])
    elif bmi < 25:
        meals = filter_meals(['Balanced', 'Chicken', 'Fish', 'Healthy', 'Main', 'Rice', 'Seafood'])
    elif bmi < 30:
        meals = filter_meals(['Salad', 'Vegetarian', 'Vegetable', 'Light', 'Low Calorie'])
    else:
        meals = filter_meals(['Vegan', 'Low fat', 'Vegetable', 'Salad', 'Healthy'])

    if not meals:
        meals = random.sample(data, 4)
    return meals[:4]


@login_required
def suggested_meals_view(request):
    user_profile = request.user.profile
    latest_bmi = user_profile.latest_bmi
    meals = get_suggested_meals(latest_bmi)
    return render(request, 'suggested_meals.html', {'meals': meals})

def get_suggested_meals_by_bmr(bmr):
    with open('cached_meals.json', 'r') as f:
        data = json.load(f)

    def filter_meals(tags):
        return [m for m in data if any(tag.lower() in (m.get('strTags') or '').lower() for tag in tags)]
    
    if bmr < 1400:
        meals = filter_meals(['Beef', 'Pasta', 'Egg', 'Lamb', 'Pork', 'Rice'])
    elif bmr < 1800:
        meals = filter_meals(['Balanced', 'Chicken', 'Fish', 'Healthy', 'Main', 'Seafood'])
    else:
        meals = filter_meals(['Protein', 'High Protein', 'Steak', 'Chicken', 'Fish', 'Egg', 'Seafood'])

    if not meals:
        meals = random.sample(data, 4)
    return meals[:4]