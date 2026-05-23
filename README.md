Eternagem – Luxury Jewelry E-Commerce Platform

A full-featured jewelry e-commerce web application built using Django, PostgreSQL, HTML, CSS, JavaScript, and Bootstrap.
The platform provides a seamless shopping experience for users along with a powerful admin management system.

🚀 Features

👤 User Features
User Registration & Login
OTP-based Authentication
Google OAuth Login
Product Browsing & Filtering
Product Categories & Sorting
Cart & Wishlist Management
Secure Checkout Process
Razorpay Payment Integration
Wallet System & Order Retry
Order Tracking
Invoice PDF Download
User Profile Management

🛠️ Admin Features
Custom Admin Dashboard
Product Management
Category Management
Order Management
User Management
Stock & Inventory Control
Sales Monitoring

🧰 Tech Stack
Backend
Python
Django
PostgreSQL
Frontend
HTML5
CSS3
JavaScript
Bootstrap
Third-Party Integrations
Razorpay Payment Gateway
Google OAuth Authentication
SMTP Email Service
Deployment
AWS EC2 / GCP VM
Gunicorn
Nginx

📂 Project Structure
Eternagem/
│
├── register/
├── product/
├── category/
├── cart/
├── order/
├── coupon/
├── userprofile/
├── customadmin/
│
├── static/
├── media/
├── templates/
│
├── jewellery/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── manage.py
└── requirements.txt


Run Migrations
python manage.py makemigrations
python manage.py migrate

Create Superuser
python manage.py createsuperuser

Run Server
python manage.py runserver

Features:

Online Payment
Payment Verification
Retry Failed Orders
Wallet Refund Integration

🔐 Authentication System
Django Authentication
Email OTP Verification
Google OAuth Login
Custom User Model
Block/Unblock Users

📄 Invoice System

Users can:

Download order invoices in PDF format
View order history
Track payment details
☁️ Deployment

Production deployment configured using:

AWS EC2 / GCP VM
Gunicorn
Nginx
PostgreSQL

📚 What I Learned
Django Models, Views & ORM
Authentication & Authorization
Payment Gateway Integration
Production Deployment
Nginx & Gunicorn Configuration
PostgreSQL Database Handling
Full-Stack Project Architecture

🔮 Future Improvements
Product Reviews & Ratings
Advanced Search
Email Notifications
Coupon Recommendation System
Analytics Dashboard
Docker Deployment
👨‍💻 Author

Sneha S

GitHub: https://github.com/snehasivadas21/jewellery.git
📜 License

This project is developed for educational and portfolio purposes.

