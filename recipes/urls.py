from django.urls import path

from . import views

app_name = "recipes"

urlpatterns = [
    path('', views.HomeView.as_view(), name='recipe-list'),
    path('recipe/<slug:slug>/', views.RecipeDetailView.as_view(), name='recipe-detail'),
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('category/<slug:slug>/', views.CategoryDetailView.as_view(), name='category-detail'),
    path('create/', views.RecipeCreateView.as_view(), name='recipe-create'),
    path('<slug:slug>/favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('favorites-list/', views.favorites_list, name='favorites_list'),
    path('<slug:slug>/review/create/', views.ReviewCreateView.as_view(), name='review-create'),
    path('reviews/<int:pk>/edit/', views.ReviewUpdateView.as_view(), name='review-edit'),
    path('reviews/<int:pk>/delete/', views.ReviewDeleteView.as_view(), name='review-delete'),
    ]