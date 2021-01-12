from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from taggit.managers import TaggableManager


class PublishedManager(models.Manager):
    '''Новый менеджер для получения всех опубликованных статей'''
    def get_queryset(self):
        '''Возвращает QuerySet для выполнения'''
        return super(PublishedManager, self).get_queryset().filter(status='published')


class Post(models.Model):
    '''поля для таблицы статей'''

    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
    )
    ''' STATUS_CHOICES возможные значения для поля status (статуса статей)'''
    '''
    title - заголовок статьи
    slug - поле для построения urls статей
    author - автор, внешний ключ, соотношение "один ко многим".
    Если удалить автора, удалятся все его стаьи
    body - текст статьи
    publish - поле даты публикация, дата зоны
    created - поле даты создания, дата сохраняется оавтоматически
    updated - дата и время редактирования статьи
    status - поле статуса статьи, мб только STATUS_CHOICES
    '''
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250,unique_for_date='publish')
    author = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='blog_post')
    body = models.TextField()
    publish = models.DateTimeField(default=timezone.now)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES,
                              default='draft')
    objects = models.Manager() # Manager default
    published = PublishedManager() # New my Manager
    tags = TaggableManager()


    class Meta:
        ''' Содержит метаданные + сортировка статей по убыванию даты публикации'''
        ordering = ('-publish',)

    def __str__(self):
        '''отображение объекта, понятного человеку'''
        return self.title

    def get_absolute_url(self):
        '''Получение сслылок на статьи, указав имя шаблона и параметры'''
        return reverse('blog:post_detail', args=[self.publish.year,
                                                 self.publish.month,
                                                 self.publish.day,
                                                 self.slug])

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return 'Comment by {} on {}'.format(self.name, self.post)


# Create your models here.
