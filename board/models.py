from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


# Create your models here.
class Post(models.Model):
    TYPE = (
        ('tank', 'Танки'),
        ('heal', 'Хилы'),
        ('dd', 'ДД'),
        ('trader', 'Торговцы'),
        ('guildmaster', 'Гилдмастеры'),
        ('quest', 'Квестгиверы'),
        ('smith', 'Кузнецы'),
        ('tanner', 'Кожевники'),
        ('potion', 'Зельевары'),
        ('spellmaster', 'Мастера заклинаний'),
    )
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=64, unique=True, verbose_name='Название')
    text = models.TextField()
    category = models.CharField(max_length=18, choices=TYPE, default='tank', verbose_name='Категория')
    upload = models.ImageField(upload_to='files/%Y/%m/%d/', null=True)
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    is_published = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return f'/post/{self.id}'

    def create(self):
        self.time_create = timezone.now()
        self.save()

    class Meta:
        ordering = ['-time_create', 'title']


class UserResponse(models.Model):
    author_response = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='author response')
    text_response = models.TextField(verbose_name='Текст')
    dateCreation = models.DateTimeField(auto_now_add=True)
    article = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name='response article')
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.text_response
