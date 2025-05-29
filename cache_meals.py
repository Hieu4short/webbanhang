import requests
import json
import os

def fetch_and_cache_meals():
    all_meals = []

    for c in 'abcdefghijklmnopqrstuvwxyz':
        url = f'https://www.themealdb.com/api/json/v1/1/search.php?f={c}'
        response = requests.get(url)
        data = response.json()
        meals = data.get('meals')
        if meals:
            all_meals.extend(meals)

    with open('cached_meals.json', 'w', encoding='utf-8') as f:
        json.dump(all_meals, f, ensure_ascii=False, indent=2)

    print(f"✅ Cached {len(all_meals)} meals successfully.")

if __name__ == '__main__':
    fetch_and_cache_meals() 