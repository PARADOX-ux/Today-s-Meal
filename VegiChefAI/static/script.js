// Global variables
let selectedIngredients = new Set();
let currentRecipes = [];
let showingFavorites = false;

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    loadFavorites();
    setupEventListeners();
    updateSelectedIngredientsDisplay();
});

function setupEventListeners() {
    // Ingredient checkbox listeners
    document.querySelectorAll('.ingredient-checkbox').forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            if (this.checked) {
                selectedIngredients.add(this.value);
            } else {
                selectedIngredients.delete(this.value);
            }
            updateSelectedIngredientsDisplay();
        });
    });

    // Manual ingredient input listener
    document.getElementById('manual-ingredient').addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            addManualIngredient();
        }
    });
}

function addManualIngredient() {
    const input = document.getElementById('manual-ingredient');
    const ingredient = input.value.trim().toLowerCase();
    
    if (ingredient && !selectedIngredients.has(ingredient)) {
        selectedIngredients.add(ingredient);
        input.value = '';
        updateSelectedIngredientsDisplay();
    }
}

function updateSelectedIngredientsDisplay() {
    const container = document.getElementById('selected-tags');
    
    if (selectedIngredients.size === 0) {
        container.innerHTML = '<span class="text-gray-400 text-sm">No ingredients selected yet...</span>';
        return;
    }
    
    const tags = Array.from(selectedIngredients).map(ingredient => 
        `<span class="inline-flex items-center px-3 py-1 rounded-full text-sm bg-saffron-100 text-saffron-800 border border-saffron-200">
            <span class="capitalize">${ingredient}</span>
            <button onclick="removeIngredient('${ingredient}')" class="ml-2 text-saffron-600 hover:text-saffron-800">
                <i class="fas fa-times text-xs"></i>
            </button>
        </span>`
    ).join('');
    
    container.innerHTML = tags;
}

function removeIngredient(ingredient) {
    selectedIngredients.delete(ingredient);
    
    // Also uncheck the corresponding checkbox if it exists
    const checkbox = document.querySelector(`.ingredient-checkbox[value="${ingredient}"]`);
    if (checkbox) {
        checkbox.checked = false;
    }
    
    updateSelectedIngredientsDisplay();
}

function getFilters() {
    return {
        no_onion_garlic: document.getElementById('no-onion-garlic').checked,
        jain: document.getElementById('jain').checked,
        satvik: document.getElementById('satvik').checked,
        quick: document.getElementById('quick').checked,
        healthy: document.getElementById('healthy').checked
    };
}

function searchRecipes() {
    if (selectedIngredients.size === 0) {
        showMessage('Please select at least one ingredient!', 'error');
        return;
    }

    showingFavorites = false;
    document.getElementById('favorites-button-text').textContent = 'View Favorites';
    document.getElementById('favorites-section').classList.add('hidden');

    const ingredients = Array.from(selectedIngredients);
    const filters = getFilters();
    const mealType = document.getElementById('meal-type').value;

    // Show loading
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('results-section').classList.add('hidden');

    fetch('/search_recipes', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            ingredients: ingredients,
            filters: filters,
            meal_type: mealType
        })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('loading').classList.add('hidden');
        
        if (data.error) {
            showMessage(data.error, 'error');
            return;
        }

        currentRecipes = data.recipes || [];
        displayRecipes(currentRecipes, data.message);
        
        // Check favorite status for displayed recipes
        const recipeNames = currentRecipes.map(recipe => recipe.name);
        setTimeout(() => checkFavoriteStatus(recipeNames), 100);
    })
    .catch(error => {
        document.getElementById('loading').classList.add('hidden');
        console.error('Error:', error);
        showMessage('An error occurred while searching for recipes. Please try again.', 'error');
    });
}

function displayRecipes(recipes, message) {
    const resultsSection = document.getElementById('results-section');
    const messageDiv = document.getElementById('results-message');
    const resultsDiv = document.getElementById('recipe-results');

    // Show message
    if (message) {
        messageDiv.innerHTML = `
            <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
                <i class="fas fa-check-circle mr-2"></i>${message}
            </div>
        `;
    }

    if (recipes.length === 0) {
        resultsDiv.innerHTML = `
            <div class="col-span-full text-center py-8">
                <i class="fas fa-search text-4xl text-gray-400 mb-4"></i>
                <p class="text-gray-600">No recipes found. Try adding more ingredients or adjusting your filters.</p>
            </div>
        `;
    } else {
        resultsDiv.innerHTML = recipes.map(recipe => createRecipeCard(recipe)).join('');
    }

    resultsSection.classList.remove('hidden');
}

