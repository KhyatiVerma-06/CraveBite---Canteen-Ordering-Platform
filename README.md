# 🍔 CraveBite – Canteen Ordering Platform

CraveBite is a full-stack canteen ordering platform built with Django and designed to provide a simple and user-friendly food ordering experience.

The project includes a responsive frontend for browsing food items, viewing offers, managing the cart, and handling user login/signup functionality. The backend is developed using Django with database support for managing application data.

## 🚀 Features

- 🏠 Home page with food categories and featured items
- 🍕 Menu page for browsing available food items
- 🛒 Shopping cart functionality
- 🔐 User Login and Signup pages
- 🎁 Offers and promotional section
- ℹ️ About page
- 📱 Responsive and user-friendly interface
- 🖼️ Food item images and custom UI styling
- 🗄️ Django-based backend
- 🔌 Django REST/API-ready backend structure
- 💾 Database integration through Django models

## 🛠️ Tech Stack

### Frontend
- HTML5
- CSS3
- JavaScript

### Backend
- Python
- Django

### Database
- PostgreSQL
- pgAdmin

### Tools
- Git
- GitHub
- Visual Studio Code

## 📁 Project Structure

```text
CraveBite---Canteen-Ordering-Platform/
│
├── .gitignore
│
└── FoodCourt/
    │
    ├── manage.py
    │
    ├── FoodCourt/
    │   ├── __init__.py
    │   ├── settings.py
    │   ├── urls.py
    │   ├── asgi.py
    │   └── wsgi.py
    │
    └── FoodName/
        │
        ├── migrations/
        │   ├── __init__.py
        │   └── 0001_initial.py
        │
        ├── Static/
        │   ├── css/
        │   │   └── style.css
        │   └── images/
        │       └── food images
        │
        ├── templates/
        │   ├── Home.html
        │   ├── Menu.html
        │   ├── Cart.html
        │   ├── Login.html
        │   ├── Signup.html
        │   ├── About.html
        │   └── Offers.html
        │
        ├── admin.py
        ├── apps.py
        ├── models.py
        ├── tests.py
        └── views.py
