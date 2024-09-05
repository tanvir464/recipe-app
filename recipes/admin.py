from django.contrib import admin
from .models import Recipe, RecipeContent, Comment
from accounts.models import CustomUser
from django.db import models
from django.db.models import Count
import os
from django.conf import settings

class RecipeContentInline(admin.StackedInline):
    model = RecipeContent
    extra = 1

class CommentInline(admin.StackedInline):
    model = Comment
    extra = 0
    fields = ('user', 'text', 'created_at', 'reaction_count', 'parent')
    readonly_fields = ('created_at',)

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'uploader', 'upload_date', 'rating', 'view_count')
    list_filter = ('upload_date', 'uploader', 'category')
    search_fields = ('title', 'uploader__username', 'category')
    inlines = [RecipeContentInline, CommentInline]
    readonly_fields = ('rating', 'rating_count', 'view_count', 'comment_count')

    def delete_model(self, request, obj):
        if obj.card_image:
            card_image_path = os.path.join(settings.MEDIA_ROOT, obj.card_image.name)
            if os.path.isfile(card_image_path):
                os.remove(card_image_path)
        
        for content in obj.contents.all():
            if content.image_content:
                image_content_path = os.path.join(settings.MEDIA_ROOT, content.image_content.name)
                if os.path.isfile(image_content_path):
                    os.remove(image_content_path)

        uploader = obj.uploader
        if uploader:
            CustomUser.objects.filter(id=uploader.id).update(recipe_count=models.F('recipe_count') - 1)
        
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        uploaders = queryset.values('uploader').annotate(recipe_count=Count('id'))

        for uploader_data in uploaders:
            user = uploader_data['uploader']
            recipe_count = uploader_data['recipe_count']
            CustomUser.objects.filter(id=user).update(recipe_count=models.F('recipe_count') - recipe_count)

        for recipe in queryset:
            if recipe.card_image:
                card_image_path = os.path.join(settings.MEDIA_ROOT, recipe.card_image.name)
                if os.path.isfile(card_image_path):
                    os.remove(card_image_path)
            
            for content in recipe.contents.all():
                if content.image_content:
                    image_content_path = os.path.join(settings.MEDIA_ROOT, content.image_content.name)
                    if os.path.isfile(image_content_path):
                        os.remove(image_content_path)

        super().delete_queryset(request, queryset)

@admin.register(RecipeContent)
class RecipeContentAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'content_type', 'order')
    list_filter = ('content_type',)
    search_fields = ('recipe__title',)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'user', 'created_at', 'reaction_count', 'is_reply')
    list_filter = ('created_at',)
    search_fields = ('text', 'user__username', 'recipe__title')
    readonly_fields = ('created_at',)

    def is_reply(self, obj):
        return obj.parent is not None
    is_reply.boolean = True
    is_reply.short_description = 'Is Reply'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'recipe', 'parent')