function createRecipeCard(recipe) {
    const isFavorite = isRecipeFavorite(recipe.name);
    const heartIcon = isFavorite ? 'fas fa-heart text-pink-500' : 'far fa-heart text-gray-400';
    
    return `
        <div class="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition duration-300">
            <div class="p-6">
                <div class="flex justify-between items-start mb-3">
                    <h3 class="text-lg font-semibold text-gray-800">${recipe.name}</h3>
                    <button onclick="toggleFavorite('${recipe.name}')" class="hover:scale-110 transition duration-200">
                        <i class="${heartIcon} text-xl"></i>
                    </button>
                </div>
                
                <div class="flex items-center gap-4 mb-4 text-sm text-gray-600">
                    <span><i class="fas fa-clock text-saffron-500 mr-1"></i>${recipe.time}</span>
                    <span><i class="fas fa-percentage text-indianGreen-500 mr-1"></i>${recipe.match_percentage}% match</span>
                    <span><i class="fas fa-tag text-blue-500 mr-1"></i>${recipe.type}</span>
                </div>

                ${recipe.missing_ingredients.length > 0 ? `
                    <div class="mb-4">
                        <p class="text-sm text-gray-700 mb-2">
                            <i class="fas fa-exclamation-triangle text-yellow-500 mr-1"></i>
                            Missing ingredients:
                        </p>
                        <div class="flex flex-wrap gap-1">
                            ${recipe.missing_ingredients.map(ing => 
                                `<span class="px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded">${ing}</span>`
                            ).join('')}
                        </div>
                    </div>
                ` : `
                    <div class="mb-4">
                        <p class="text-sm text-green-700">
                            <i class="fas fa-check-circle text-green-500 mr-1"></i>
                            You have all ingredients!
                        </p>
                    </div>
                `}

                ${recipe.tags.length > 0 ? `
                    <div class="mb-4">
                        <div class="flex flex-wrap gap-1">
                            ${recipe.tags.map(tag => 
                                `<span class="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">${tag}</span>`
                            ).join('')}
                        </div>
                    </div>
                ` : ''}

                <div class="mb-4">
                    <p class="text-sm text-gray-700 font-medium mb-2">Quick Steps:</p>
                    <ol class="text-sm text-gray-600 space-y-1">
                        ${recipe.steps.slice(0, 3).map((step, index) => 
                            `<li>${index + 1}. ${step}</li>`
                        ).join('')}
                        ${recipe.steps.length > 3 ? `<li class="text-gray-500">...and ${recipe.steps.length - 3} more steps</li>` : ''}
                    </ol>
                </div>

                <button onclick="getAICookingInstructions('${recipe.name}', ${JSON.stringify(Array.from(selectedIngredients)).replace(/"/g, '&quot;')}, ${JSON.stringify(recipe.ingredients).replace(/"/g, '&quot;')})" 
                        class="w-full bg-gradient-to-r from-saffron-500 to-saffron-600 text-white py-2 px-4 rounded-lg font-medium hover:from-saffron-600 hover:to-saffron-700 transition duration-200">
                    <i class="fas fa-robot mr-2"></i>Cook This with AI Guide
                </button>
            </div>
        </div>
    `;
}

function getAICookingInstructions(recipeName, userIngredients, recipeIngredients) {
    // Show loading in modal
    document.getElementById('ai-modal').classList.remove('hidden');
    document.getElementById('ai-content').innerHTML = `
        <div class="text-center py-8">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-saffron-500"></div>
            <p class="mt-2 text-gray-600">Getting AI cooking instructions for ${recipeName}...</p>
        </div>
    `;

    fetch('/get_ai_instructions', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            recipe_name: recipeName,
            user_ingredients: userIngredients,
            recipe_ingredients: recipeIngredients
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            document.getElementById('ai-content').innerHTML = `
                <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                    <i class="fas fa-exclamation-triangle mr-2"></i>${data.error}
                </div>
            `;
            return;
        }

        displayAIInstructions(recipeName, data.instructions);
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('ai-content').innerHTML = `
            <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                <i class="fas fa-exclamation-triangle mr-2"></i>Failed to get AI instructions. Please try again.
            </div>
        `;
    });
}

