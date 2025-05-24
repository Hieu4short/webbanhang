from django.shortcuts import render, redirect
import requests
from django.http import HttpResponse
from django.contrib.auth import views as auth_views         
from django.contrib.auth.forms import UserCreationForm      
from django.contrib.auth.models import User                 
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required                        
from .models import BMILog, BMRLog
from .forms import AvatarUpdateForm
from .models import UserProfile


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
        