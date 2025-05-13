from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'date_joined', 'recipe_count', 'profile_picture_preview')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'email', 'bio', 'profile_picture')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )
    readonly_fields = ('date_joined', 'last_login', 'profile_picture_preview')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    filter_horizontal = ('groups', 'user_permissions',)

    def profile_picture_preview(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" style="max-height: 50px; max-width: 50px;" />', obj.profile_picture.url)
        return "No Image"
    profile_picture_preview.short_description = 'Profile Preview'

    def recipe_count(self, obj):
        return obj.recipes.count()
    recipe_count.short_description = 'Recipes Count'

admin.site.register(CustomUser, CustomUserAdmin)