function displayAIInstructions(recipeName, instructions) {
    const content = document.getElementById('ai-content');
    
    let html = `<h4 class="text-lg font-semibold text-gray-800 mb-4">${recipeName}</h4>`;
    
    if (instructions.instructions && instructions.instructions.length > 0) {
        html += `
            <div class="mb-6">
                <h5 class="font-semibold text-gray-800 mb-3">
                    <i class="fas fa-list-ol text-saffron-500 mr-2"></i>Step-by-Step Instructions:
                </h5>
                <ol class="space-y-2">
                    ${instructions.instructions.map((step, index) => 
                        `<li class="flex">
                            <span class="flex-shrink-0 w-6 h-6 bg-saffron-500 text-white rounded-full text-sm flex items-center justify-center mr-3 mt-1">${index + 1}</span>
                            <span class="text-gray-700">${step}</span>
                        </li>`
                    ).join('')}
                </ol>
            </div>
        `;
    }
    
    if (instructions.substitutions && instructions.substitutions.length > 0) {
        html += `
            <div class="mb-6">
                <h5 class="font-semibold text-gray-800 mb-3">
                    <i class="fas fa-exchange-alt text-indianGreen-500 mr-2"></i>Ingredient Substitutions:
                </h5>
                <ul class="space-y-2">
                    ${instructions.substitutions.map(sub => 
                        `<li class="flex items-start">
                            <i class="fas fa-arrow-right text-indianGreen-500 mr-2 mt-1"></i>
                            <span class="text-gray-700">${sub}</span>
                        </li>`
                    ).join('')}
                </ul>
            </div>
        `;
    }
    
    if (instructions.tips && instructions.tips.length > 0) {
        html += `
            <div class="mb-6">
                <h5 class="font-semibold text-gray-800 mb-3">
                    <i class="fas fa-lightbulb text-yellow-500 mr-2"></i>Pro Tips:
                </h5>
                <ul class="space-y-2">
                    ${instructions.tips.map(tip => 
                        `<li class="flex items-start">
                            <i class="fas fa-star text-yellow-500 mr-2 mt-1"></i>
                            <span class="text-gray-700">${tip}</span>
                        </li>`
                    ).join('')}
                </ul>
            </div>
        `;
    }
    
    if (instructions.cultural_context) {
        html += `
            <div class="mb-6">
                <h5 class="font-semibold text-gray-800 mb-3">
                    <i class="fas fa-info-circle text-blue-500 mr-2"></i>Cultural Context:
                </h5>
                <p class="text-gray-700 bg-blue-50 p-3 rounded-lg">${instructions.cultural_context}</p>
            </div>
        `;
    }
    
    if (instructions.serving_suggestions && instructions.serving_suggestions.length > 0) {
        html += `
            <div class="mb-6">
                <h5 class="font-semibold text-gray-800 mb-3">
                    <i class="fas fa-utensils text-pink-500 mr-2"></i>Serving Suggestions:
                </h5>
                <ul class="space-y-2">
                    ${instructions.serving_suggestions.map(suggestion => 
                        `<li class="flex items-start">
                            <i class="fas fa-heart text-pink-500 mr-2 mt-1"></i>
                            <span class="text-gray-700">${suggestion}</span>
                        </li>`
                    ).join('')}
                </ul>
            </div>
        `;
    }
    
    content.innerHTML = html;
}

function closeAIModal() {
    document.getElementById('ai-modal').classList.add('hidden');
}

function resetFilters() {
    // Clear selected ingredients
    selectedIngredients.clear();
    
    // Uncheck all ingredient checkboxes
    document.querySelectorAll('.ingredient-checkbox').forEach(checkbox => {
        checkbox.checked = false;
    });
    
    // Clear manual ingredient input
    document.getElementById('manual-ingredient').value = '';
    
    // Reset filters
    document.getElementById('meal-type').value = 'All';
    document.querySelectorAll('input[type="checkbox"]').forEach(checkbox => {
        if (checkbox.classList.contains('ingredient-checkbox')) return; // Skip ingredient checkboxes
        checkbox.checked = false;
    });
    
    // Update display
    updateSelectedIngredientsDisplay();
    
    // Hide results
    document.getElementById('results-section').classList.add('hidden');
    document.getElementById('favorites-section').classList.add('hidden');
    
    // Reset favorites view
    showingFavorites = false;
    document.getElementById('favorites-button-text').textContent = 'View Favorites';
    
    showMessage('Filters reset successfully!', 'success');
}

function showMessage(message, type) {
    const messageDiv = document.getElementById('results-message');
    const bgColor = type === 'error' ? 'bg-red-100 border-red-400 text-red-700' : 'bg-green-100 border-green-400 text-green-700';
    const icon = type === 'error' ? 'fas fa-exclamation-triangle' : 'fas fa-check-circle';
    
    messageDiv.innerHTML = `
        <div class="${bgColor} border px-4 py-3 rounded">
            <i class="${icon} mr-2"></i>${message}
        </div>
    `;
    
    document.getElementById('results-section').classList.remove('hidden');
    document.getElementById('recipe-results').innerHTML = '';
}

// Favorites functionality
function loadFavorites() {
    const favorites = localStorage.getItem('favoriteRecipes');
    return favorites ? JSON.parse(favorites) : [];
}

function saveFavorites(favorites) {
    localStorage.setItem('favoriteRecipes', JSON.stringify(favorites));
}

