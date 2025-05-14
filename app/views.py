from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def home(request):
    return render(request, 'app/home.html')

def bmi_calculator(request):
    return render(request, 'app/bmi.html')

def bmr_calculator(request):
    return render(request, 'app/bmr.html')
