from django.urls import path
from . import views
from .views import ingredient_autocomplete, verify_email, EditRecipeView

urlpatterns = [
    path('', views.main_page, name='main_page'),
    path('profile/', views.profile_page, name='profile_page'),
    path('profile/create/', views.CreateRecipeView.as_view(), name='create_recipe'),
    path('ingredient-autocomplete/', ingredient_autocomplete, name='ingredient_autocomplete'),
    path('recipes/', views.recipe_list, name='recipe_list'),
    path('recipes/<int:pk>/', views.recipe_detail, name='recipe_detail'),
    path('recipes/<int:pk>/add_comment/', views.add_comment, name='add_comment'),
    path('signup/', views.signup, name='signup'),
    path('accounts/login/', views.custom_login, name='login'),
    path('accounts/logout/', views.CustomLogoutView.as_view(next_page='main_page'), name='logout'),
    path('verify-email/<str:uidb64>/<str:token>/', verify_email, name='verify_email'),
    path('recipe/<int:pk>/edit/', EditRecipeView.as_view(), name='edit_recipe'),
]