from django.contrib import admin
from .models import Recipe, Comment, Ingredient, RecipeIngredient
admin.site.register(Recipe)
admin.site.register(Comment)
admin.site.register(Ingredient)
admin.site.register(RecipeIngredient)