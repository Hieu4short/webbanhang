from django import forms
from .models import UserProfile
from .models import Article
from ckeditor.widgets import CKEditorWidget

class AvatarUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['avatar']


class ArticleForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())
    class Meta:
        model = Article
        fields = ['title', 'content', 'category', 'image']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }