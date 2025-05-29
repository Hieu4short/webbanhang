from django.shortcuts import render, redirect
import requests
import string
import json
import os
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

    if request.method == 'POST':
        weight = float(request.POST['weight'])
        height_cm = float(request.POST['height'])
        height_m = height_cm / 100
        bmi = round(weight / (height_m ** 2), 2)

        if bmi <= 18.5:
            category = "Underweight"
        elif bmi < 25:
            category = "Normal"
        elif bmi < 30:
            category = "Overweight"
        else:
            category = "Obese"

        BMILog.objects.create(
            user=request.user,
            weight=weight,
            height=height_cm,
            bmi_value=bmi,
            category=category
        )

    return render(request, 'app/bmi.html', {
        'bmi': bmi,
        'category': category
    })

def bmr_calculator(request):
    bmr = None

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

    return render(request, 'app/bmr.html', {
        'bmr': bmr
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
    page_number = request.GET.get('page', 1)
    
    try:
        with open('cached_meals.json', 'r', encoding='utf-8') as f:
            meals = json.load(f)
    except FileNotFoundError:
        meals = []


    if category:
        meals = [meal for meal in meals if meal.get('strCategory') == category]

    paginator = Paginator(meals, 8)
    page_obj = paginator.get_page(page_number)

    favorite_ids = []
    if request.user.is_authenticated:
        favorite_ids = FavoriteRecipe.objects.filter(user=request.user).values_list('meal_id', flat=True)

    cat_response = requests.get('https://www.themealdb.com/api/json/v1/1/list.php?c=list')
    categories = cat_response.json().get('meals', []) 

    return render(request, 'app/recipes.html', {
        'page_obj': page_obj,
        'category': category,
        'favorite_ids': favorite_ids,
        'categories': categories,
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