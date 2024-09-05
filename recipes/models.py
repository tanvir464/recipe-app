from django.db import models
from django.utils import timezone
from django.conf import settings
from PIL import Image

class Recipe(models.Model):
    CATEGORY_CHOICES = [
        ('-', '-'),
        ('Starters', 'Starters'),
        ('Main Courses', 'Main Courses'),
        ('Sides', 'Sides'),
        ('Desserts', 'Desserts'),
        ('Drinks', 'Drinks'),
    ]
    uploader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    upload_date = models.DateTimeField(default=timezone.now)
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='-')
    card_image = models.ImageField(upload_to='recipe_card_images/')
    rating = models.FloatField(default=0.0)
    rating_count = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    rated_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='rated_recipes', through='UserRating')

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.card_image and hasattr(self.card_image, 'path'):
            image = Image.open(self.card_image.path)
            max_size = (1024, 1024)
            image.thumbnail(max_size)
            image.save(self.card_image.path, quality=85)

class UserRating(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    rating = models.FloatField()
    rated_at = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    recipe = models.ForeignKey('Recipe', related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    reaction_count = models.PositiveIntegerField(default=0)
    parent = models.ForeignKey('self', null=True, blank=True, related_name='comment_replies', on_delete=models.CASCADE)
    reacted_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='reacted_comments')

    def __str__(self):
        return f"Comment by {self.user.username} on {self.recipe.title}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.recipe.comment_count = self.recipe.comments.count()
            self.recipe.save()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.recipe.comment_count = self.recipe.comments.count()
        self.recipe.save()

class RecipeContent(models.Model):
    recipe = models.ForeignKey(Recipe, related_name='contents', on_delete=models.CASCADE)
    content_type = models.CharField(max_length=10, choices=[('text', 'Text'), ('image', 'Image')])
    text_content = models.TextField(blank=True, null=True)
    image_content = models.ImageField(upload_to='recipe_images/', blank=True, null=True)
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image_content and hasattr(self.image_content, 'path'):
            image = Image.open(self.image_content.path)
            max_size = (1024, 1024)
            image.thumbnail(max_size)
            image.save(self.image_content.path, quality=85)