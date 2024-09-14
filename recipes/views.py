from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import CustomUser
from django.db import models
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Avg
from .models import Recipe, RecipeContent, Comment, UserRating
from django.template.loader import render_to_string
from django.urls import reverse
import os
from django.conf import settings

def upload_recipe(request):
    if not request.user.is_authenticated:
        messages.warning(request, 'Please log in first to upload a recipe.', extra_tags='alert-dismissible fade show')
        return redirect(reverse('login'))

    if request.method == 'POST':
        title = request.POST.get('title')
        category = request.POST.get('category')
        card_image = request.FILES.get('card_image')
        content_types = request.POST.getlist('content_type[]')
        text_contents = request.POST.getlist('text_content[]')
        image_contents = request.FILES.getlist('image_content[]')
        content_orders = request.POST.getlist('content_order[]')

        recipe = Recipe.objects.create(
            title=title, 
            category=category, 
            uploader=request.user,
            card_image=card_image
        )

        text_index = 0
        image_index = 0

        for i, content_type in enumerate(content_types):
            if content_type == 'text':
                if text_index < len(text_contents):
                    RecipeContent.objects.create(
                        recipe=recipe,
                        content_type='text',
                        text_content=text_contents[text_index],
                        order=content_orders[i]
                    )
                    text_index += 1
            elif content_type == 'image':
                if image_index < len(image_contents):
                    RecipeContent.objects.create(
                        recipe=recipe,
                        content_type='image',
                        image_content=image_contents[image_index],
                        order=content_orders[i]
                    )
                    image_index += 1

        CustomUser.objects.filter(id=request.user.id).update(recipe_count=models.F('recipe_count') + 1)

        messages.warning(request, 'Recipe uploaded successfully!', extra_tags='alert-dismissible fade show')
        return redirect(request.path)

    return render(request, 'recipes/upload.html')

def recipe_detail(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    if recipe.uploader != request.user and request.user.is_authenticated:
        recipe.view_count += 1
        recipe.save()
    contents = recipe.contents.all().order_by('order')
    comments = recipe.comments.filter(parent=None).prefetch_related('comment_replies').order_by('-created_at')
    user_rating = None
    if request.user.is_authenticated:
        user_rating = UserRating.objects.filter(user=request.user, recipe=recipe).first()
    
    context = {
        'recipe': recipe,
        'contents': contents,
        'comments': comments,
        'user_rating': user_rating.rating if user_rating else None,
    }
    return render(request, 'recipes/recipe.html', context)

@login_required
@require_POST
def add_comment(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    comment_text = request.POST.get('comment', '')
    parent_id = request.POST.get('parent_id')

    if comment_text:
        if parent_id:
            parent_comment = get_object_or_404(Comment, id=parent_id)
            new_comment = Comment.objects.create(
                user=request.user,
                recipe=recipe,
                text=comment_text,
                parent=parent_comment
            )
        else:
            new_comment = Comment.objects.create(
                user=request.user,
                recipe=recipe,
                text=comment_text
            )

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'comment_html': render_to_string('recipes/comment_snippet.html', {'comment': new_comment})
            })
    else:
        messages.error(request, 'Comment text is required.')
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'error': 'Comment text is required.'})

    return redirect('recipe_detail', recipe_id=recipe_id)

@login_required
@require_POST
def rate_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    rating = request.POST.get('rating')
    if rating:
        try:
            rating = float(rating)
            UserRating.objects.update_or_create(
                user=request.user,
                recipe=recipe,
                defaults={'rating': rating}
            )

            avg_rating = UserRating.objects.filter(recipe=recipe).aggregate(Avg('rating'))['rating__avg']
            recipe.rating = avg_rating
            recipe.rating_count = UserRating.objects.filter(recipe=recipe).count()
            recipe.save()
            
            return JsonResponse({
                'success': True,
                'user_rating': rating,
                'avg_rating': avg_rating,
                'rating_count': recipe.rating_count
            })
        except ValueError:
            return JsonResponse({'success': False, 'error': 'Invalid rating value'})
    else:
        return JsonResponse({'success': False, 'error': 'Rating is required'})
    
@login_required
@require_POST
def cancel_rate_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    UserRating.objects.filter(user=request.user, recipe=recipe).delete()

    avg_rating = UserRating.objects.filter(recipe=recipe).aggregate(Avg('rating'))['rating__avg']
    recipe.rating = avg_rating or 0
    recipe.rating_count = UserRating.objects.filter(recipe=recipe).count()
    recipe.save()
    
    return JsonResponse({
        'success': True,
        'avg_rating': recipe.rating,
        'rating_count': recipe.rating_count
    })

def get_recipe_details(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)
    user_rating = UserRating.objects.filter(user=request.user, recipe=recipe).first()
    return JsonResponse({
        'user_rating': user_rating.rating if user_rating else 0,
        'avg_rating': recipe.rating,
        'rating_count': recipe.rating_count
    })

@login_required
@require_POST
def toggle_reaction(request):
    content_type = request.POST.get('content_type')
    content_id = request.POST.get('content_id')

    if content_type in ['comment', 'reply']:
        content = get_object_or_404(Comment, id=content_id)
    else:
        return JsonResponse({'success': False, 'error': 'Invalid content type'})

    if request.user in content.reacted_by.all():
        content.reacted_by.remove(request.user)
        action = 'removed'
    else:
        content.reacted_by.add(request.user)
        action = 'added'

    content.reaction_count = content.reacted_by.count()
    content.save()

    return JsonResponse({
        'success': True,
        'action': action,
        'reaction_count': content.reacted_by.count()
    })


@login_required
@require_POST
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    
    if request.user == comment.user:
        comment.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'error': 'You are not authorized to delete this comment'})

@login_required
@require_POST
def delete_recipe(request, recipe_id):
    recipe = get_object_or_404(Recipe, id=recipe_id)

    if request.user == recipe.uploader:
        if recipe.card_image:
            card_image_path = os.path.join(settings.MEDIA_ROOT, recipe.card_image.name)
            if os.path.isfile(card_image_path):
                os.remove(card_image_path)
        
        for content in recipe.contents.all():
            if content.image_content:
                image_content_path = os.path.join(settings.MEDIA_ROOT, content.image_content.name)
                if os.path.isfile(image_content_path):
                    os.remove(image_content_path)
                    
        request.user.recipe_count -= 1
        request.user.save()
        recipe.delete()
        messages.success(request, 'Recipe deleted successfully!', extra_tags='alert-dismissible fade show')
        return redirect('index')