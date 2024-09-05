from django.shortcuts import render
from recipes.models import Recipe
import datetime
from django.db.models import Q
from accounts.models import CustomUser

def index(request):
    featured_recipes = Recipe.objects.all().order_by('-rating')[:12]
    latest_recipes = Recipe.objects.all().order_by('-upload_date')[:12]

    context = {
        'featured_recipes': featured_recipes,
        'latest_recipes': latest_recipes,
    }
    return render(request, 'core/index.html', context)

def filter_by_category(request, category):
    featured_recipes = Recipe.objects.filter(category__iexact=category).order_by('-rating')[:12]
    latest_recipes = Recipe.objects.filter(category__iexact=category).order_by('-upload_date')[:12]

    context = {
        'featured_recipes': featured_recipes,
        'latest_recipes': latest_recipes,
    }
    return render(request, 'core/index.html', context)

def top_rated(request, time_filter):
    today = datetime.date.today()
    
    if time_filter == 'year':
        start_date = today - datetime.timedelta(days=365)
    elif time_filter == 'month':
        start_date = today - datetime.timedelta(days=30)
    elif time_filter == 'week':
        start_date = today - datetime.timedelta(days=7)
    else:
        start_date = None
    
    if start_date:
        featured_recipes = Recipe.objects.filter(upload_date__gte=start_date).order_by('-rating')[:12]
        latest_recipes = Recipe.objects.filter(upload_date__gte=start_date).order_by('-upload_date')[:12]
    else:
        featured_recipes = Recipe.objects.all().order_by('-rating')[:12]
        latest_recipes = Recipe.objects.all().order_by('-upload_date')[:12]

    context = {
        'featured_recipes': featured_recipes,
        'latest_recipes': latest_recipes,
    }
    return render(request, 'core/index.html', context)

def most_viewed(request, time_filter):
    today = datetime.date.today()
    
    if time_filter == 'year':
        start_date = today - datetime.timedelta(days=365)
    elif time_filter == 'month':
        start_date = today - datetime.timedelta(days=30)
    elif time_filter == 'week':
        start_date = today - datetime.timedelta(days=7)
    else:
        start_date = None
    
    if start_date:
        featured_recipes = Recipe.objects.filter(upload_date__gte=start_date).order_by('-view_count')[:12]
        latest_recipes = Recipe.objects.filter(upload_date__gte=start_date).order_by('-view_count')[:12]
    else:
        featured_recipes = Recipe.objects.all().order_by('-view_count')[:12]
        latest_recipes = Recipe.objects.all().order_by('-view_count')[:12]

    context = {
        'featured_recipes': featured_recipes,
        'latest_recipes': latest_recipes,
    }
    return render(request, 'core/index.html', context)

def search_results(request):
    query = request.GET.get('query', '')

    user_results = CustomUser.objects.filter(
        Q(username__icontains=query) |
        Q(bio__icontains=query)
    ).distinct() [:12]

    recipe_results = Recipe.objects.filter(
        Q(title__icontains=query) |
        Q(contents__text_content__icontains=query)
    ).distinct() [:12]

    context = {
        'user_results': user_results,
        'recipe_results': recipe_results,
    }

    return render(request, 'core/results.html', context)
