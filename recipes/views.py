import io

from django.contrib import messages
from django.contrib.auth.views import LogoutView
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate, logout
from django.utils.xmlutils import SimplerXMLGenerator

from .models import Recipe, Comment
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse, HttpResponseForbidden
from django.urls import reverse
from recipes.forms import RecipeForm, RecipeIngredient, RecipeIngredientFormSet, RecipeIngredientForm, SignUpForm
from django.views import View
from recipes.models import Ingredient
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

class EditRecipeView(LoginRequiredMixin, View):
    login_url = '/login/'
    redirect_field_name = 'next'


    def get(self, request, pk):
        recipe = Recipe.objects.get(pk=pk)
        recipe_form = RecipeForm(instance=recipe)
        formset = RecipeIngredientFormSet(instance=recipe)

        # Query the ingredients for this recipe to pass the ingredient name and unit
        ingredients_info = []
        for recipe_ingredient in recipe.recipe_ingredients.all():
            ingredients_info.append({
                'ingredient_name': recipe_ingredient.ingredient.name,
                'unit': recipe_ingredient.ingredient.unit
            })

        # Pair forms with the ingredient data
        forms_with_ingredient_data = zip(formset.forms, ingredients_info)

        return render(request, 'recipes/edit_recipe.html', {
            'recipe': recipe,
            'recipe_form': recipe_form,
            'formset': formset,
            'forms_with_ingredient_data': forms_with_ingredient_data  # Pass the paired forms and ingredient data to the template
        })

    def post(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)

        # Ensure the logged-in user is the author of the recipe
        if recipe.author != request.user:
            return HttpResponseForbidden("You are not authorized to edit this recipe.")

        recipe_form = RecipeForm(request.POST, instance=recipe)
        formset = RecipeIngredientFormSet(request.POST, instance=recipe)

        if recipe_form.is_valid() and formset.is_valid():
            recipe_form.save()
            formset.save()
            return redirect('profile_page')

        messages.error(request, 'Please correct the ingredients')

        return self.get(request, pk)

class CreateRecipeView(LoginRequiredMixin, View):
    login_url = '/login/'  # Redirect to login if not authenticated
    redirect_field_name = 'next'  # Where to redirect after login

    def get(self, request):
        print(request)
        recipe_form = RecipeForm()
        formset = RecipeIngredientFormSet()
        return render(request, 'recipes/create_recipe.html', {'recipe_form': recipe_form, 'formset': formset})

    def post(self, request):
        print(request)
        recipe_form = RecipeForm(request.POST)
        formset = RecipeIngredientFormSet(request.POST)

        if recipe_form.is_valid() and formset.is_valid():
            recipe = recipe_form.save(commit=False)
            recipe.author = request.user
            recipe.save()
            formset.instance = recipe
            formset.save()
            return redirect('profile_page')
        messages.error(request, 'Please correct the ingredients')
        return render(request, 'recipes/create_recipe.html', {'recipe_form': recipe_form, 'formset': formset})
def main_page(request):
    recipes = Recipe.objects.all()
    return render(request, 'recipes/main_page.html', {'recipes': recipes})

# User profile page
@login_required
def profile_page(request):
    user_recipes = request.user.recipes.all()
    return render(request, 'recipes/profile_page.html', {'user_recipes': user_recipes})

# Create new recipe
@login_required
def create_recipe(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        ingredients = request.POST.get('ingredients')
        instructions = request.POST.get('instructions')
        recipe, created = Recipe.objects.get_or_create(
            title=title,
            author=request.user,
            defaults={
                'ingredients': ingredients,
                'instructions': instructions
            }
        )
        if not created:
            return render(request, 'recipes/create_recipe.html', {'error': 'Recipe already exists!'})
        return redirect('profile_page')
    return render(request, 'recipes/create_recipe.html')

# Display all recipes
def recipe_list(request):
    recipes = Recipe.objects.all()
    return render(request, 'recipes/recipe_list.html', {'recipes': recipes})

# Display recipe detail
def recipe_detail(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if request.user.is_authenticated:
        return render(request, 'recipes/recipe_detail.html', {'recipe': recipe})
    else:
        return render(request, 'recipes/recipe_guest.html', {'recipe': recipe})

# Add a comment
@login_required
def add_comment(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    if request.method == 'POST':
        content = request.POST.get('content')
        Comment.objects.create(recipe=recipe, user=request.user, content=content)
        return HttpResponseRedirect(reverse('recipe_detail', args=[pk]))

# Signup view
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate account until email verification
            user.save()

            # Generate token and send email
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            verification_link = request.build_absolute_uri(
                reverse('verify_email', kwargs={'uidb64': uid, 'token': token})
            )

            # Send email
            subject = "Verify your email"
            message = f"Click the link to verify your email: {verification_link}"
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [user.email]
            send_mail(subject, message, from_email, recipient_list)
            messages.success(request, 'We sent a verification email to your address. Please check your inbox.')

            return render(request, 'recipes/main_page.html', {'message': 'Please check your email to verify your account.'})
    else:
        form = SignUpForm()

    return render(request, 'recipes/signup.html', {'form': form})

def verify_email(request, uidb64, token):
    from django.utils.http import urlsafe_base64_decode
    from django.contrib.auth.models import User

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return render(request, 'recipes/profile_page.html', {'message': 'Email verified!'})
    else:
        return HttpResponse('Verification link is invalid!', status=400)

class EmailVerificationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_active:
            return redirect('email_verification_required')
        return self.get_response(request)

# Login view override for redirect
def custom_login(request, *args, **kwargs):
    from django.contrib.auth.views import LoginView
    response = LoginView.as_view(template_name='recipes/login.html')(request, *args, **kwargs)
    if request.user.is_authenticated:
        return redirect('profile_page')
    return response

# Logout view override for redirect
class CustomLogoutView(LogoutView):
    next_page = 'main_page'


def ingredient_autocomplete(request):
    query = request.GET.get('term', '')  # 'term' is the default parameter for jQuery UI Autocomplete
    ingredients = Ingredient.objects.filter(name__icontains=query)[:10]  # Limit results to 10

    # Create an XML response
    output = io.StringIO()
    xml = SimplerXMLGenerator(output, 'utf-8')
    xml.startDocument()
    xml.startElement('ingredients', {})

    for ingredient in ingredients:
        xml.startElement('ingredient', {'id': str(ingredient.id),
                                                    'unit': ingredient.unit})
        xml.characters(ingredient.name)
        xml.endElement('ingredient')

    xml.endElement('ingredients')
    xml.endDocument()

    return HttpResponse(output.getvalue(), content_type='application/xml')
