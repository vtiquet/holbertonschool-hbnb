const API_BASE_URL = 'http://127.0.0.1:5000/api/v1';

// Global storage for all fetched places to enable client-side filtering
let allPlaces = []; 
// Simple cache to store fetched user details and avoid redundant API calls
let userCache = {}; 

// --- HELPER FUNCTIONS (RETAINED) ---

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

function getPlaceIdFromURL() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('id') || urlParams.get('place_id');
}

function getToken() {
    return getCookie('token');
}

function customAlert(message) {
    const alertBox = document.createElement('div');
    alertBox.style.cssText = `
        position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
        padding: 0; background: #fff; border: 2px solid #ccc; border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4); z-index: 1000;
        width: 300px; overflow: hidden; font-family: Arial, sans-serif;
    `;
    
    const header = document.createElement('div');
    header.style.cssText = `background-color: #008080; color: white; padding: 10px 20px; font-weight: bold;`;
    header.textContent = 'Notification';

    const body = document.createElement('div');
    body.style.cssText = `padding: 20px; text-align: center; color: #333;`;
    body.innerHTML = `<p>${message}</p>`;

    const footer = document.createElement('div');
    footer.style.cssText = `padding: 10px 20px; text-align: center; border-top: 1px solid #eee;`;
    
    const button = document.createElement('button');
    button.textContent = 'OK';
    button.style.cssText = `background-color: #008080; color: white; border: none; padding: 8px 15px; border-radius: 5px; cursor: pointer; transition: background-color 0.3s;`;
    
    button.onmouseover = () => button.style.backgroundColor = '#006666';
    button.onmouseout = () => button.style.backgroundColor = '#008080';
    
    button.onclick = function() {
        this.closest('div').parentNode.remove();
    };

    footer.appendChild(button);
    alertBox.appendChild(header);
    alertBox.appendChild(body);
    alertBox.appendChild(footer);
    
    document.body.appendChild(alertBox);
}

function setupPasswordToggle() {
    const togglePassword = document.getElementById('togglePassword');
    const password = document.getElementById('password');

    if (togglePassword && password) {
        togglePassword.addEventListener('click', function () {
            const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
            password.setAttribute('type', type);
            this.classList.toggle('fa-eye');
            this.classList.toggle('fa-eye-slash');
        });
    }
}

/**
 * Fetches user details by ID, utilizing a cache.
 * NOTE: This is primarily used for Reviewers now, as Host details are expected to be embedded.
 * @param {string} userId - The ID of the user to fetch.
 * @returns {Promise<object|null>} The user object or null on failure.
 */
async function fetchUser(userId) {
    if (!userId) return null;
    if (userCache[userId]) return userCache[userId];

    try {
        const response = await fetch(`${API_BASE_URL}/users/${userId}`);
        if (response.ok) {
            const user = await response.json();
            userCache[userId] = user; // Store in cache
            return user;
        }
    } catch (e) {
        console.error(`Error fetching user ${userId}:`, e);
    }
    userCache[userId] = null; // Cache failure
    return null;
}

// --- TASK 1: LOGIN (login.html) (RETAINED) ---

function setupLoginForm() {
    const loginForm = document.getElementById('login-form');
    const errorMessage = document.getElementById('error-message'); 
    const notification = document.getElementById('successNotification');
    const closeBtn = document.querySelector('#successNotification .close-btn');

    setupPasswordToggle(); 

    if (closeBtn && notification) {
        closeBtn.onclick = function() {
            notification.style.display = 'none';
        }
    }

    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault(); 
            const email = document.getElementById('email').value.trim();
            const password = document.getElementById('password').value;

            if (errorMessage) errorMessage.textContent = ''; 
            if (notification) notification.style.display = 'none'; 

            if (!email || !password) {
                if (errorMessage) errorMessage.textContent = 'Please enter both email and password.';
                return;
            }

            try {
                const response = await fetch(`${API_BASE_URL}/auth/login`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ email, password })
                });

                if (response.ok) {
                    const data = await response.json();
                    document.cookie = `token=${data.access_token}; path=/; max-age=${60 * 60 * 24}; SameSite=Lax;`; 
                    
                    const urlParams = new URLSearchParams(window.location.search);
                    const nextUrl = urlParams.get('next') || 'index.html'; 
                    
                    if (notification) {
                        notification.style.display = 'block';
                        setTimeout(() => {
                            notification.style.display = 'none'; 
                            window.location.href = nextUrl; 
                        }, 2000);
                    } else {
                           window.location.href = nextUrl;
                    }

                } else {
                    const errorData = await response.json().catch(() => ({}));
                    const message = errorData.message || ' Check your email and password.';
                    if (errorMessage) errorMessage.textContent = `Error: ${message}`;
                    customAlert(`Login Failed: ${message}`);
                }
            } catch (error) {
                console.error('Network or API connection error:', error);
                const networkError = 'A network error occurred. Ensure the server is running.';
                if (errorMessage) errorMessage.textContent = networkError;
                customAlert(`${networkError} (Hint: Check Flask/API status and CORS configuration!)`); 
            }
        });
    }
}

