from django import forms
from django.contrib.auth.models import User
from django.forms import inlineformset_factory, BaseInlineFormSet
from .models import Recipe, RecipeIngredient, Ingredient

from django.contrib.auth.forms import UserCreationForm

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'instructions']
        widgets = {
            'instructions': forms.Textarea(attrs={'rows': 5, 'cols': 50}),
        }

# RecipeIngredient form
class RecipeIngredientForm(forms.ModelForm):
    # ingredient = forms.TextInput(attrs={'class': 'ingredient-id-placeholder', 'type': 'hidden'})
    ingredient_name = forms.CharField(widget=forms.TextInput(attrs={
            'class': 'autocomplete',
            'placeholder': 'Start typing ingredient...'
        }))
    unit = forms.CharField(required=False)
    # DELETE = forms.BooleanField(required=True)

    class Meta:
        model = RecipeIngredient
        fields = ['ingredient', 'quantity', 'unit']
        widgets = {'ingredient': forms.TextInput(attrs={'type': 'hidden', 'class': 'ingredient-id-placeholder'})}

# Custom formset validation
class BaseRecipeIngredientFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        ingredients = []
        for form in self.forms:
            if form.cleaned_data.get('DELETE'):  # Skip deleted forms
                continue

            ingredient = form.cleaned_data.get('ingredient')  # Use the ingredient instance directly
            if ingredient in ingredients:
                raise forms.ValidationError("Each ingredient must be unique.")
            ingredients.append(ingredient)

class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data

RecipeIngredientFormSet = inlineformset_factory(
    Recipe,
    RecipeIngredient,
    form=RecipeIngredientForm,
    formset=BaseRecipeIngredientFormSet,
    extra=0,
    can_delete=True,
    max_num=None,
)
