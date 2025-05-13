from django.db import models
from django.urls import reverse
from users.models import CustomUser
from django.core.validators import MinValueValidator, FileExtensionValidator, MaxValueValidator
from django.utils.text import slugify
from autoslug import AutoSlugField
from django.db import models
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

class HoursMinutesSecondsField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 9)  
        kwargs.setdefault('help_text', 'Format: HH:MM:SS (e.g. 1:30:00)')
        super().__init__(*args, **kwargs)

    def validate(self, value, model_instance):
        super().validate(value, model_instance)
        try:
            hours, minutes, seconds = map(int, value.split(':'))
            if any([
                hours < 0,
                not (0 <= minutes <= 59),
                not (0 <= seconds <= 59)
            ]):
                raise ValueError
        except (ValueError, AttributeError, IndexError):
            raise ValidationError('Invalid time format. Use HH:MM:SS (hours >= 0, minutes/seconds 00-59)')

class Ingredient(models.Model):
    class Units(models.TextChoices):
        GRAMS = 'g', 'Grams'
        KILOGRAMS = 'kg', 'Kilograms'
        MILLILITERS = 'ml', 'Milliliters'
        LITERS = 'l', 'Liters'
        CUP = 'cup', 'Cup'
        PIECE = 'piece', 'Piece'
        POUNDS = 'pounds', 'Pounds'

    name = models.CharField(
        max_length=100,
        verbose_name="Ingredient Name",
        help_text="Name of the ingredient"
    )
    quantity = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name="Quantity",
        validators=[MinValueValidator(0.01)]
    )
    unit = models.CharField(
        max_length=20,
        choices=Units.choices,
        verbose_name="Measurement Unit"
    )
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        related_name="ingredients",
        verbose_name="Associated Recipe"
    )

    class Meta:
        verbose_name = "Ingredient"
        verbose_name_plural = "Ingredients"
        ordering = ['name']

    def __str__(self):
        return f"{self.quantity} {self.get_unit_display()} of {self.name}"

class Recipe(models.Model):
    class DifficultyLevel(models.TextChoices):
        EASY = 'easy', 'Easy'
        MEDIUM = 'medium', 'Medium'
        HARD = 'hard', 'Hard'

    total_comments = models.PositiveIntegerField(default=0, verbose_name="Total Comments")


    title = models.CharField(
        max_length=200,
        verbose_name="Recipe Title",
        unique=True
    )
    description = models.TextField(
        verbose_name="Description",
        help_text="Brief recipe description"
    )   
    cooking_time = HoursMinutesSecondsField(verbose_name="Cooking Time",)
    servings = models.PositiveIntegerField(
        verbose_name="Number of Servings",
        validators=[MinValueValidator(1)]
    )
    difficulty = models.CharField(
        max_length=20,
        choices=DifficultyLevel.choices,
        default=DifficultyLevel.MEDIUM,
        verbose_name="Difficulty Level"
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Author"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    favorites = models.ManyToManyField(
        CustomUser,
        related_name='favorite_recipes',
        blank=True,
        verbose_name=('favorites')
    )
    image = models.ImageField(
        upload_to="recipes/",
        blank=True,
        null=True,
        verbose_name="Recipe Image",
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png',])]
    )
    category = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="recipes",
        verbose_name="Category"
    )
    slug = AutoSlugField(
        populate_from='title',
        unique=True,
        verbose_name="URL Slug",
        always_update=True 
    )

    def get_absolute_url(self):
        return reverse("recipes:recipe-detail", kwargs={"slug": self.slug})

    def formatted_cooking_time(self):
        return f"{self.cooking_time} minutes"
    formatted_cooking_time.short_description = "Cooking Time"

    class Meta:
        verbose_name = "Recipe"
        verbose_name_plural = "Recipes"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['title']),
        ]

    def __str__(self):
        return self.title

class Instruction(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="instructions",
        verbose_name="Recipe Instructions"
    )
    step_number = models.PositiveIntegerField(
        verbose_name="Step Number",
        validators=[MinValueValidator(1)]
    )
    instruction_text = models.TextField(
        verbose_name="Instruction Text",
        help_text="Detailed step description",
        default="Description"
    )

    class Meta:
        verbose_name = "Instruction Step"
        verbose_name_plural = "Instruction Steps"
        ordering = ['step_number']
        unique_together = ['recipe', 'step_number']

    def __str__(self):
        return f"Step {self.step_number} for {self.recipe.title}"

class Category(models.Model):
    name = models.CharField(
        max_length=200,
        verbose_name="Category Name",
        unique=True
    )
    slug = AutoSlugField(
        populate_from='name',
        unique=True,
        verbose_name="Category Slug",
        always_update=True
    )

    image = models.ImageField(
        upload_to="categories/",
        blank=True,
        null=True,
        verbose_name="Category Image",
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])]
    )

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['name']

    def get_absolute_url(self):
        return reverse("recipes:category_list", kwargs={"slug": self.slug})

    def __str__(self):
        return self.name



class Review(models.Model):
    recipe = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    user = models.ForeignKey(
        'users.CustomUser',
        on_delete=models.CASCADE
    )
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['recipe', 'user']

    def __str__(self):
        return f"Comment by {self.user}"

@receiver([post_save, post_delete], sender=Review)
def update_comment_count(sender, instance, **kwargs):
    recipe = instance.recipe
    recipe.total_comments = Review.objects.filter(recipe=recipe).count()
    recipe.save(update_fields=['total_comments'])


@receiver(post_delete, sender=Review)
def update_comment_on_delete(sender, instance, **kwargs):
    instance.recipe.total_comments = instance.recipe.reviews.count()
    instance.recipe.save(update_fields=['total_comments'])
