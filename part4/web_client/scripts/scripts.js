const API_BASE_URL = 'http://127.0.0.1:5000/api/v1';

// --- HELPER FUNCTIONS ---

/**
 * Retrieves the value of a cookie by its name.
 * @param {string} name - The name of the cookie to retrieve.
 * @returns {string|null} The cookie value or null if not found.
 */
function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
    return null;
}

/**
 * Extracts the 'id' parameter from the current URL query string.
 * @returns {string|null} The place ID or null if not found.
 */
function getPlaceIdFromURL() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('id') || urlParams.get('place_id');
}

/**
 * Fetches the JWT token from cookies.
 * @returns {string|null} The JWT token.
 */
function getToken() {
    return getCookie('token');
}

/**
 * Custom alert function to avoid window.alert()
 * @param {string} message - The message to display.
 */
function customAlert(message) {
    const alertBox = document.createElement('div');
    alertBox.style.cssText = `
        position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
        padding: 0; background: #fff; border: 2px solid #ccc; border-radius: 10px;
        box-shadow: 0 8px 16px rgba(0,0,0,0.3); z-index: 1000;
        width: 300px; overflow: hidden; font-family: Arial, sans-serif;
    `;
    
    // Header for the alert (using theme color)
    const header = document.createElement('div');
    header.style.cssText = `
        background-color: #008080; /* Teal/Turquoise theme color */
        color: white;
        padding: 10px 20px;
        font-weight: bold;
    `;
    header.textContent = 'Notification';

    // Body for the message
    const body = document.createElement('div');
    body.style.cssText = `
        padding: 20px;
        text-align: center;
        color: #333;
    `;
    body.innerHTML = `<p>${message}</p>`;

    // Footer for the button
    const footer = document.createElement('div');
    footer.style.cssText = `
        padding: 10px 20px;
        text-align: center;
        border-top: 1px solid #eee;
    `;
    
    const button = document.createElement('button');
    button.textContent = 'OK';
    button.style.cssText = `
        background-color: #008080;
        color: white;
        border: none;
        padding: 8px 15px;
        border-radius: 5px;
        cursor: pointer;
        transition: background-color 0.3s;
    `;
    
    // Add hover effects for better UX
    button.onmouseover = () => button.style.backgroundColor = '#006666';
    button.onmouseout = () => button.style.backgroundColor = '#008080';
    
    button.onclick = function() {
        // Remove the alert box when OK is clicked
        this.closest('div').parentNode.remove();
    };

    footer.appendChild(button);
    alertBox.appendChild(header);
    alertBox.appendChild(body);
    alertBox.appendChild(footer);
    
    document.body.appendChild(alertBox);
}

// --- PASSWORD TOGGLE FUNCTION (Task 1) ---

function setupPasswordToggle() {
    const togglePassword = document.getElementById('togglePassword');
    const password = document.getElementById('password');

    if (togglePassword && password) {
        togglePassword.addEventListener('click', function () {
            // Toggle the type attribute
            const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
            password.setAttribute('type', type);
            
            // Toggle the eye icon class
            this.classList.toggle('fa-eye');
            this.classList.toggle('fa-eye-slash');
        });
    }
}


// --- TASK 1: LOGIN (login.html) ---

function setupLoginForm() {
    const loginForm = document.getElementById('login-form');
    if (!loginForm) return;

    // Initialize the password toggle function
    setupPasswordToggle(); 

    loginForm.addEventListener('submit', async (event) => {
        event.preventDefault();
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const errorMessage = document.getElementById('error-message');
        
        if (errorMessage) errorMessage.textContent = ''; 

        try {
            const LOGIN_ENDPOINT = `${API_BASE_URL}/auth/login`; 

            const response = await fetch(LOGIN_ENDPOINT, { 
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, password })
            });

            if (response.ok) {
                // --- CRITICAL SUCCESS LOGIC ---
                const data = await response.json();
                const token = data.token; // Assume the API sends { "token": "..." }

                if (token) {
                    // 1. Store the token as a cookie (Requirement)
                    // Set cookie to expire in 7 days (standard practice)
                    document.cookie = `token=${token}; path=/; max-age=${60 * 60 * 24 * 7}; secure; samesite=Lax`;
                    
                    // 2. Redirect to the home page (Requirement)
                    window.location.href = 'index.html';
                } else {
                    // Handle case where API succeeds but sends no token
                    customAlert('Login successful, but no token received from the API.');
                }
                // --- END CRITICAL SUCCESS LOGIC ---

            } else {
                // Handle failed login (401 Unauthorized, 400 Bad Request, etc.)
                const errorData = await response.json().catch(() => ({ message: 'Login failed: Unknown error.' }));
                const message = errorData.message || response.statusText || 'Invalid email or password.';
                
                if (errorMessage) errorMessage.textContent = message;
                customAlert('Login failed: ' + message);
            }
        } catch (error) {
            // This is the network error/CORS error catch
            console.error('Login error:', error);
            if (errorMessage) errorMessage.textContent = 'A network error occurred. Check console for details.';
            customAlert('A network error occurred. Please ensure your API is running and CORS is configured correctly.');
        }
    });
}

