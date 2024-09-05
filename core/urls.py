from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('category/<str:category>/', views.filter_by_category, name='filter_by_category'),
    path('top-rated/<str:time_filter>/', views.top_rated, name='top_rated'),
    path('most-viewed/<str:time_filter>/', views.most_viewed, name='most_viewed'),
    path('search/', views.search_results, name='search_results'),
]