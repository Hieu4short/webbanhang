from django import forms
from .models import UserProfile

class AvatarUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar']