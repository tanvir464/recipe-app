from django.urls import path
from . import views

urlpatterns = [
    path('<int:recipe_id>/delete/', views.delete_recipe, name='delete_recipe'),
    path('<int:recipe_id>/rate/', views.rate_recipe, name='rate_recipe'),
    path('toggle_reaction/', views.toggle_reaction, name='toggle_reaction'),
    path('delete_comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('upload/', views.upload_recipe, name='upload_recipe'),
    path('recipe/<int:recipe_id>/', views.recipe_detail, name='recipe_detail'),
    path('recipe/<int:recipe_id>/add_comment/', views.add_comment, name='add_comment'),
    path('recipe/<int:recipe_id>/details/', views.get_recipe_details, name='get_recipe_details'),
    path('recipe/<int:recipe_id>/cancel_rate/', views.cancel_rate_recipe, name='cancel_rate_recipe'),
]