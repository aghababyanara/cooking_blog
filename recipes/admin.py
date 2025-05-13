from django.contrib import admin
from django.utils.html import format_html
from .models import Recipe, Ingredient, Instruction, Category, Review

class IngredientInline(admin.TabularInline):
    model = Ingredient
    extra = 1
    min_num = 1
    fields = ('name', 'quantity', 'unit')
    verbose_name_plural = "Ingredients"
    validate_min = True

class InstructionInline(admin.StackedInline):
    model = Instruction
    extra = 1
    min_num = 1
    fields = ('step_number', 'instruction_text')
    ordering = ('step_number',)
    verbose_name_plural = "Instructions"
    validate_min = True

@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    inlines = [IngredientInline, InstructionInline]
    list_display = ('title', 'author', 'category', 'difficulty', 
                    'formatted_cooking_time', 'get_total_comments',
                    'favorites_count', 'image_preview')
    list_filter = ('category', 'difficulty', 'created_at')
    search_fields = ('title', 'description', 'author__username')
    readonly_fields = ('created_at', 'updated_at', 'image_preview', 
                      'favorites_count', 'slug', 'get_total_comments')
    filter_horizontal = ('favorites',)
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Main Info', {
            'fields': ('title', 'author', 'category', 'slug')
        }),
        ('Details', {
            'fields': ('description', 'cooking_time', 'servings', 'difficulty')
        }),
        ('Social', {
            'fields': ('favorites', 'favorites_count', 'get_total_comments'),
            'classes': ('collapse',)
        }),
        ('Media', {
            'fields': ('image', 'image_preview'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def image_preview(self, obj):
        return format_html('<img src="{}" style="max-height: 100px;" />', obj.image.url) if obj.image else "No Image"
    image_preview.short_description = 'Image Preview'

    def favorites_count(self, obj):
        return obj.favorites.count()
    favorites_count.short_description = 'Favorites'

    def get_total_comments(self, obj):
        return obj.reviews.count()
    get_total_comments.short_description = 'Total Comments'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'recipe_count', 'image_preview')
    search_fields = ('name', 'slug')
    readonly_fields = ('image_preview', 'slug', 'recipe_count')
    fields = ('name', 'slug', 'image', 'image_preview')

    def image_preview(self, obj):
        return format_html('<img src="{}" style="max-height: 100px;" />', obj.image.url) if obj.image else "No Image"
    image_preview.short_description = 'Preview'

    def recipe_count(self, obj):
        return obj.recipes.count()
    recipe_count.short_description = 'Recipes'

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('get_truncated_comment', 'recipe', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('recipe__title', 'user__username', 'comment')
    readonly_fields = ('created_at',)
    raw_id_fields = ('recipe', 'user')
    list_select_related = ('recipe', 'user')

    def get_truncated_comment(self, obj):
        return f"{obj.comment[:47]}..." if len(obj.comment) > 50 else obj.comment
    get_truncated_comment.short_description = 'Comment'