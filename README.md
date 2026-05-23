# 💎 Eternagem - Jewelry E-Commerce Platform

A fully functional production-level jewelry e-commerce platform built using **Django**, **PostgreSQL**, **HTML**, **CSS**, **JavaScript**, and **Bootstrap**.

The platform includes secure authentication, product management, online payments, wallet integration, order management, and a complete admin dashboard.

---

# 🚀 Features

## 👤 User Features

* User Registration & Login
* OTP Verification System
* Google Authentication
* Product Browsing & Filtering
* Category-Based Product Listing
* Product Sorting & Search
* Wishlist Functionality
* Add to Cart
* Secure Checkout Flow
* Razorpay Payment Gateway Integration
* Wallet & Order Retry System
* User Profile Management
* Address Management
* Order History & Tracking
* Invoice PDF Download
* Responsive UI Design

---

## 🛠️ Admin Features

* Admin Dashboard
* Product Management
* Category Management
* Order Management
* User Management
* Stock & Inventory Control
* Coupon Management
* Sales Monitoring
* Order Status Updates
* User Blocking / Unblocking

---

# 🧰 Tech Stack

| Technology       | Usage                    |
| ---------------- | ------------------------ |
| Django           | Backend Framework        |
| PostgreSQL       | Database                 |
| HTML5            | Frontend Structure       |
| CSS3             | Styling                  |
| Bootstrap        | Responsive UI            |
| JavaScript       | Client-Side Interactions |
| Razorpay         | Payment Gateway          |
| Gunicorn         | WSGI Server              |
| Nginx            | Reverse Proxy Server     |
| AWS EC2 / GCP VM | Deployment               |

---

# 📂 Project Structure

```bash
Eternagem/
│
├── register/
├── customadmin/
├── category/
├── product/
├── cart/
├── order/
├── coupon/
├── userprofile/
│
├── static/
├── media/
├── templates/
│
├── manage.py
├── requirements.txt
└── README.md
```

---

# ⚙️ Installation & Setup

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/snehasivadas21/jewellery.git
cd jewellery
```

---

## 2️⃣ Create Virtual Environment

```bash
python -m venv env
```

### Activate Environment

#### Windows

```bash
env\Scripts\activate
```

#### Linux / Mac

```bash
source env/bin/activate
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4️⃣ Configure Environment Variables

Create a `.env` file in the project root.

## 5️⃣ Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 6️⃣ Create Superuser

```bash
python manage.py createsuperuser
```

---

## 7️⃣ Run Development Server

```bash
python manage.py runserver
```

Open:

```bash
http://127.0.0.1:8000/
```

---

# 💳 Payment Integration

This project uses **Razorpay** for secure online payments.

Features include:

* Online Payment Processing
* Failed Order Retry
* Wallet Refund Handling
* Payment Verification

---

# 🔐 Authentication System

* Django Custom User Model
* OTP Verification
* Google OAuth Login
* Session-Based Authentication
* Blocked User Handling

---

# ☁️ Deployment

The project is production-ready and can be deployed using:

* AWS EC2
* Google Cloud Platform (GCP)
* Nginx
* Gunicorn

---

# 📚 What I Learned

* Django Architecture & ORM
* Authentication & Authorization
* Payment Gateway Integration
* Wallet & Order Logic
* PostgreSQL Database Design
* Static & Media File Handling
* Production Deployment with Nginx & Gunicorn
* Cloud Hosting on AWS / GCP

---

# 🔮 Future Enhancements

* Product Reviews & Ratings
* Advanced Search & Filtering
* Email Notifications
* Analytics Dashboard
* Multi-Vendor Support
* Docker Deployment

---

# 👨‍💻 Author

### Sneha S

Passionate Full Stack Django Developer focused on building scalable and production-ready web applications.

---

# ⭐ Support

If you like this project, consider giving it a ⭐ on GitHub.
