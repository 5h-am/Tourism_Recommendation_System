let selectedAttractions = new Set();
let cities = [];
let countries = [];
let categories = [];
let citiesByCountry = {};
let map = null;
let markers = [];

const STORAGE_KEYS = {
    SELECTED_ATTRACTIONS: 'selectedAttractions',
    PREFERENCES: 'userPreferences',
};

async function loadInitialData() {
    try {
        const destResponse = await fetch('/api/destinations');
        const destData = await destResponse.json();
        cities = destData.cities || [];
        countries = destData.countries || [];
        citiesByCountry = destData.citiesByCountry || {};

        const citySelect = document.getElementById('city');
        cities.forEach((city) => {
            const option = document.createElement('option');
            option.value = city;
            option.textContent = city;
            citySelect.appendChild(option);
        });

        const countrySelect = document.getElementById('country');
        countries.forEach((country) => {
            const option = document.createElement('option');
            option.value = country;
            option.textContent = country;
            countrySelect.appendChild(option);
        });

        countrySelect.addEventListener('change', onCountryChange);

        const catResponse = await fetch('/api/categories');
        const catData = await catResponse.json();
        categories = catData.categories || [];

        const categoriesGroup = document.getElementById('categoriesGroup');
        categoriesGroup.innerHTML = '';
        categories.forEach((category) => {
            const label = document.createElement('label');
            label.innerHTML = `<input type="checkbox" value="${category}" class="category-checkbox"> ${category}`;
            categoriesGroup.appendChild(label);
        });

        loadPreferences();
        loadSelectedAttractions();
    } catch (error) {
        console.error('Error loading initial data:', error);
        document.getElementById('categoriesGroup').innerHTML =
            '<div class="error-message">Error loading categories. Please refresh the page.</div>';
    }
}

function savePreferences() {
    const preferences = {
        city: document.getElementById('city').value,
        country: document.getElementById('country').value,
        minRating: document.getElementById('minRating').value,
        limit: document.getElementById('limit').value,
        categories: Array.from(document.querySelectorAll('.category-checkbox:checked'))
            .map(cb => cb.value)
    };
    
    try {
        localStorage.setItem(STORAGE_KEYS.PREFERENCES, JSON.stringify(preferences));
    } catch (error) {
        console.error('Error saving preferences:', error);
    }
}

function loadPreferences() {
    try {
        const saved = localStorage.getItem(STORAGE_KEYS.PREFERENCES);
        if (!saved) return;
        
        const preferences = JSON.parse(saved);
        document.getElementById('country').value = preferences.country || 'any';

        if (typeof onCountryChange === 'function') {
            onCountryChange();
        }

        document.getElementById('city').value = preferences.city || 'any';
        document.getElementById('minRating').value = preferences.minRating || '4.0';
        document.getElementById('limit').value = preferences.limit || '10';
        
        if (preferences.categories) {
            preferences.categories.forEach(cat => {
                const checkbox = document.querySelector(`.category-checkbox[value="${cat}"]`);
                if (checkbox) checkbox.checked = true;
            });
        }
    } catch (error) {
        console.error('Error loading preferences:', error);
    }
}

function onCountryChange() {
    const selectedCountry = document.getElementById('country').value;
    const citySelect = document.getElementById('city');

    citySelect.innerHTML = '<option value="any">Any City</option>';

    if (selectedCountry === 'any') {
        cities.forEach((city) => {
            const option = document.createElement('option');
            option.value = city;
            option.textContent = city;
            citySelect.appendChild(option);
        });
    } else {
        const countryCities = citiesByCountry[selectedCountry] || [];
        countryCities.forEach((city) => {
            const option = document.createElement('option');
            option.value = city;
            option.textContent = city;
            citySelect.appendChild(option);
        });
    }

    citySelect.value = 'any';
}

function saveSelectedAttractions() {
    try {
        localStorage.setItem(STORAGE_KEYS.SELECTED_ATTRACTIONS, JSON.stringify(Array.from(selectedAttractions)));
    } catch (error) {
        console.error('Error saving selected attractions:', error);
    }
}

function loadSelectedAttractions() {
    try {
        const saved = localStorage.getItem(STORAGE_KEYS.SELECTED_ATTRACTIONS);
        if (!saved) return;
        
        const ids = JSON.parse(saved);
        selectedAttractions = new Set(ids.map(id => parseInt(id)));
        
        if (selectedAttractions.size > 0) {
            document.getElementById('selectedCount').textContent = selectedAttractions.size;
            document.getElementById('optimizeSection').style.display = 'block';
        }
    } catch (error) {
        console.error('Error loading selected attractions:', error);
    }
}

