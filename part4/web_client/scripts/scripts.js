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

/**
 * Initializes the login form and password visibility toggle.
 */
function setupLoginForm() {
    const form = document.getElementById('login-form');
    if (!form) return;

    // --- Password Visibility Toggle Feature (User Request) ---
    const passwordInput = document.getElementById('password');
    const togglePassword = document.getElementById('togglePassword');

    if (togglePassword) {
        togglePassword.addEventListener('click', function (e) {
            // Toggle the type attribute between 'password' and 'text'
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            
            // Toggle the eye icon
            this.classList.toggle('fa-eye-slash');
            this.classList.toggle('fa-eye');
        });
    }

    // --- Login Form Submission ---
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const errorElement = document.getElementById('error-message');
        errorElement.textContent = '';

        const loginData = { email, password };

        try {
            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(loginData),
            });

            if (response.ok) {
                const data = await response.json();
                
                // CRITICAL FIX: Check for the 'token' key
                if (data.token) {
                    // Set cookie for 1 hour
                    document.cookie = `token=${data.token}; path=/; max-age=3600; Secure; SameSite=Lax`;
                    customAlert('Login successful! Redirecting...');
                    window.location.href = 'index.html';
                } else {
                    // This handles the user's specific error message
                    customAlert('Login successful, but no token received from the API.');
                }
            } else {
                const errorData = await response.json().catch(() => ({ message: 'Login failed: Unknown error.' }));
                const message = errorData.message || response.statusText || 'Login failed.';
                errorElement.textContent = message;
                customAlert(`Login failed: ${message}`);
            }
        } catch (error) {
            console.error('Login error:', error);
            errorElement.textContent = 'A network error occurred. Please check the API status.';
            customAlert('A network error occurred during login.');
        }
    });
}

// --- TASK 2: INDEX (index.html) ---

/**
 * Checks authentication status and updates the navigation bar.
 */
function checkIndexAuthentication() {
    const token = getToken();
    const loginLink = document.getElementById('login-link');
    const nav = document.querySelector('header nav');

    // Remove existing login/logout link to avoid duplicates
    if (loginLink) loginLink.remove(); 
    
    if (token) {
        // User is logged in: Add Logout Link
        const logoutLink = document.createElement('a');
        logoutLink.href = '#';
        logoutLink.className = 'login-button';
        logoutLink.textContent = 'Logout';
        logoutLink.addEventListener('click', (e) => {
            e.preventDefault();
            // Clear the cookie and redirect
            document.cookie = 'token=; path=/; max-age=0; Secure; SameSite=Lax';
            customAlert('You have been logged out.');
            window.location.href = 'index.html';
        });
        nav.appendChild(logoutLink);
        
    } else {
        // User is logged out: Add Login Link
        const loginLinkElement = document.createElement('a');
        loginLinkElement.href = 'login.html';
        loginLinkElement.className = 'login-button';
        loginLinkElement.id = 'login-link';
        loginLinkElement.textContent = 'Login';
        nav.appendChild(loginLinkElement);
    }
    
    // Then load the places
    loadPlaces();
}


/**
 * Fetches and displays all places.
 */
