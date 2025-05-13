from django import forms
from .models import Review, Recipe, Ingredient, Instruction
from django.forms import inlineformset_factory
from django.core.validators import RegexValidator


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['comment']

class RecipeForm(forms.ModelForm):
    cooking_time = forms.CharField(
        validators=[
            RegexValidator(
                regex=r'^([0-1]?\d|2[0-3]):([0-5]?\d):([0-5]?\d)$',  
                message='Time format: HH:MM:SS (max 23:59:59)'
            )
        ]
    )
    
    class Meta:
        model = Recipe
        fields = ['title', 'description', 'cooking_time', 'servings', 'difficulty', 'category', 'image']
        widgets = {
            'cooking_time': forms.TextInput(attrs={'placeholder': 'HH:MM:SS'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

IngredientFormSet = inlineformset_factory(
    Recipe,
    Ingredient,
    fields=('name', 'quantity', 'unit'),
    extra=2,
    can_delete=False,
    widgets={
        'name': forms.TextInput(attrs={'placeholder': 'e. g. Flour'}),
        'quantity': forms.NumberInput(attrs={'step': '0.01', 'placeholder': 'e. g. 100'}),
    }
)

InstructionFormSet = inlineformset_factory(
    Recipe,
    Instruction,
    fields=('instruction_text',),  
    extra=3,
    can_delete=False,
    widgets={
        'instruction_text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'e. g. Mix the ingredients...'}),
    }
)

class InstructionForm(forms.ModelForm):
    class Meta:
        model = Instruction
        fields = ('instruction_text',)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['step_number'] = forms.IntegerField(
            widget=forms.HiddenInput(),
            required=False
        )