function updateSelectedCount() {
    document.getElementById('selectedCount').textContent = selectedAttractions.size;
    document.getElementById('optimizeSection').style.display = 
        selectedAttractions.size > 0 ? 'block' : 'none';
}

async function getWeather(city, country, elementId) {
    const weatherContainer = document.getElementById(elementId);
    const originalContent = weatherContainer.innerHTML;
    
    weatherContainer.innerHTML = '<div class="weather-loading">Loading weather...</div>';
    
    try {
        const response = await fetch('/api/weather', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ city, country })
        });
        
        if (!response.ok) {
            throw new Error('Weather not available');
        }
        
        const weather = await response.json();
        displayWeather(weather, weatherContainer);
        
    } catch (error) {
        weatherContainer.innerHTML = '<div class="error-message" style="font-size: 0.9em;">Weather data not available</div>';
        console.error('Error fetching weather:', error);
    }
}

function displayWeather(weather, container) {
    const condition = weather.condition || 'unknown';
    const temp = weather.temperature || 0;
    const windSpeed = weather.windspeed || 0;
    
    const weatherEmojis = {
        'clear': '☀️',
        'partly_cloudy': '🌤️',
        'cloudy': '☁️',
        'rain': '🌧️',
        'drizzle': '🌦️',
        'snow': '🌨️',
        'thunderstorm': '⛈️',
        'foggy': '🌫️',
        'unknown': '❓'
    };
    
    const emoji = weatherEmojis[condition] || weatherEmojis['unknown'];
    const tempClass = temp < 10 ? 'cold' : temp > 25 ? 'hot' : '';
    
    container.innerHTML = `
        <div class="weather-card">
            <h5>🌤️ Weather in ${weather.city}, ${weather.country}</h5>
            <div class="weather-info">
                <div class="weather-item">
                    <span class="weather-icon">${emoji}</span>
                    <span class="temperature ${tempClass}">${temp.toFixed(1)}°C</span>
                </div>
                <div class="weather-item">
                    <strong>Condition:</strong> ${condition.replace('_', ' ')}
                </div>
                <div class="weather-item">
                    <strong>Wind:</strong> ${windSpeed.toFixed(1)} km/h
                </div>
            </div>
        </div>
    `;
}

async function getRecommendations() {
    const city = document.getElementById('city').value;
    const country = document.getElementById('country').value;
    const minRating = parseFloat(document.getElementById('minRating').value) || 0;
    const limit = parseInt(document.getElementById('limit').value) || 10;
    const selectedCategories = Array.from(document.querySelectorAll('.category-checkbox:checked'))
        .map(cb => cb.value);
    
    savePreferences();
    
    const container = document.getElementById('recommendations');
    const recommendBtn = document.getElementById('recommendBtn');
    
    container.innerHTML = '<div class="loading">🔍 Finding your perfect attractions</div>';
    recommendBtn.disabled = true;
    
    try {
        const response = await fetch('/api/recommend', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                city: city === 'any' ? null : city,
                country: country === 'any' ? null : country,
                min_rating: minRating,
                categories: selectedCategories,
                limit: limit
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to get recommendations');
        }
        
        const recommendations = await response.json();
        displayRecommendations(recommendations);
    } catch (error) {
        container.innerHTML = '<div class="error-message">❌ Error loading recommendations. Please try again.</div>';
        console.error('Error:', error);
    } finally {
        recommendBtn.disabled = false;
    }
}

