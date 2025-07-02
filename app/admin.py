from django.contrib import admin
from .models import Article
from .models import Comment
admin.site.register(Comment)
# Register your models here.

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'is_approved', 'created_at')
    list_filter = ('category', 'is_approved', 'author')
    search_fields = ('title', 'content')
    list_editable = ('is_approved',)
    prepopulated_fields = {'slug': ('title',)}