async function loadPlaces() {
    const placesContainer = document.getElementById('places-list');
    if (!placesContainer) return;
    placesContainer.innerHTML = 'Loading places...';

    try {
        const response = await fetch(`${API_BASE_URL}/places`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const places = await response.json();
        
        placesContainer.innerHTML = '';
        if (places.length === 0) {
            placesContainer.innerHTML = '<p>No places found in the database.</p>';
            return;
        }

        places.forEach(place => {
            // Revert to direct access. If the API is running and populated correctly, these should work.
            // If they are still 0 or 'N/A' after this, the problem is in your API's /places endpoint response structure.
            const price = place.price_by_night;
            const guests = place.max_guest;
            const rooms = place.number_rooms;
            const bathrooms = place.number_bathrooms;
            
            const placeCard = document.createElement('article');
            placeCard.className = 'place-card';
            placeCard.innerHTML = `
                <h3>${place.title}</h3>
                <p><strong>$${price || 'N/A'}</strong> per night</p>
                <p>${place.description || 'No description provided.'}</p>
                <div class="place-meta">
                    <span>Max Guests: ${guests || 'N/A'}</span>
                    <span>Bedrooms: ${rooms || 'N/A'}</span>
                    <span>Bathrooms: ${bathrooms || 'N/A'}</span>
                </div>
                <a href="place.html?id=${place.id}" class="details-button">View Details</a>
            `;
            placesContainer.appendChild(placeCard);
        });

    } catch (error) {
        console.error("Error fetching places:", error);
        placesContainer.innerHTML = `<p style="color: red;">Failed to load places. API Error: ${error.message}</p>`;
    }
}

// --- TASK 3: PLACE DETAILS (place.html) ---

/**
 * Loads and displays detailed information for a specific place.
 */
async function setupPlaceDetails() {
    const placeId = getPlaceIdFromURL();
    if (!placeId) {
        document.getElementById('place-details-container').innerHTML = '<h2>Error: Place ID not found in URL.</h2>';
        return;
    }

    await checkIndexAuthentication(); // Update nav bar (Logout/Login)

    try {
        // 1. Fetch Place Details
        const placeResponse = await fetch(`${API_BASE_URL}/places/${placeId}`);
        if (!placeResponse.ok) {
            throw new Error('Place not found or API error.');
        }
        const place = await placeResponse.json();

        // 2. Fetch Host Details (Requires /users/{id} endpoint to work)
        let hostUser = null;
        try {
            const hostResponse = await fetch(`${API_BASE_URL}/users/${place.host_id}`);
            if (hostResponse.ok) {
                hostUser = await hostResponse.json();
            }
        } catch(e) {
            console.warn("Could not fetch host details.");
        }
        
        // 3. Fetch Reviews
        const reviewsResponse = await fetch(`${API_BASE_URL}/places/${placeId}/reviews`);
        const reviews = reviewsResponse.ok ? await reviewsResponse.json() : [];

        // 4. Render Details
        renderPlaceDetails(place, hostUser); // Pass both place and host data
        renderReviews(reviews);

        // 5. Update 'Add Review' link
        const addReviewLink = document.getElementById('add-review-link');
        if (addReviewLink) {
            if (getToken()) {
                addReviewLink.href = `add_review.html?place_id=${placeId}`;
                addReviewLink.style.display = 'inline-block';
            } else {
                addReviewLink.textContent = 'Login to add a review';
                addReviewLink.href = 'login.html';
            }
        }

    } catch (error) {
        console.error("Error fetching place details:", error);
        document.getElementById('place-details-container').innerHTML = `<h2>Error: ${error.message}</h2><p>Could not load place details.</p>`;
    }
}

/**
 * Renders the main place information onto place.html.
 * @param {object} place - The place object fetched from the API.
 * @param {object} reviews - The array of review objects.
 * @param {object} amenities - The array of amenity objects (optional/if needed).
 */
function renderPlaceDetails(place, user) {
    const container = document.getElementById('place-details-container');
    if (!container) return;

    // FIX: Use actual place data, not hardcoded text.
    // NOTE: This assumes your API /users/{id} endpoint returns a user object.
    const hostName = user ? `${user.first_name} ${user.last_name}` : `User ID ${place.host_id}`;
    
    // NOTE: Amenities are not fetched in this simplified script. You would need to fetch them
    // via /places/{id}/amenities and render them here.
    
    container.innerHTML = `
        <h2>${place.title}</h2>
        <div class="place-info">
            <p><strong>Host:</strong> ${hostName}</p>
            <p><strong>Price:</strong> $${place.price_by_night || 'N/A'} / night</p>
            <p><strong>Description:</strong> ${place.description || 'No description provided.'}</p>
        </div>
        
        <div class="place-meta">
            <span>Max Guests: ${place.max_guest || 'N/A'}</span>
            <span>Bedrooms: ${place.number_rooms || 'N/A'}</span>
            <span>Bathrooms: ${place.number_bathrooms || 'N/A'}</span>
        </div>
        
        <section class="amenities-section">
            <h3>Amenities</h3>
            <ul id="amenities-list">
                <li>Wi-Fi</li>
                <li>Kitchen</li>
                <li>Free parking</li>
                </ul>
        </section>
    `;
}


/**
 * Renders the list of reviews.
 */
function renderReviews(reviews) {
    const reviewsContainer = document.getElementById('reviews-list');
    if (!reviewsContainer) return;
    
    reviewsContainer.innerHTML = reviews.length === 0 
        ? '<p>No reviews yet.</p>' 
        : '';

    reviews.forEach(review => {
        const reviewCard = document.createElement('article');
        reviewCard.className = 'review-card';
        // NOTE: You would typically fetch the user's name from /users/{user_id}
        // For simplicity, we use the ID here, but fetching the username is better UX.
        reviewCard.innerHTML = `
            <h4>Rating: ${review.rating} / 5</h4>
            <p>User ID: ${review.user_id}</p>
            <p>${review.text}</p>
        `;
        reviewsContainer.appendChild(reviewCard);
    });
}


/**
 * Initializes the review submission form on add_review.html.
 */
function setupReviewForm() {
    const form = document.getElementById('review-form');
    const placeId = getPlaceIdFromURL();
    const token = getToken();
    const feedbackMessage = document.getElementById('feedback-message');
    
    if (!token) {
        customAlert("You must be logged in to add a review.");
        window.location.href = `login.html`; // Redirect if not logged in
        return;
    }
    if (!form || !placeId) {
        customAlert("Error: Cannot find form or place ID is missing.");
        return;
    }
    
    // Show which place the review is for (optional, needs another API call)
    // document.getElementById('place-title').textContent = `Review for Place ${placeId}`;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        feedbackMessage.textContent = 'Submitting...';

        const rating = document.getElementById('rating').value;
        const reviewText = document.getElementById('review-text').value.trim();

        if (!rating || !reviewText) {
            feedbackMessage.textContent = 'Please provide a rating and review text.';
            return;
        }
        
        // IMPORTANT: The API needs the user_id. You need to decode the JWT payload 
        // to get the user ID (which is the token identity 'sub' or 'identity').
        let userId = null;
        try {
            const tokenParts = token.split('.');
            const payload = JSON.parse(atob(tokenParts[1]));
            userId = payload.sub || payload.identity;
        } catch (e) {
            console.warn("Could not decode user ID from token payload.");
        }

        if (!userId) {
            feedbackMessage.textContent = 'Error: Could not retrieve user ID from token.';
            return;
        }

        const reviewData = {
            rating: parseInt(rating),
            text: reviewText,
            user_id: userId,
            place_id: placeId
        };

        try {
            const response = await fetch(`${API_BASE_URL}/places/${placeId}/reviews`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}` // Mandatory for protected routes
                },
                body: JSON.stringify(reviewData),
            });

            if (response.ok) {
                feedbackMessage.textContent = 'Success! Review submitted. Redirecting...';
                // Redirect back to the place details page after submission
                setTimeout(() => {
                    window.location.href = `place.html?id=${placeId}`;
                }, 1500);
            } else {
                const errorData = await response.json().catch(() => ({ message: 'Failed to submit review: Unknown error.' }));
                const message = errorData.message || response.statusText || 'Failed to submit review.';
                customAlert(`Failed to submit review: ${message}`);
                feedbackMessage.textContent = `Error: ${message}`;
            }
        } catch (error) {
            console.error('Review submission error:', error);
            feedbackMessage.textContent = 'Error: A network error occurred.';
        }
    });
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