function displayRecommendations(recommendations) {
    const container = document.getElementById('recommendations');
    
    if (!recommendations || recommendations.length === 0) {
        container.innerHTML = '<div class="error-message">No attractions found. Try different preferences!</div>';
        return;
    }
    
    container.innerHTML = recommendations.map(att => {
        const isSelected = selectedAttractions.has(att.id);
        const stars = '★'.repeat(Math.floor(att.rating)) + (att.rating % 1 >= 0.5 ? '½' : '');
        const reviewCount = att.review_count.toLocaleString();
        const weatherId = `weather-${att.id}`;
        
        const categoryTags = att.categories.map(cat => 
            `<span class="category-tag">${cat}</span>`
        ).join('');
        
        return `
            <div class="attraction-card ${isSelected ? 'selected-card' : ''}" id="card-${att.id}" onclick="toggleAttraction(${att.id})">
                <h3>${att.place_name}</h3>
                <p><strong>📍 Location:</strong> ${att.city}, ${att.country}</p>
                <div class="star-rating">${stars}</div>
                <p><strong>⭐ Rating:</strong> ${att.rating.toFixed(1)} / 5.0</p>
                <p><strong>💬 Reviews:</strong> ${reviewCount}</p>
                <div style="margin: 10px 0;">
                    <strong>🏷️ Categories:</strong>
                    <div style="margin-top: 5px;">${categoryTags || '<em>No categories</em>'}</div>
                </div>
                <div class="score-badge">Match Score: ${att.score.toFixed(1)}/100</div>
                ${att.score_breakdown ? `
                    <div class="score-breakdown">
                        <div class="score-breakdown-title">Score Breakdown:</div>
                        Base: ${att.score_breakdown.base_score.toFixed(1)} | 
                        Location: +${att.score_breakdown.location_bonus.toFixed(1)} | 
                        Categories: +${att.score_breakdown.category_bonus.toFixed(1)} | 
                        Quality: +${att.score_breakdown.quality_bonus.toFixed(1)} | 
                        Popularity: +${att.score_breakdown.popularity_bonus.toFixed(1)}
                    </div>
                ` : ''}
                <button class="weather-btn" onclick="event.stopPropagation(); getWeather('${att.city}', '${att.country}', '${weatherId}')">
                    🌤️ Check Weather
                </button>
                <div id="${weatherId}"></div>
                <button class="add-btn" onclick="event.stopPropagation(); toggleAttraction(${att.id})">
                    ${isSelected ? '✓ Selected' : '+ Add to Itinerary'}
                </button>
            </div>
        `;
    }).join('');

    const attractionsWithCoords = recommendations.filter(
        (att) => typeof att.latitude === 'number' && typeof att.longitude === 'number',
    );

    if (attractionsWithCoords.length > 0) {
        showAttractionsOnMap(attractionsWithCoords);
    } else {
        const mapSection = document.getElementById('mapSection');
        if (mapSection) {
            mapSection.style.display = 'none';
        }
    }
}

function initializeMap() {
    if (!map && typeof L !== 'undefined') {
        map = L.map('map').setView([20, 0], 2);
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            maxZoom: 18,
        }).addTo(map);
    }
}

function showAttractionsOnMap(attractions) {
    if (!map) {
        initializeMap();
    }
    if (!map) {
        return;
    }

    markers.forEach((marker) => map.removeLayer(marker));
    markers = [];

    const bounds = [];

    attractions.forEach((att) => {
        if (att.latitude && att.longitude) {
            const marker = L.marker([att.latitude, att.longitude]).bindPopup(`
                <div>
                    <h3>${att.place_name}</h3>
                    <p><strong>📍</strong> ${att.city}, ${att.country}</p>
                    <p><strong>⭐</strong> ${att.rating.toFixed(1)} / 5.0</p>
                    <p><strong>💬</strong> ${att.review_count.toLocaleString()} reviews</p>
                    <p><strong>Match Score:</strong> ${att.score.toFixed(1)}/100</p>
                </div>
            `);

            marker.addTo(map);
            markers.push(marker);
            bounds.push([att.latitude, att.longitude]);
        }
    });

    if (bounds.length > 0) {
        map.fitBounds(bounds, { padding: [50, 50] });
    }

    const mapSection = document.getElementById('mapSection');
    if (mapSection) {
        mapSection.style.display = 'block';
    }

    setTimeout(() => map.invalidateSize(), 100);
}

function toggleAttraction(id) {
    const card = document.getElementById(`card-${id}`);
    if (!card) return;
    
    if (selectedAttractions.has(id)) {
        selectedAttractions.delete(id);
        card.classList.remove('selected-card');
    } else {
        selectedAttractions.add(id);
        card.classList.add('selected-card');
    }
    
    localStorage.setItem(STORAGE_KEYS.SELECTED_ATTRACTIONS, JSON.stringify([...selectedAttractions]));
    updateSelectedCount();
    
    const button = card.querySelector('.add-btn');
    if (button) {
        button.textContent = selectedAttractions.has(id) ? '✓ Selected' : '+ Add to Itinerary';
    }
}

