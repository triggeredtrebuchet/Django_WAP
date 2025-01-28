const autocompleteUrl = document.getElementById('autocomplete').getAttribute('data-url');
function initializeAutocomplete() {
    $('.autocomplete').autocomplete({
        source: function (request, response) {
            $.ajax({
                url: autocompleteUrl,
                data: { term: request.term },
                dataType: "xml",
                success: function (data) {
                    const ingredients = [];
                    $(data)
                        .find('ingredient')
                        .each(function () {
                            const id = parseInt($(this).attr('id'), 10);
                            const label = $(this).text();
                            const unit = $(this).attr('unit');
                            ingredients.push({ id: id, label: label, unit: unit });
                        });
                    response(ingredients);
                },
                error: function () {
                    alert("Error fetching autocomplete data.");
                }
            });
        },
        minLength: 1,
        select: function (event, ui) {
            const row = $(this).closest('tr');
            row.find(".ingredient-unit-input").val(ui.item.unit);
            const firstInput = row.find('td:first-child input:first'); // Get the first input in the first <td>
            firstInput.prop('readonly', true);
            row.find('input[name$="-ingredient"]').val(ui.item.id);
            row.find('.ingredient-id-placeholder').val(ui.item.id)
        }
    });
}

document.addEventListener('DOMContentLoaded', function () {
    initializeAutocomplete();
    const addMoreBtn = document.getElementById('add-ingredient-button')
    const totalNewForms = document.getElementById('id_recipe_ingredients-TOTAL_FORMS')

    addMoreBtn.addEventListener('click', add_new_form)
    function add_new_form(event) {
        if (event) {
            event.preventDefault()
        }
        const currentIngredientsForms = document.getElementsByClassName('ingredient-row')
        const currentFormCount = currentIngredientsForms.length
        const formCopyTarget = document.getElementById('ingredient-table')
        const emptyFormEl = document.getElementById('empty-ingredient').cloneNode(true)
        emptyFormEl.setAttribute('class', 'ingredient-row')
        emptyFormEl.setAttribute('id', `form-${currentFormCount}`)
        emptyFormEl.setAttribute('style', '')
        const regex = new RegExp('__prefix__', 'g')
        emptyFormEl.innerHTML = emptyFormEl.innerHTML.replace(regex, currentFormCount)
        totalNewForms.setAttribute('value', currentFormCount + 1)
        formCopyTarget.append(emptyFormEl)
        initializeAutocomplete()
    }

    // Delete a form (mark it for deletion)
    document.getElementById('ingredient-table').addEventListener('click', function (e) {
        if (e.target && e.target.classList.contains('delete-row')) {
            const row = e.target.closest('.ingredient-row');
            const deleteField = row.querySelector('.delete-field input');
            if (deleteField) {
                deleteField.checked = 'true'; // Mark the form for deletion
                row.style.display = 'none'; // Hide the row
            }
        }
    });
});
