from django.contrib import admin
from .models import Post, Comment

# регистрируем декодируемый класс - наследник Model.Admin
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    '''
    list_display - поля, которые хотим видеть в на странице в админке
    list_filter - блок справа, фильтрация списка по полям
    search_fields - строка поиска по полям
    prepopulated_fields - генерация slug из поля title
    raw_id_fields -
    '''
    list_display = ('title', 'slug', 'author', 'publish','status')
    list_filter = ('status', 'created', 'publish', 'author')
    search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'publish'
    ordering = ('status', 'publish')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'post', 'created', 'active')
    list_filter = ('active', 'created', 'updated')
    search_fields = ('name', 'email', 'body')
# Register your models here.
