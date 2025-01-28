from django.contrib.auth.models import User
from django.db import models


# class CustomUser(AbstractUser):
#     ROLE_CHOICES = [
#         ('standard', 'Standard'),
#         ('manager', 'Manager'),
#     ]
#     role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='standard')

class Ingredient(models.Model):
    name = models.CharField(max_length=255, unique=True)
    unit = models.CharField(max_length=20, choices=[('ml', 'Milliliters'), ('g', 'Grams'), ('tsp', 'Teaspoons'),
                                                    ('tbsp', 'Tablespoons'), ('piece', 'Piece')])
    def __str__(self):
        return self.name

class Recipe(models.Model):
    title = models.CharField(max_length=255)
    instructions = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes')
    ingredients = models.ManyToManyField(Ingredient, through='RecipeIngredient')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',  # Updated related_name for clarity
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe_ingredients',  # Updated related_name to avoid conflicts
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=0)

    def __str__(self):
        return f"{self.quantity} {self.ingredient.unit} of {self.ingredient.name} for {self.recipe.title}"


class Comment(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment by {self.user.username} on {self.recipe.title}'