// --- TASK 2: INDEX (index.html) ---

let allPlaces = []; // Global store for client-side filtering

/**
 * 1. Check User Authentication & Setup Logout Link
 */
function checkIndexAuthentication() {
    const token = getToken();
    const loginLink = document.getElementById('login-link');
    
    if (loginLink) {
        if (token) {
            // Authenticated: Change to Logout
            loginLink.textContent = 'Logout';
            loginLink.href = '#'; 
            loginLink.removeEventListener('click', handleLogout); 
            loginLink.addEventListener('click', handleLogout);
        } else {
            // Not Authenticated: Show Login
            loginLink.textContent = 'Login';
            loginLink.href = 'login.html';
            loginLink.removeEventListener('click', handleLogout); 
        }
    }
    
    // Always fetch places, passing the token if available
    fetchPlaces(token);
    setupPriceFilter();
}

function handleLogout(event) {
    event.preventDefault();
    document.cookie = 'token=; path=/; max-age=0;'; // Expire the cookie
    window.location.href = 'index.html'; // Reload to reflect status change
}

/**
 * 2. Fetch Places Data
 * @param {string|null} token - The JWT token for authentication.
 */
async function fetchPlaces(token) {
    const placesList = document.getElementById('places-list');
    if (!placesList) return;
    placesList.innerHTML = '<h2>Loading Places...</h2>';
    
    // Prepare headers, including Authorization if token is present
    const headers = { 'Content-Type': 'application/json' };
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/places`, { headers });

        if (response.ok) {
            allPlaces = await response.json();
            displayPlaces(allPlaces); // Populate the list
        } else {
            placesList.innerHTML = `<h2>Failed to fetch places. Status: ${response.status}. Please check API logs.</h2>`;
            console.error('Failed to fetch places:', response.statusText);
        }
    } catch (error) {
        placesList.innerHTML = `<h2>A network error occurred. Please ensure the API is running and CORS is configured.</h2>`;
        console.error('Network error during fetch places:', error);
    }
}

/**
 * 3. Populate Places List
 * @param {Array<Object>} places - Array of place objects from the API.
 */
function displayPlaces(places) {
    const placesList = document.getElementById('places-list');
    if (!placesList) return;
    placesList.innerHTML = ''; // Clear existing content

    if (places.length === 0) {
        placesList.innerHTML = '<p>No places found.</p>';
        return;
    }

    places.forEach(place => {
        const placeCard = document.createElement('div');
        placeCard.className = 'place-card';
        placeCard.dataset.price = place.price_per_night; // Store price for filtering
        
        placeCard.innerHTML = `
            <h3>${place.name}</h3>
            <p><strong>Price:</strong> $<span class="price">${place.price_per_night}</span> / night</p>
            <p>Location: ${place.city_id || 'Unknown City'}</p>
            <a href="place.html?id=${place.id}" class="details-button">View Details</a>
        `;
        placesList.appendChild(placeCard);
    });
}

/**
 * 4. Implement Client-Side Filtering
 */
function setupPriceFilter() {
    const priceFilter = document.getElementById('price-filter');
    if (!priceFilter) return;

    priceFilter.addEventListener('change', (event) => {
        const maxPrice = event.target.value;
        const placeCards = document.querySelectorAll('.place-card');

        placeCards.forEach(card => {
            const placePrice = parseInt(card.dataset.price, 10);
            
            // Check if 'All' is selected or if the place price is less than or equal to the selected max price
            if (maxPrice === 'all' || placePrice <= parseInt(maxPrice, 10)) {
                card.style.display = 'block';
            } else {
                card.style.display = 'none';
            }
        });
    });
}

// --- TASK 3: PLACE DETAILS (place.html) ---

function setupPlaceDetails() {
    const placeId = getPlaceIdFromURL();
    const token = getToken();
    
    if (!placeId) {
        document.getElementById('place-details').innerHTML = '<h2>Error: Place ID not found in URL.</h2>';
        return;
    }

    const addReviewSection = document.getElementById('add-review');
    const addReviewButton = document.getElementById('add-review-button');

    if (token) {
        // Authenticated: Show button and link it to the review form
        if (addReviewSection) addReviewSection.style.display = 'block';
        if (addReviewButton) {
            addReviewButton.href = `add_review.html?place_id=${placeId}`;
        }
    } else {
        // Not authenticated: Hide add review section
        if (addReviewSection) addReviewSection.style.display = 'none';
    }

    fetchPlaceDetails(token, placeId);
}

async function fetchPlaceDetails(token, placeId) {
    const detailsSection = document.getElementById('place-details');
    if (!detailsSection) return;
    detailsSection.innerHTML = '<h2>Loading Place Details...</h2>';
    
    const headers = { 'Content-Type': 'application/json' };
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    try {
        // Fetch Place Details
        const placeResponse = await fetch(`${API_BASE_URL}/places/${placeId}`, { headers });
        if (!placeResponse.ok) throw new Error('Failed to fetch place details.');
        const place = await placeResponse.json();

        // Fetch Reviews
        const reviewsResponse = await fetch(`${API_BASE_URL}/places/${placeId}/reviews`, { headers });
        const reviews = reviewsResponse.ok ? await reviewsResponse.json() : [];

        displayPlaceDetails(place, reviews);

    } catch (error) {
        detailsSection.innerHTML = `<h2>Error fetching data: ${error.message}</h2>`;
        console.error('Details fetch error:', error);
    }
}

function displayPlaceDetails(place, reviews) {
    const detailsSection = document.getElementById('place-details');
    if (!detailsSection) return;
    detailsSection.innerHTML = ''; // Clear loading message

    const amenitiesList = (place.amenities || []).map(a => `<li>${a.name || a.id}</li>`).join('');

    const reviewsHtml = reviews.length > 0 ? reviews.map(review => `
        <div class="review-card">
            <p><strong>User ID:</strong> ${review.user_id || 'N/A'}</p>
            <p><strong>Rating:</strong> ${review.rating}/5</p>
            <p>${review.text}</p>
        </div>
    `).join('') : '<p>No reviews yet for this place. Be the first to add one!</p>';

    const placeDetailsHTML = `
        <article class="place-details">
            <h1>${place.name}</h1>
            <p class="place-info"><strong>Location:</strong> ${place.city_id || 'Unknown City'}</p>
            <p class="place-info"><strong>Host:</strong> ${place.host_id || 'Unknown Host'}</p>
            <p class="place-info"><strong>Price per Night:</strong> $${place.price_per_night}</p>
            <p class="place-info"><strong>Max Guests:</strong> ${place.max_guest}</p>
            <p class="place-info"><strong>Description:</strong> ${place.description}</p>
            
            <h3>Amenities</h3>
            <ul>${amenitiesList}</ul>

            <hr>
            
            <h2>Reviews</h2>
            <section id="reviews-list">${reviewsHtml}</section>
        </article>
    `;
    detailsSection.innerHTML = placeDetailsHTML;
}

// --- TASK 4: ADD REVIEW FORM (add_review.html) ---

function setupReviewForm() {
    const token = getToken();
    const placeId = getPlaceIdFromURL();
    const reviewForm = document.getElementById('review-form');

    // 1. Check Authentication and Place ID
    if (!token) {
        customAlert('You must be logged in to add a review. Redirecting to home.');
        window.location.href = 'index.html'; // Redirect if unauthenticated
        return;
    }
    if (!placeId) {
        customAlert('Error: Place ID not found. Redirecting to home.');
        window.location.href = 'index.html';
        return;
    }
    
    // Update the header to show which place is being reviewed
    const placeIdDisplay = document.getElementById('place-id-display');
    if (placeIdDisplay) placeIdDisplay.textContent = `Add a Review for Place ID: ${placeId}`;

    // 2. Setup Event Listener
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
            document.getElementById('review-form').reset(); // Clear form
            if (feedbackMessage) feedbackMessage.textContent = 'Success! Review submitted.';
            // Redirect back to the place details page after submission
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

// --- MAIN INITIALIZATION ---

document.addEventListener('DOMContentLoaded', () => {
    // Determine which page we are on and call the relevant setup function
    const path = window.location.pathname;

    if (path.includes('login.html')) {
        setupLoginForm();
    } else if (path.includes('place.html')) {
        setupPlaceDetails();
    } else if (path.includes('add_review.html')) {
        setupReviewForm();
    } else if (path.includes('index.html') || path.endsWith('/web_client/') || path.endsWith('/part4/')) {
        // Handle index.html or root access
        checkIndexAuthentication();
    }
});