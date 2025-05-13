from django.shortcuts import render, get_object_or_404
from django.views import View
from django.core.paginator import Paginator
from django.db.models import Count, Prefetch
from .models import Recipe, Category, Review, Instruction
from django.db.models import Max
from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db import IntegrityError, transaction
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from.forms import ReviewForm, RecipeForm , IngredientFormSet, InstructionFormSet
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib import messages
from django.db import IntegrityError
from .forms import RecipeForm, IngredientFormSet, InstructionFormSet

class HomeView(View):
    def get(self, request):  # Убрали параметр slug
        categories = Category.objects.annotate(
            recipe_count=Count('recipes')
        ).prefetch_related(
            Prefetch(
                'recipes',
                queryset=Recipe.objects.select_related('author', 'category')
                             .annotate(comment_count=Count('reviews'))
                             .order_by('-created_at')[:18],
                to_attr='featured_recipes'
            )
        ).order_by('name')[:6]

        context = {'categories': categories}
        return render(request, 'recipes/index.html', context)

class RecipeDetailView(View):
    def get(self, request, slug):
        recipe = get_object_or_404(
            Recipe.objects
                .select_related('author', 'category')
                .prefetch_related(
                    'ingredients',
                    Prefetch('instructions', 
                        queryset=Instruction.objects.order_by('step_number')
                    ),
                    Prefetch('reviews',
                        queryset=Review.objects.select_related('user')
                    )
                ),
            slug=slug
        )

        user_review = None
        if request.user.is_authenticated:
            user_review = Review.objects.filter(
                recipe=recipe,
                user=request.user
            ).first()

        recommended_recipes = Recipe.objects.filter(
            category=recipe.category
        ).exclude(
            id=recipe.id
        ).select_related('author', 'category')[:6]

        context = {
            'recipe': recipe,
            'recommended_recipes': recommended_recipes,
            'user_review': user_review,
            'meta_description': recipe.description[:160] if recipe.description else ''
        }
        return render(request, 'recipes/recipe_detail.html', context)


class CategoryListView(View):
    def get(self, request):
        categories = Category.objects.annotate(
            recipe_count=Count('recipes'),
            latest_recipe=Max('recipes__created_at')
        ).order_by('name')
        
        context = {'categories': categories}
        return render(request, 'recipes/categories.html', context)

class CategoryDetailView(View):
    def get(self, request, slug):
        category = get_object_or_404(
            Category.objects.prefetch_related(
                Prefetch(
                    'recipes',
                    queryset=Recipe.objects.select_related('author', 'category')
                )
            ),
            slug=slug
        )
        
        recipes = category.recipes.order_by('-created_at')
        paginator = Paginator(recipes, 6)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'category': category,
            'page_obj': page_obj,
            'meta_title': f"{category.name} Recipes"
        }
        return render(request, 'recipes/category_detail.html', context)


class RecipeCreateView(LoginRequiredMixin, CreateView):
    model = Recipe
    form_class = RecipeForm
    template_name = 'recipes/recipe_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['ingredient_formset'] = IngredientFormSet(
                self.request.POST, 
                prefix='ingredients'
            )
            context['instruction_formset'] = InstructionFormSet(
                self.request.POST,
                prefix='instructions'
            )
        else:
            context['ingredient_formset'] = IngredientFormSet(prefix='ingredients')
            context['instruction_formset'] = InstructionFormSet(prefix='instructions')
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        ingredient_formset = context['ingredient_formset']
        instruction_formset = context['instruction_formset']

        if not all([ingredient_formset.is_valid(), instruction_formset.is_valid()]):
            return self.render_to_response(context)

        try:
            with transaction.atomic():
                self.object = form.save(commit=False)
                self.object.author = self.request.user  # обязательно до save()
                self.object.save()

                # Привязываем рецепт к формсетам
                ingredient_formset.instance = self.object
                instruction_formset.instance = self.object

                # Сохраняем ингредиенты
                ingredient_formset.save()

                # Сохраняем инструкции с автонумерацией
                instructions = instruction_formset.save(commit=False)
                for i, instruction in enumerate(instructions):
                    instruction.step_number = i + 1
                    instruction.recipe = self.object  
                    instruction.save()

                messages.success(self.request, "The recipe was created successfully")
                return redirect(self.get_success_url())

        except Exception as e:
            messages.error(self.request, f"Error saving recipe: {str(e)}")
            return self.form_invalid(form)


    def get_success_url(self):
        return reverse_lazy('recipes:recipe-detail', kwargs={'slug': self.object.slug})

@login_required
def favorites_list(request):
    user = request.user
    return render(request, 'recipes/favorites_list.html', {
        'user': user
    })

@login_required
@require_POST
def toggle_favorite(request, slug):
    recipe = get_object_or_404(Recipe, slug=slug)
    if request.user.is_authenticated:
        if recipe in request.user.favorite_recipes.all():
            request.user.favorite_recipes.remove(recipe)
        else:
            request.user.favorite_recipes.add(recipe)
        
        return render(request, 'recipes/favorite_button.html', {
            'recipe': recipe,
            'user': request.user
        })
    return HttpResponseForbidden()


class ReviewCreateView(LoginRequiredMixin, CreateView):
    model = Review
    form_class = ReviewForm

    def get_success_url(self):
        return reverse('recipes:recipe-detail', kwargs={'slug': self.recipe.slug})

    def dispatch(self, request, *args, **kwargs):
        self.recipe = get_object_or_404(Recipe, slug=kwargs['slug'])
        if Review.objects.filter(recipe=self.recipe, user=request.user).exists():
            return redirect('recipes:review-edit', 
                         pk=Review.objects.get(recipe=self.recipe, 
                                             user=request.user).pk)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            form.instance.user = self.request.user
            form.instance.recipe = self.recipe
            return super().form_valid(form)
        except IntegrityError:
            messages.error(self.request, "You've already reviewed this recipe!")
            return redirect(self.recipe.get_absolute_url())

class ReviewUpdateView(LoginRequiredMixin, UpdateView):
    model = Review
    form_class = ReviewForm
    template_name = 'recipes/review_form.html'

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "The review was updated successfully")
        return super().form_valid(form)

    def get_success_url(self):
        return self.object.recipe.get_absolute_url()

class ReviewDeleteView(LoginRequiredMixin, DeleteView):
    model = Review
    template_name = 'recipes/review_confirm_delete.html'

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "The review was deleted successfully")
        return super().delete(request, *args, **kwargs)

    def get_success_url(self):
        return self.object.recipe.get_absolute_url()
    