
RESPONSES = {
 "hi": "Hello! I'm NutriHealth Assistant. Ask me about: BMI, weight loss, nutrition or healthy recipes 💚",
    "hello": "Hi there! What health topic can I help you with today?",
    "hey": "Hey! Ready to explore nutrition tips? Fire away your questions!",

    # ============ BMI ============
    "bmi": "BMI = Weight(kg) / (Height(m)^2\nCategories:\n• <18.5: Underweight\n• 18.5-24.9: Healthy\n• 25-29.9: Overweight\n• 30+: Obese",
    "calculate bmi": "To calculate BMI:\n1. Measure height (meters)\n2. Weigh yourself (kg)\n3. Formula: BMI = Weight / (Height × Height)\nExample: 70kg at 1.75m → 70/(1.75×1.75) = 22.9",
    "healthy bmi": "The ideal BMI range is 18.5 to 24.9. For Asians, 23+ may indicate increased risk.",

    # ============ Weight Management ============
    "weight loss": "7 Science-Backed Weight Loss Tips:\n1. Eat 30g protein/meal\n2. Drink water before meals\n3. Walk 10k steps/day\n4. Sleep 7-9 hours\n5. Reduce sugar\n6. Eat fiber-rich foods\n7. Strength train 3x/week",
    "lose belly fat": "Best foods for belly fat loss:\n• Salmon\n• Greek yogurt\n• Avocados\n• Green tea\n• Eggs\n• Berries\nCombine with HIIT workouts 3x/week",
    "weight gain": "Healthy weight gain tips:\n1. Eat 300-500 extra calories/day\n2. Focus on nuts, nut butters\n3. Drink smoothies with protein powder\n4. Strength training\n5. Eat every 3-4 hours",

    # ============ Nutrition ============
    "balanced diet": "Components of balanced diet:\n• 50% Vegetables/Fruits\n• 25% Whole grains\n• 25% Lean proteins\n• Healthy fats (avocado, olive oil)\n• Limit processed foods",
    "protein foods": "Top protein sources:\n1. Chicken breast\n2. Salmon\n3. Eggs\n4. Greek yogurt\n5. Lentils\n6. Tofu\n7. Lean beef",
    "low carb foods": "Best low-carb options:\n• Leafy greens\n• Cauliflower\n• Avocados\n• Berries\n• Nuts/Seeds\n• Fish\n• Eggs\n• Coconut oil",

    # ============ Meal Planning ============
    "healthy breakfast": "Power breakfast ideas:\n• Oatmeal + berries + nuts\n• Greek yogurt + granola\n• Veggie omelet\n• Smoothie: spinach+banana+protein\n• Avocado toast + egg",
    "meal prep": "Meal prep basics:\n1. Cook proteins in bulk\n2. Roast weekly veggies\n3. Portion into containers\n4. Add fresh elements before eating\n5. Keep sauces separate",
    "quick meals": "5-minute healthy meals:\n• Tuna salad wrap\n• Microwave quinoa bowl\n• Cottage cheese + fruit\n• Pre-cooked chicken + salad\n• Protein smoothie",

    # ============ Supplements ============
    "vitamin d": "Vitamin D facts:\n• Best source: Sunlight\n• Foods: Fatty fish, eggs\n• Recommended: 600-800 IU/day\n• Deficiency common in winter",
    "probiotics": "Probiotic benefits:\n• Improve gut health\n• Found in yogurt, kefir\n• May boost immunity\n• Help digest lactose\n• Reduce antibiotic side effects",

    # ============ Special Diets ============
    "keto diet": "Keto basics:\n• <50g carbs/day\n• 70% fats\n• 25% protein\n• 5% carbs\nFoods: Meat, fish, eggs, cheese, low-carb veggies, nuts",
    "vegan protein": "Top plant proteins:\n1. Lentils\n2. Chickpeas\n3. Quinoa\n4. Tofu\n5. Tempeh\n6. Seitan\n7. Pea protein\nCombine sources for complete amino acids",

    # ============ Error Handling ============
    "default": "I'm not sure I understand. Try asking about:\n• BMI calculation\n• Weight loss tips\n• Healthy recipes\n• Nutrition facts\nOr search our knowledge base!"
}

def get_response(user_input):
    user_input = user_input.lower()
    for keyword, answer in RESPONSES.items():
        if keyword in user_input:
            return answer
    return RESPONSES["default"]