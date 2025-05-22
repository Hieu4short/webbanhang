from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class BMILog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    weight = models.FloatField()
    height = models.FloatField()
    bmi_value = models.FloatField()
    category = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

class BMRLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    weight = models.FloatField()
    height = models.FloatField()
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    bmr_value = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

