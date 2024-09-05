from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'bio', 'profile_picture')}),
        ('Social', {'fields': ('follower_count', 'following_count', 'recipe_count', 'follower_list', 'following_list')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )

    # readonly_fields = ('recipe_count',)

    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'follower_count', 'following_count', 'recipe_count')

    search_fields = ('username', 'first_name', 'last_name', 'email')

    ordering = ('username',)