// --- TASK 2: INDEX (index.html) (RETAINED) ---

function checkIndexAuthentication() {
    const token = getToken();
    const loginLink = document.getElementById('login-link');
    const nav = document.querySelector('header nav');

    if (loginLink) loginLink.remove(); 
    
    if (token) {
        const logoutLink = document.createElement('a');
        logoutLink.href = '#';
        logoutLink.className = 'login-button';
        logoutLink.textContent = 'Logout';
        logoutLink.addEventListener('click', (e) => {
            e.preventDefault();
            document.cookie = 'token=; path=/; max-age=0; Secure; SameSite=Lax';
            customAlert('You have been logged out.');
            
            window.location.href = window.location.href; 
        });
        nav.appendChild(logoutLink);
        
    } else {
        const loginLinkElement = document.createElement('a');
        loginLinkElement.href = 'login.html';
        loginLinkElement.className = 'login-button';
        loginLinkElement.id = 'login-link';
        loginLinkElement.textContent = 'Login';
        nav.appendChild(loginLinkElement);
    }
    
    const path = window.location.pathname;
    if (path.includes('index.html') || path.endsWith('/web_client/') || path.endsWith('/part4/')) {
        loadPlaces();
    }
}

function renderPlaces(places) {
    const placesContainer = document.getElementById('places-list');
    if (!placesContainer) return;
    
    placesContainer.innerHTML = ''; 

    if (places.length === 0) {
        placesContainer.innerHTML = '<p>No places found matching your criteria.</p>';
        return;
    }

    places.forEach(place => {
        const placeCard = document.createElement('article');
        placeCard.className = 'place-card';
        
        const placeName = place.title || 'Unnamed Place';
        const priceDisplay = (place.price != null && place.price !== '') ? place.price : 'N/A'; 
        const placeLocation = `GPS: ${place.latitude?.toFixed(4) || '?'}°, ${place.longitude?.toFixed(4) || '?'}°`;

        placeCard.innerHTML = `
            <h2>${placeName}</h2> 
            
            <div class="price_by_night">
                $${priceDisplay}
            </div>

            <div class="information">
                <div class="location-info">
                    <i class="fas fa-map-marker-alt"></i>
                    ${placeLocation}
                </div>
            </div>

            <div class="description">
                ${place.description || 'No description provided.'}
            </div>
            
            <a href="place.html?id=${place.id}" class="details-button">Details</a>
        `;
        
        placesContainer.appendChild(placeCard);
    });
}

function filterAndRenderPlaces(places, maxPrice) {
    if (maxPrice == null || isNaN(maxPrice)) {
        renderPlaces(places);
        return;
    }
    
    const filteredPlaces = places.filter(place => {
        const price = parseFloat(place.price);
        return !isNaN(price) && price <= maxPrice;
    });

    renderPlaces(filteredPlaces);
}

function setupPriceFilter() {
    const priceFilter = document.getElementById('price-filter');
    const priceDisplay = document.getElementById('current-max-price');

    if (priceFilter) {
        priceFilter.addEventListener('input', function() {
            const maxPrice = parseInt(this.value, 10);
            if (priceDisplay) priceDisplay.textContent = maxPrice;
            
            filterAndRenderPlaces(allPlaces, maxPrice);
        });
        
        const initialMaxPrice = parseInt(priceFilter.value, 10);
        if (priceDisplay) priceDisplay.textContent = initialMaxPrice;
        
        filterAndRenderPlaces(allPlaces, initialMaxPrice);

    } else {
        renderPlaces(allPlaces);
    }
}


