document.addEventListener('DOMContentLoaded', () => {
    window.ingredientTotal = document.getElementById('id_ingredients-TOTAL_FORMS');
    window.ingredientIndex = parseInt(ingredientTotal.value) || 0;
    
    window.instructionTotal = document.getElementById('id_instructions-TOTAL_FORMS');
    window.instructionIndex = parseInt(instructionTotal.value) || 0;
});

function updateFormIndices(formElement, prefix) {
    const newIndex = window[`${prefix}Index`];
    const regex = new RegExp(`${prefix}-(\\d+)-`, 'g');
    
    formElement.querySelectorAll('[name], [id]').forEach(element => {
        if (element.name) element.name = element.name.replace(regex, `${prefix}-${newIndex}-`);
        if (element.id) element.id = element.id.replace(regex, `${prefix}-${newIndex}-`);
    });
}

function addIngredientForm() {
    const forms = document.querySelectorAll('.ingredient-form');
    const template = forms[forms.length - 1].cloneNode(true);
    
    template.querySelectorAll('input').forEach(input => {
        input.value = '';
        input.classList.remove('border-red-500');
    });
    template.querySelectorAll('.text-red-500').forEach(error => error.remove());
    
    updateFormIndices(template, 'ingredients');
    document.getElementById('ingredients-formset').appendChild(template);
    window.ingredientTotal.value = ++window.ingredientIndex;
}

function addInstructionForm() {
    const forms = document.querySelectorAll('.instruction-form');
    const template = forms[forms.length - 1].cloneNode(true);
    
    template.querySelector('textarea').value = '';
    template.querySelectorAll('.text-red-500').forEach(error => error.remove());
    
    template.querySelectorAll('input[type="hidden"]').forEach(input => input.remove());
    
    updateFormIndices(template, 'instructions');
    document.getElementById('instructions-formset').appendChild(template);
    window.instructionTotal.value = ++window.instructionIndex;
    
    const steps = document.querySelectorAll('.instruction-form span');
    steps.forEach((span, index) => {
        span.textContent = `Step ${index + 1}`;
    });
}