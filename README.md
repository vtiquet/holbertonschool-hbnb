\<div align="center"\>\<img src="[https://github.com/ksyv/holbertonschool-web\_front\_end/blob/main/baniere\_holberton.png](https://github.com/ksyv/holbertonschool-web_front_end/blob/main/baniere_holberton.png)"\>\</div\>

# HBnB - Project: Your Home Away From Home 🏡✨

This repository contains the **HBnB (Holberton's BnB) project**, developed in four progressive parts, each building upon the previous to deliver a complete and robust accommodation management application. The project aims to design, implement, and deploy a **scalable web platform** with a clear architecture, a secure backend API, and a dynamic user interface.

-----

## 📑 Table of Contents:

  - [📦 HBnB - UML](https://www.google.com/search?q=%23hbnb---uml)
  - [🛠 HBnB - BL and API](https://www.google.com/search?q=%23hbnb---bl-and-api)
  - [🔐 HBnB - Auth & DB](https://www.google.com/search?q=%23hbnb---auth--db)
  - [💻 HBnB - Simple Web Client](https://www.google.com/search?q=%23hbnb---simple-web-client)

-----

## 📦 HBnB - UML (Part 1: The Blueprint) 📐

The foundational phase focused on architectural planning and design using **UML diagrams** to map out the application's structure and behavior.

  - **0. High-Level Package Diagram.md**: A 3-layer architecture (UML Package Diagram) showing layers and the **Facade Pattern**.
    ([View Diagram](https://www.google.com/search?q=https://github.com/vtiquet/holbertonschool-hbnb/blob/develop/part1/0.%2520High-Level%2520Package%2520Diagram.md))
  - **1. Detailed Class Diagram for Business Logic Layer.md**: A detailed UML Class Diagram for the Business Logic layer entities (**User**, **Place**, **Review**, **Amenity**).
    ([View Diagram](https://www.google.com/search?q=https://github.com/vtiquet/holbertonschool-hbnb/blob/develop/part1/1.%2520Detailed%2520Class%2520Diagram%2520for%2520Business%2520Logic%2520Layer.md))
  - **2. Sequence Diagrams for API Calls.md**: Four UML Sequence Diagrams to map the flow of information for key API calls across the three layers.
    ([View Diagrams](https://www.google.com/search?q=https://github.com/vtiquet/holbertonschool-hbnb/blob/develop/part1/2.%2520Sequence%2520Diagrams%2520for%2520API%2520Calls.md))
  - **3. Documentation Compilation.md**: A compilation of all diagrams and notes into a single, comprehensive **Technical Document**.

-----

## 🛠 HBnB - BL and API (Part 2: The Core Backend) ⚙️

This phase involved the initial implementation of the backend logic and RESTful API using **Python** and **Flask**, establishing the application's core functionality.

1.  **Layered Architecture:** Implemented a clean separation of concerns:
      * **Persistence Layer** ([`app/persistence`](https://github.com/vtiquet/holbertonschool-hbnb/blob/main/part2/hbnb/app/persistence%5D\(https://github.com/vtiquet/holbertonschool-hbnb/blob/main/part2/hbnb/app/persistence\))): Abstracted data storage logic.
      * **Service Layer** ([`app/services`](https://github.com/vtiquet/holbertonschool-hbnb/blob/main/part2/hbnb/app/services%5D\(https://github.com/vtiquet/holbertonschool-hbnb/blob/main/part2/hbnb/app/services\))): Established a **Facade** for centralized business logic.
      * **API Layer** ([`app/api`](https://github.com/vtiquet/holbertonschool-hbnb/blob/main/part2/hbnb/app/api%5D\(https://github.com/vtiquet/holbertonschool-hbnb/blob/main/part2/hbnb/app/api\))): Defined clear, standard REST endpoints.
2.  **Core Resource Management:** Full **CRUD** (Create, Read, Update, Delete) functionality was implemented for:
      * [**Users**](https://www.google.com/search?q=https://github.com/vtiquet/holbertonschool-hbnb/blob/main/part2/hbnb/app/api/v1/users.py)
      * [**Places**](https://www.google.com/search?q=https://github.com/vtiquet/holbertonschool-hbnb/blob/main/part2/hbnb/app/api/v1/places.py)
      * [**Reviews**](https://www.google.com/search?q=https://github.com/vtiquet/holbertonschool-hbnb/blob/main/part2/hbnb/app/api/v1/reviews.py)
      * [**Amenities**](https://www.google.com/search?q=https://github.com/vtiquet/holbertonschool-hbnb/blob/main/part2/hbnb/app/api/v1/amenities.py)
3.  **Environment Setup:** Finalized project configuration ([`config.py`](https://github.com/vtiquet/holbertonschool-hbnb/blob/main/part2/hbnb/config.py%5D\(https://github.com/vtiquet/holbertonschool-hbnb/blob/main/part2/hbnb/config.py\))) and dependency management ([`requirements.txt`](https://github.com/vtiquet/holbertonschool-hbnb/blob/main/part2/hbnb/requirements.txt%5D\(https://github.com/vtiquet/holbertonschool-hbnb/blob/main/part2/hbnb/requirements.txt\))).

-----

## 🔐 HBnB - Auth & DB (Part 3: Security & Persistence) 🔒

The backend transitioned to a secure, persistent, and scalable architecture, ready for real-world deployment.

1.  **JWT Authentication & Authorization:** Implemented user authentication using **Flask-JWT-Extended** and secured endpoints with **role-based access control** (RBAC).
2.  **SQLAlchemy ORM Integration:** Replaced the in-memory repository with a **SQLAlchemy-based persistence layer**, mapping all entities to a database (MySQL).
3.  **Relational Schema Design:** Designed the complete relational schema, including **one-to-many** and **many-to-many** relationships.
4.  **Data Security:** Integrated **Bcrypt** for secure password hashing.

-----

## 💻 HBnB - Simple Web Client (Part 4) 🚀

The grand finale\! This is the **user-facing front-end** built using **HTML5, CSS3, and Vanilla JavaScript**. It dynamically interacts with the secure Flask API (Parts 2 & 3) to offer a smooth, client-side experience. Key functionalities include:

  * **Place Listings & Filtering**: Users can view all available places and filter them by maximum price. 💰
  * **User Authentication**: Secure **login** and **logout** to manage sessions. 🔑
  * **Place Details**: View descriptions, amenities, and user reviews for individual listings.
  * **Review Submission**: Authenticated users can easily share their experience and rate a stay. ⭐

-----

## Authors

<div align="center">

| Author | Role | GitHub | Email |
|--------|------|--------|-------|
| **Loïc Le Guen** | Co-Developer | [@loicleguen](https://github.com/loicleguen) | 11510@holbertonstudents.com |
| **Valentin TIQUET** | Co-Developer | [@vtiquet](https://github.com/vtiquet) | 11503@holbertonstudents.com |

</div>