async function loadPlaces() {
    const placesContainer = document.getElementById('places-list');
    if (!placesContainer) return;
    placesContainer.innerHTML = 'Loading places...';

    try {
        const response = await fetch(`${API_BASE_URL}/places`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        allPlaces = await response.json();
        
        setupPriceFilter();

    } catch (error) {
        console.error("Error fetching places:", error);
        placesContainer.innerHTML = '<p style="color: red;">Error loading places. Please check the API status and console for details.</p>';
    }
}


// --- TASK 3: PLACE DETAILS (place.html) ---

/**
 * Renders the main place information and amenities onto the #place-details section.
 * @param {object} place - The place object fetched from the API.
 * @param {object|null} owner - The embedded host user object (place.owner). (UPDATED)
 * @param {Array<object>} amenities - List of embedded amenity objects (place.amenities). (UPDATED)
 */
function renderPlaceDetails(place, owner, amenities = []) {
    const container = document.getElementById('place-details'); 
    if (!container) return;

    // FIX: Host Name Logic - assumes owner is embedded in the place object (as per partner's code)
    let hostName;
    if (owner && owner.first_name && owner.last_name) {
        hostName = `${owner.first_name} ${owner.last_name}`;
    } else if (place.host_id) {
        // Fallback to displaying host_id if name is missing but ID is present (from main place object)
        hostName = `User ID: ${place.host_id} (Host name missing)`;
    } else {
        hostName = 'N/A (Check API/DB linkage for host)';
    }

    const placeName = place.title || 'Details Not Found';
    const priceDisplay = (place.price != null && place.price !== '') ? place.price : 'N/A'; 
    const placeLocation = `GPS: ${place.latitude?.toFixed(4) || '?'}°, ${place.longitude?.toFixed(4) || '?'}°`;
    
    // FIX: Build the dynamic amenities list HTML from the embedded amenities array
    let amenitiesHtml = '';
    if (amenities.length > 0) {
        amenities.forEach(amenity => {
            // Using a generic checkmark icon for now
            amenitiesHtml += `<li><i class="fas fa-check-circle"></i> ${amenity.name}</li>`;
        });
    } else {
        amenitiesHtml = '<li>No amenities listed for this place (Check API response structure).</li>';
    }
    
    container.innerHTML = `
        <article class="place-article">
            <h2>${placeName}</h2>

            <div class="place-info-header">
                <p><strong>Price:</strong> $<span class="place-price">${priceDisplay}</span> / night</p>
                <p><strong>Location:</strong> ${placeLocation}</p>
            </div>
            
            <div class="place-detail-section host-info">
                <h4>Hosted by:</h4>
                <p>${hostName}</p>
            </div>
            
            <div class="place-detail-section description-info">
                <h4>Description:</h4>
                <p>${place.description || 'No description provided.'}</p>
            </div>
            
            <div class="place-detail-section amenities-section">
                <h4>Amenities</h4>
                <ul class="amenities-list">
                    ${amenitiesHtml}
                </ul>
            </div>
        </article>
    `;
}

/**
 * Renders the list of reviews into the #reviews section, including dynamic names.
 */
function renderReviews(reviews, placeId) {
    const reviewsContainer = document.getElementById('reviews');
    const token = getToken();

    if (!reviewsContainer) return;
    
    reviewsContainer.innerHTML = '<h3>Guest Reviews</h3>'; 

    if (reviews.length === 0) {
        reviewsContainer.innerHTML += '<p>No reviews yet. Be the first!</p>';
    } else {
        const reviewsList = document.createElement('div');
        reviewsList.className = 'reviews-list';
        
        reviews.forEach(review => {
            const reviewItem = document.createElement('article');
            reviewItem.className = 'review-item';
            
            const hasUserName = review.userName && review.userName !== 'null null' && review.userName.trim() !== '';
            
            // FIX: Robust check for user ID to prevent "User ID: undefined" string
            let userNameDisplay;
            if (hasUserName) {
                 userNameDisplay = `Reviewed by: ${review.userName}`;
            } else if (review.user_id) { 
                 userNameDisplay = `Reviewed by: User ID: ${review.user_id}`;
            } else { 
                 userNameDisplay = `Reviewed by: Anonymous User (ID missing)`;
            }

            reviewItem.innerHTML = `
                <div class="review-header">
                    <span class="review-rating">Rating: ${review.rating} / 5</span>
                    <span class="review-user">${userNameDisplay}</span>
                </div>
                <p class="review-text">${review.text}</p>
            `;
            reviewsList.appendChild(reviewItem);
        });
        
        reviewsContainer.appendChild(reviewsList);
    }
    
    const ctaContainer = document.createElement('div');
    ctaContainer.className = 'add-review-cta';
    ctaContainer.style.textAlign = 'center';
    ctaContainer.style.marginTop = '20px';

    const buttonStyle = "background-color: #008080; padding: 10px 20px; text-decoration: none; color: white; border-radius: 5px; display: inline-block; transition: background-color 0.3s;";

    if (token) {
        ctaContainer.innerHTML = `<a href="add_review.html?place_id=${placeId}" class="details-button" style="${buttonStyle}">Add a Review</a>`;
    } else {
        const currentPageUrl = encodeURIComponent(window.location.href);
        ctaContainer.innerHTML = `<a href="login.html?next=${currentPageUrl}" class="details-button" style="${buttonStyle}">Login to Add a Review</a>`;
    }
    reviewsContainer.appendChild(ctaContainer);
}


async function setupPlaceDetails() {
    const placeId = getPlaceIdFromURL();
    const container = document.getElementById('place-details');
    
    const addReviewSection = document.getElementById('add-review');
    if(addReviewSection) addReviewSection.style.display = 'none'; 

    if (!placeId || !container) {
        if(container) container.innerHTML = '<h2>Error: Place ID not found in URL.</h2>';
        return;
    }

    await checkIndexAuthentication(); 
    container.innerHTML = 'Loading place details...';
    
    try {
        // 1. Fetch Place Details (EAGER LOADING EXPECTED: place.owner, place.amenities, place.reviews)
        const placeResponse = await fetch(`${API_BASE_URL}/places/${placeId}`);
        if (!placeResponse.ok) {
            throw new Error('Place not found or API error.');
        }
        const place = await placeResponse.json();

        // Use embedded amenities and owner/host details
        const placeAmenities = place.amenities || [];
        const owner = place.owner || null;
        
        // Use embedded reviews
        const reviews = place.reviews || [];

        // 2. Resolve User Names for all Reviews concurrently
        // NOTE: This is still required as the reviewer's name is NOT embedded in the review object.
        const reviewUserPromises = reviews.map(review => fetchUser(review.user_id));
        const reviewUsers = await Promise.all(reviewUserPromises);
        
        // Map user names back into the review objects
        const enhancedReviews = reviews.map((review, index) => {
            const user = reviewUsers[index];
            let userName = null;
            if (user && user.first_name && user.last_name) {
                userName = `${user.first_name} ${user.last_name}`;
            }
            return {
                ...review,
                userName: userName
            };
        });
        
        // 3. Render Details
        renderPlaceDetails(place, owner, placeAmenities); 
        renderReviews(enhancedReviews, placeId); 

    } catch (error) {
        console.error("Error fetching place details:", error);
        container.innerHTML = `<h2>Error loading place details.</h2><p>${error.message}</p>`;
    }
}


// --- TASK 4: ADD REVIEW FORM (add_review.html) (RETAINED) ---

function setupReviewForm() {
    const token = getToken();
    const placeId = getPlaceIdFromURL();
    const reviewForm = document.getElementById('review-form');

    if (!token) {
        customAlert('You must be logged in to add a review. Redirecting to home.');
        window.location.href = 'index.html'; 
        return;
    }
    if (!placeId) {
        customAlert('Error: Place ID not found. Redirecting to home.');
        window.location.href = 'index.html';
        return;
    }
    
    const placeIdDisplay = document.getElementById('place-id-display');
    if (placeIdDisplay) placeIdDisplay.textContent = `Add a Review for Place ID: ${placeId}`;

    if (reviewForm) {
        reviewForm.addEventListener('submit', async (event) => {
            event.preventDefault();
            
            const reviewText = document.getElementById('review-text').value;
            const rating = document.getElementById('rating').value; 
            
            await submitReview(token, placeId, reviewText, rating);
        });
    }
}

async function submitReview(token, placeId, reviewText, rating) {
    const feedbackMessage = document.getElementById('feedback-message');
    if (feedbackMessage) feedbackMessage.textContent = 'Submitting...';

    const reviewData = {
        text: reviewText,
        rating: parseInt(rating, 10) || 5 
    };

    const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };

    try {
        const response = await fetch(`${API_BASE_URL}/places/${placeId}/reviews`, {
            method: 'POST',
            headers: headers,
            body: JSON.stringify(reviewData)
        });

        if (response.ok) {
            customAlert('Review submitted successfully!');
            document.getElementById('review-form').reset(); 
            if (feedbackMessage) feedbackMessage.textContent = 'Success! Review submitted.';
            setTimeout(() => {
                window.location.href = `place.html?id=${placeId}`;
            }, 1500);
        } else {
            const errorData = await response.json().catch(() => ({ message: 'Failed to submit review: Unknown error.' }));
            const message = errorData.message || response.statusText || 'Failed to submit review.';
            customAlert(`Failed to submit review: ${message}`);
            if (feedbackMessage) feedbackMessage.textContent = `Error: ${message}`;
        }
    } catch (error) {
        console.error('Review submission error:', error);
        customAlert('A network error occurred while submitting the review.');
        if (feedbackMessage) feedbackMessage.textContent = 'Error: A network error occurred.';
    }
}

// --- MAIN INITIALIZATION (RETAINED) ---

document.addEventListener('DOMContentLoaded', () => {
    const path = window.location.pathname;

    if (path.includes('login.html')) {
        setupLoginForm(); 
    } else if (path.includes('place.html')) {
        setupPlaceDetails();
    } else if (path.includes('add_review.html')) {
        setupReviewForm();
    } else if (path.includes('index.html') || path.endsWith('/web_client/') || path.endsWith('/part4/')) {
        checkIndexAuthentication();
    }
});