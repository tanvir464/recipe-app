from django import forms
from .models import Recipe

class RecipeForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = ['title', 'category', 'card_image']

class RecipeContentForm(forms.Form):
    content_type = forms.ChoiceField(choices=[('text', 'Text'), ('image', 'Image')])
    text_content = forms.CharField(widget=forms.Textarea, required=False)
    image_content = forms.ImageField(required=False)
    order = forms.IntegerField(widget=forms.HiddenInput)