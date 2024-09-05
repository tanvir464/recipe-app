from django.contrib.auth.models import AbstractUser
from django.db import models
import os
from django.conf import settings
from PIL import Image

class CustomUser(AbstractUser):
    bio = models.TextField(max_length=2000, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', default='profile_pics/default.jpg')
    follower_count = models.IntegerField(default=0)
    following_count = models.IntegerField(default=0)
    recipe_count = models.IntegerField(default=0)
    follower_list = models.ManyToManyField('self', related_name='followers', symmetrical=False, blank=True)
    following_list = models.ManyToManyField('self', related_name='followings', symmetrical=False, blank=True)
    
    def __str__(self):
        return self.username
    
        
    def save(self, *args, **kwargs):
        try:
            old_profile_picture = CustomUser.objects.get(pk=self.pk).profile_picture
            if old_profile_picture != 'profile_pics/default.jpg':
                if old_profile_picture and old_profile_picture.url != self.profile_picture.url:
                    old_profile_picture_path = os.path.join(settings.MEDIA_ROOT, old_profile_picture.name)
                    if os.path.isfile(old_profile_picture_path):
                        os.remove(old_profile_picture_path)
        except CustomUser.DoesNotExist:
            pass

        super().save(*args, **kwargs)

        if self.profile_picture:
            image = Image.open(self.profile_picture.path)
            max_size = (1024, 1024)
            image.thumbnail(max_size)
            image.save(self.profile_picture.path, quality=85)
