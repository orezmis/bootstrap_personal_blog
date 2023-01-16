import os
from django.db import models
from django.contrib.auth.models import User
from markdownx.models import MarkdownxField
from markdownx.utils import markdown

class Tag(models.Model):
    name        = models.CharField(max_length=50, unique=True)
    slug        = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/blog/tag/{self.slug}/'


class Category(models.Model):
    name        = models.CharField(max_length=50, unique=True)
    slug        = models.SlugField(max_length=200, unique=True, allow_unicode=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return f'/blog/category/{self.slug}/'

    class Meta:
        verbose_name_plural = 'Categories'


class Post(models.Model):
    title       = models.CharField(max_length=40)
    hook_text   = models.CharField(max_length=100, blank=True)
    content     = MarkdownxField()

    head_image  = models.ImageField(upload_to='blog/images/%Y/%m/%d/', blank=True)
    file_upload = models.FileField(upload_to='blog/files/%Y/%m/%d/', blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)
    author      = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    category    = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    tags        = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return f'[{self.pk}]{self.title} :: {self.author}'

    def get_absolute_url(self):
        return f'/blog/{self.pk}/'

    def get_file_name(self):
        return os.path.basename(self.file_upload.name)

    def get_file_ext(self):
        return self.get_file_name().split('.')[-1]

    def get_content_markdown(self):
        return markdown(self.content)

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.author}::{self.content}'

    def get_absolute_url(self):
        return f'{self.post.get_absolute_url()}#comment-{self.pk}'

    def get_avatar_url(self):
        try:
            if self.author.socialaccount_set.exists():
                return self.author.socialaccount_set.first().get_avatar_url()

            else:
                import requests
                email = str(self.author.email).encode('utf-8')
                url = f'https://gitlab.com/api/v4/avatar?email={email}&size=25'
                response = requests.get(url=url)
                if response.status_code == 200:
                    data = response.json()
                    av_url = data['avatar_url']
                else:
                    av_url = f'https://gitlab.com/api/v4/avatar?email=example@example.com&size=25'
                return av_url
                
        except:
            return 'https://dummyimage.com/50x50/ced4da/6c757d.jpg'