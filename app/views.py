from django.shortcuts import render
import requests
from django.http import HttpResponse

# Create your views here.
def home(request):
    return render(request, 'app/home.html')

def bmi_calculator(request):
    return render(request, 'app/bmi.html')

def bmr_calculator(request):
    return render(request, 'app/bmr.html')

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