async function optimizeItinerary() {
    const days = parseInt(document.getElementById('days').value);
    
    if (!days || days <= 0) {
        alert('Please enter a valid number of days (at least 1)');
        return;
    }
    
    if (selectedAttractions.size === 0) {
        alert('Please select at least one attraction');
        return;
    }
    
    const container = document.getElementById('itinerary');
    container.innerHTML = '<div class="loading">✨ Optimizing your itinerary</div>';
    
    try {
        const response = await fetch('/api/optimize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                attractionIds: Array.from(selectedAttractions), 
                days: days
            })
        });
        
        if (!response.ok) {
            throw new Error('Failed to optimize itinerary');
        }
        
        const result = await response.json();
        displayItinerary(result);
    } catch (error) {
        container.innerHTML = '<div class="error-message">❌ Error optimizing itinerary. Please try again.</div>';
        console.error('Error:', error);
    }
}

function displayItinerary(result) {
    const container = document.getElementById('itinerary');
    
    if (result.error) {
        container.innerHTML = `<div class="error-message">❌ ${result.error}</div>`;
        return;
    }
    
    if (!result.itinerary || result.itinerary.length === 0) {
        container.innerHTML = '<div class="error-message">No itinerary generated. Please try again.</div>';
        return;
    }
    
    let html = `<div style="margin-top: 20px;">
        <p><strong>Total Attractions:</strong> ${result.total_attractions}</p>
        <p><strong>Cities to Visit:</strong> ${result.cities_visited.join(', ')}</p>
    </div>`;
    
    result.itinerary.forEach(day => {
        const uniqueCities = [...new Set(day.attractions.map(a => a.city))];
        const weatherId = `day-weather-${day.day}`;
        
        html += `
            <div class="itinerary-day">
                <h4>📅 Day ${day.day} ${uniqueCities.length > 0 ? `- ${uniqueCities.join(', ')}` : ''}</h4>
                <p><strong>Total Attractions:</strong> ${day.total_attractions} | 
                <strong>Estimated Time:</strong> ${day.total_hours} hours</p>
                ${uniqueCities.length > 0 ? `
                    <button class="weather-btn" onclick="getWeatherForDay('${uniqueCities[0]}', '${day.attractions[0].country}', '${weatherId}')">
                        🌤️ Check Weather
                    </button>
                    <div id="${weatherId}"></div>
                ` : ''}
                ${day.attractions.map(att => `
                    <div class="attraction-item">
                        <strong>${att.name}</strong><br>
                        <small>📍 ${att.city}, ${att.country}</small><br>
                        <small>⭐ ${att.rating.toFixed(1)} | 💬 ${att.review_count.toLocaleString()} reviews</small><br>
                        <small>⏱️ Estimated Time: ${att.estimated_time} hours</small><br>
                        <small>🏷️ ${att.categories.join(', ')}</small>
                    </div>
                `).join('')}
            </div>
        `;
    });
    
    container.innerHTML = html;
}

function getWeatherForDay(city, country, elementId) {
    getWeather(city, country, elementId);
}

function clearAllFilters() {
    localStorage.clear();
    
    document.getElementById('city').value = 'any';
    document.getElementById('country').value = 'any';
    document.getElementById('minRating').value = '4.0';
    document.getElementById('limit').value = '10';
    
    document.querySelectorAll('.category-checkbox').forEach(cb => cb.checked = false);
    
    selectedAttractions.clear();
    
    document.getElementById('recommendations').innerHTML = '';
    document.getElementById('optimizeSection').style.display = 'none';
    document.getElementById('selectedCount').textContent = '0';
    document.getElementById('itinerary').innerHTML = '';
    
    document.querySelectorAll('.attraction-card').forEach(card => {
        card.classList.remove('selected-card');
        const btn = card.querySelector('.add-btn');
        if (btn) btn.textContent = '+ Add to Itinerary';
    });

    const mapSection = document.getElementById('mapSection');
    if (mapSection) {
        mapSection.style.display = 'none';
    }
    if (map) {
        markers.forEach((marker) => map.removeLayer(marker));
        markers = [];
    }
}

function clearSelections() {
    selectedAttractions.clear();
    localStorage.removeItem(STORAGE_KEYS.SELECTED_ATTRACTIONS);
    
    document.querySelectorAll('.attraction-card').forEach(card => {
        card.classList.remove('selected-card');
        const btn = card.querySelector('.add-btn');
        if (btn) btn.textContent = '+ Add to Itinerary';
    });
    
    document.getElementById('selectedCount').textContent = '0';
    document.getElementById('optimizeSection').style.display = 'none';
    document.getElementById('itinerary').innerHTML = '';
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', loadInitialData);
} else {
    loadInitialData();
}
