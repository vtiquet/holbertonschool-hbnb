
<div align="center"><img src="https://github.com/ksyv/holbertonschool-web_front_end/blob/main/baniere_holberton.png"></div>

# ✨ HBnB Web Client: Your Next Stay Starts Here\! 🏡

## 🗺️ Overview

This repository contains the dynamic **HBnB (Holberton's BnB) Web Client**, which is the user-facing front-end for our full-stack accommodation management application.

Built using **HTML, CSS, and vanilla JavaScript**, this client interacts seamlessly with our Python/Flask RESTful API to manage places, users, and reviews, providing a smooth, single-page-application-like experience without full page reloads. It's where the magic happens\! ✨

-----

## 🛠️ Technology Stack

The HBnB ecosystem is divided into two parts for clear responsibilities.

### 💻 Client-Side (Frontend)

| Technology | Role |
| :--- | :--- |
| **HTML5** | Semantic structure—the skeleton of our pages. |
| **CSS3** | Modern styling for a great user experience. |
| **JavaScript ES6+** | Client-side logic, making asynchronous calls (`fetch`) to the API, and dynamic DOM updates. |

### 🧠 Server-Side (Backend)

*(The powerful foundation this client relies on\!)*
| Technology | Role |
| :--- | :--- |
| **Python 3** | Core language for the backend API. |
| **Flask** | The web framework serving the RESTful API endpoints. |
| **MySQL** | The database where all the places and reviews live. |
| **REST API** | The bridge between the client and the data. |

-----

## 🌟 Key Features

The web client provides the following core functionalities to users:

1.  **🔒 User Authentication:** Secure login and logout to manage sessions.
2.  **🏠 Home Page (Index):** Lists all available places dynamically, giving you plenty of options\!
3.  **🔍 Place Filtering:** Adjust the max price slider to instantly filter places based on your budget.
4.  **🛌 Place Details View:** See everything about a place—description, amenities, and user reviews.
5.  **📝 Review Submission:** Logged-in users can share their experience and rate a stay\!

-----

## 🚀 Setup and Installation

To get the client running, you need to ensure the Flask API is already up and running on its default host.

### 1\. Backend Setup (Assumed)

You should have the main HBnB backend running, typically following these steps:

1.  **Clone the Repo (If necessary):**
    ```bash
    git clone https://github.com/vtiquet/holbertonschool-hbnb.git
    cd part4/hbnb
    ```
2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Database & Environment:**
      * Ensure your MySQL database is set up (e.g., via `setup_hbnb_db.sql`).
      * Set any necessary environment variables.
4.  **⚙️ Run the Flask API:**
    The API should be accessible at **`http://127.0.0.1:5000`**.
    ```bash
    python3 run.py
    ```

### 2\. 🌐 Frontend Client Usage

The client is a collection of static files designed to talk to the local API endpoint: `http://127.0.0.1:5000/api/v1`.

1.  Navigate to the directory containing the client files (e.g., `part4/`).
    ```bash
    cd ..
    ```
2.  Simply open the main HTML files in your browser\! 🥳
      * **Start Here:** Double-click `index.html`
      * **Go Straight to Login:** Double-click `login.html`

*(No separate web server is usually needed for the static client files.)*

-----

## 📁 File Structure

The client is kept simple and organized:

```
└── part4/
    ├── README.md              (You are here! 👋)
    └── hbnb                   (Folder for the Backend, same as in part3)
    └── web_client             (Folder for the Frontend Client)
        ├── index.html             (The main place listing page)
        ├── login.html             (The gateway to the app)
        ├── place.html             (Details for a specific listing)
        ├── add_review.html        (Form for adding new feedback)
        ├── styles/
        │   └── style.css          (All the beautiful visuals)
        └── scripts/
            └── scripts.js         (All the JavaScript logic and API calls)
```

-----

## ✅ How to Test

Time to try it out\!

### **🔑 Login**

1.  Head over to `login.html`.
2.  Use valid credentials (make sure you've seeded your database with a user\!).
3.  Successful login will whisk you away to `index.html`, and your "Login" link magically changes to "Logout." 🪄

### **🏘️ View and Filter Places**

1.  On `index.html`, marvel at the list of places fetched from the API.
2.  Drag the **"Max Price"** slider to instantly narrow down your choices\! 💰
3.  Click any listing card to zoom into the full details on `place.html`.

### **🌟 Add a Review**

1.  Make sure you're logged in\!
2.  Visit a place's details page (`place.html?id=<place_id>`).
3.  Find the review section and share your rating and comments.
4.  Hit **Submit Review**\! If all goes well, your valuable feedback will be posted for all to see. 👍

## Author
<div align="center">
  
| Author | Role | GitHub | Email |
|--------|------|--------|-------|
| **Valentin TIQUET** | Developer | [@vtiquet](https://github.com/vtiquet) | 11503@holbertonstudents.com |
</div>