from django.db import models
from django.contrib.auth.models import AbstractUser
from django.urls import reverse
from django.core.validators import FileExtensionValidator

class CustomUser(AbstractUser):
    bio = models.TextField(max_length=500, blank=True, verbose_name="Biography")
    profile_picture = models.ImageField(    
        upload_to='users/profile_pics/',
        blank=True,
        null=True,
        default='static/images/default_picture.png',
        verbose_name="Profile Picture",
        validators=[FileExtensionValidator(['jpg', 'png', 'jpeg'])]
    )

    def get_absolute_url(self):
        return reverse("users:profile", kwargs={"pk": self.pk})
    
    def get_recipe_count(self):
        return self.recipes.count()
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username
        
    
    