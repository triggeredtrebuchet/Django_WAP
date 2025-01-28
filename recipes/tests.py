from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.http import HttpResponseForbidden
from recipes.models import Recipe, Ingredient
from django.contrib.messages import get_messages


class RecipeViewsTest(TestCase):

    def setUp(self):
        # Create a user to test with
        self.user = User.objects.create_user(username='testuser', password='testpassword')
        self.user2 = User.objects.create_user(username='testuser2', password='testpassword')

        # Create a sample recipe
        self.recipe = Recipe.objects.create(
            title="Test Recipe",
            author=self.user,
            instructions="Test Instructions"
        )

        # Create some ingredients
        self.ingredient = Ingredient.objects.create(name="Sugar", unit="grams")

    def test_create_recipe_view(self):
        """Test the creation of a new recipe"""
        self.client.login(username='testuser', password='testpassword')
        url = reverse('create_recipe')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/create_recipe.html')

        # Test post request
        data = {
            'title': 'New Recipe',
            'instructions': 'New Instructions',
            'ingredients': 'Sugar',
            'quantity': '100'
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('profile_page'))

    def test_edit_recipe_view(self):
        """Test the editing of an existing recipe"""
        self.client.login(username='testuser', password='testpassword')
        url = reverse('edit_recipe', args=[self.recipe.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/edit_recipe.html')

        # Test post request with valid data
        data = {
            'title': 'Updated Recipe',
            'instructions': 'Updated Instructions',
            'ingredients': 'Sugar',
            'quantity': '200'
        }
        response = self.client.post(url, data)
        self.recipe.refresh_from_db()  # Refresh to get the updated data
        self.assertEqual(self.recipe.title, 'Updated Recipe')
        self.assertRedirects(response, reverse('profile_page'))

    def test_edit_recipe_view_unauthorized(self):
        """Test that a user cannot edit another user's recipe"""
        self.client.login(username='testuser2', password='testpassword')
        url = reverse('edit_recipe', args=[self.recipe.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, HttpResponseForbidden.status_code)
        self.assertContains(response, 'You are not authorized to edit this recipe.')

    def test_add_comment(self):
        """Test adding a comment to a recipe"""
        self.client.login(username='testuser', password='testpassword')
        url = reverse('add_comment', args=[self.recipe.id])
        data = {'content': 'This is a comment.'}
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('recipe_detail', args=[self.recipe.id]))
        self.assertEqual(self.recipe.comments.count(), 1)
        self.assertEqual(self.recipe.comments.first().content, 'This is a comment.')

    def test_signup_view(self):
        """Test the signup process"""
        url = reverse('signup')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/signup.html')

        # Test post request with valid data
        data = {
            'username': 'newuser',
            'password1': 'newpassword',
            'password2': 'newpassword',
            'email': 'newuser@example.com'
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('profile_page'))

    def test_login_redirects_to_profile_page(self):
        """Test that login redirects to the profile page"""
        url = reverse('login')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'recipes/login.html')

        # After login, it should redirect to profile page
        data = {
            'username': 'testuser',
            'password': 'testpassword'
        }
        response = self.client.post(url, data, follow=True)
        self.assertRedirects(response, reverse('profile_page'))

    def test_logout_redirects_to_main_page(self):
        """Test that logout redirects to the main page"""
        self.client.login(username='testuser', password='testpassword')
        url = reverse('logout')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('main_page'))