function isRecipeFavorite(recipeName) {
    // This will be updated by checking with the server
    // For now, return false and let updateHeartIcons handle the check
    return false;
}

function checkFavoriteStatus(recipeNames) {
    if (recipeNames.length === 0) return;
    
    fetch('/check_favorites', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            recipe_names: recipeNames
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            console.error('Error checking favorites:', data.error);
            return;
        }
        
        const favoritedNames = data.favorited_recipes || [];
        
        // Update heart icons based on server response
        const recipeCards = document.querySelectorAll('#recipe-results .bg-white, #favorites-results .bg-white');
        recipeCards.forEach(card => {
            const title = card.querySelector('h3').textContent;
            const heartButton = card.querySelector('button i');
            const isFavorite = favoritedNames.includes(title);
            
            heartButton.className = isFavorite ? 'fas fa-heart text-pink-500 text-xl' : 'far fa-heart text-gray-400 text-xl';
        });
    })
    .catch(error => {
        console.error('Error checking favorites:', error);
    });
}

function toggleFavorite(recipeName) {
    fetch('/toggle_favorite', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            recipe_name: recipeName
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showMessage(data.error, 'error');
            return;
        }
        
        if (data.is_favorite) {
            showMessage(`Added "${recipeName}" to favorites`, 'success');
        } else {
            showMessage(`Removed "${recipeName}" from favorites`, 'success');
        }
        
        // Update heart icons in current view
        const recipeNames = showingFavorites ? [] : currentRecipes.map(recipe => recipe.name);
        if (recipeNames.length > 0) {
            setTimeout(() => checkFavoriteStatus(recipeNames), 100);
        }
        
        // If viewing favorites, refresh the favorites view
        if (showingFavorites) {
            setTimeout(() => {
                displayFavoriteRecipes();
            }, 1000);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showMessage('Failed to update favorites', 'error');
    });
}

function updateHeartIcons() {
    // Update all heart icons in the current view
    const recipeCards = document.querySelectorAll('#recipe-results .bg-white, #favorites-results .bg-white');
    recipeCards.forEach(card => {
        const title = card.querySelector('h3').textContent;
        const heartButton = card.querySelector('button i');
        const isFavorite = isRecipeFavorite(title);
        
        heartButton.className = isFavorite ? 'fas fa-heart text-pink-500 text-xl' : 'far fa-heart text-gray-400 text-xl';
    });
}

function toggleFavorites() {
    if (showingFavorites) {
        // Switch back to search results
        showingFavorites = false;
        document.getElementById('favorites-button-text').textContent = 'View Favorites';
        document.getElementById('favorites-section').classList.add('hidden');
        if (currentRecipes.length > 0) {
            document.getElementById('results-section').classList.remove('hidden');
        }
    } else {
        // Show favorites
        showingFavorites = true;
        document.getElementById('favorites-button-text').textContent = 'Back to Results';
        document.getElementById('results-section').classList.add('hidden');
        displayFavoriteRecipes();
    }
}

function displayFavoriteRecipes() {
    const favoritesSection = document.getElementById('favorites-section');
    const favoritesResults = document.getElementById('favorites-results');
    
    // Show loading
    favoritesResults.innerHTML = `
        <div class="col-span-full text-center py-8">
            <div class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-saffron-500"></div>
            <p class="mt-2 text-gray-600">Loading your favorites...</p>
        </div>
    `;
    
    fetch('/get_favorites')
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            favoritesResults.innerHTML = `
                <div class="col-span-full text-center py-8">
                    <i class="fas fa-exclamation-triangle text-4xl text-red-400 mb-4"></i>
                    <p class="text-red-600">${data.error}</p>
                </div>
            `;
            return;
        }
        
        const favoriteRecipes = data.recipes || [];
        
        if (favoriteRecipes.length === 0) {
            favoritesResults.innerHTML = `
                <div class="col-span-full text-center py-8">
                    <i class="fas fa-heart text-4xl text-gray-400 mb-4"></i>
                    <p class="text-gray-600">No favorite recipes yet. Start exploring and save some recipes!</p>
                </div>
            `;
        } else {
            favoritesResults.innerHTML = favoriteRecipes.map(recipe => createRecipeCard(recipe)).join('');
        }
    })
    .catch(error => {
        console.error('Error loading favorites:', error);
        favoritesResults.innerHTML = `
            <div class="col-span-full text-center py-8">
                <i class="fas fa-exclamation-triangle text-4xl text-red-400 mb-4"></i>
                <p class="text-red-600">Failed to load favorites</p>
            </div>
        `;
    });
    
    favoritesSection.classList.remove('hidden');
}

// Close modal when clicking outside
document.getElementById('ai-modal').addEventListener('click', function(e) {
    if (e.target === this) {
        closeAIModal();
    }
});
