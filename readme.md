# 🏪 Vendora - Platform Documentation

> **Empowering local vendors in India to connect with customers through digital presence**

---

## 📑 Table of Contents

- [🎯 Introduction](#-introduction)
- [⚙️ Tech Stack](#️-tech-stack)
- [📁 Architecture](#-architecture)
- [🗄️ Database](#️-database)
- [🎨 Design System](#-design-system)
- [🔐 Authentication](#-authentication)
- [💼 Business Logic](#-business-logic)
- [✨ Features](#-features)
- [☁️ Deployment](#️-deployment)
- [🚀 Quick Start](#-quick-start)

---

## 🎯 Introduction

**Vendora** is a web platform connecting local service providers (barbers, mechanics, plumbers, etc.) with customers in India. Vendors create professional pages where customers can discover and book appointments.

### 👥 Target Users
- **Vendors** 🛠️: Local service providers seeking digital presence
- **Customers** 👤: People looking to book local services

---

## ⚙️ Tech Stack

### Backend
- **Flask** 🐍 - Python web framework
- **SQLAlchemy** 🗃️ - ORM for database
- **Flask-Login** 🔑 - Session management
- **Flask-Bcrypt** 🔒 - Password security

### Database
- **MySQL** 🐬 - Production database (Aiven Cloud)
- **Alembic** 📊 - Database migrations

### Frontend
- **Tailwind CSS v3** 🎨 - Utility-first CSS
- **Jinja2** 📝 - Template engine
- **Inter Font** ✍️ - Typography

### Cloud Services
- **Vercel** 🚀 - Application hosting
- **Cloudinary** ☁️ - Image storage & CDN
- **Aiven** 🗄️ - Managed MySQL

---

## 📁 Architecture

### Project Structure

```
vendora2/
├── run.py                    # 🚪 Entry point
├── requirements.txt          # 📦 Dependencies
├── vercel.json              # ⚙️ Deployment config
└── vendora_app/
    ├── app.py               # 🏭 App factory
    ├── extensions.py        # 🔌 Extensions init
    ├── templates/           # 🎨 Base templates
    │   ├── base.html
    │   ├── headers/
    │   └── sidebar/
    ├── migrations/          # 📊 DB migrations
    └── blueprints/          # 🧩 Modular routes
        ├── auth/           # 🔐 Authentication
        ├── vendor/         # 🏪 Vendor features
        ├── customer/       # 👤 Customer features
        ├── appointment/    # 📅 Appointments
        └── core/           # 🏠 Core routes
```

### 🏗️ Architecture Benefits

| Pattern                  | Benefit                              |
| ------------------------ | ------------------------------------ |
| **Blueprint Pattern**    | Modular, scalable, maintainable code |
| **Factory Pattern**      | Testable, configurable app instances |
| **Template Inheritance** | DRY principle, consistent UI         |
| **Migrations**           | Version-controlled schema changes    |

---

## 🗄️ Database

### Schema Overview

#### 👤 **users** Table
Primary authentication table with role flags.

| Field           | Type         | Description                  |
| --------------- | ------------ | ---------------------------- |
| `uid`           | INT          | Primary key                  |
| `username`      | VARCHAR(100) | Unique username              |
| `password`      | VARCHAR(80)  | Bcrypt hashed                |
| `is_customer`   | BOOLEAN      | Customer role flag           |
| `is_vendor`     | BOOLEAN      | Vendor role flag             |
| `last_role`     | VARCHAR(20)  | Last logged-in role          |
| `name`          | VARCHAR(50)  | Display name                 |
| `profile_img`   | VARCHAR(500) | Cloudinary URL               |
| `business_imgs` | JSON         | Array of business image URLs |

#### 🏪 **vendor** Table
Vendor business information.

| Field              | Type         | Description         |
| ------------------ | ------------ | ------------------- |
| `id`               | INT          | Primary key         |
| `user_id`          | INT          | Foreign key → users |
| `business_name`    | VARCHAR(100) | Business name       |
| `business_address` | VARCHAR(200) | Location            |
| `phone_number`     | VARCHAR(20)  | Contact             |
| `rating`           | FLOAT        | Average rating      |
| `rater_no`         | INT          | Number of ratings   |

#### 👥 **customer** Table
Customer profile information.

| Field       | Type         | Description         |
| ----------- | ------------ | ------------------- |
| `id`        | INT          | Primary key         |
| `user_id`   | INT          | Foreign key → users |
| `full_name` | VARCHAR(100) | Customer name       |
| `address`   | VARCHAR(200) | Address             |
| `phone`     | VARCHAR(20)  | Phone number        |

### 🔗 Relationships

```
users (1) ──< (1) customer
users (1) ──< (1) vendor
users (1) ──< (*) note
```

**Key Features:**
- ✅ Cascade deletes (user deletion removes profiles)
- ✅ Dual role support (user can be both customer & vendor)
- ✅ JSON storage for business images

---

## 🎨 Design System

### 🎨 Color Palette

| Color          | Hex       | Usage                 |
| -------------- | --------- | --------------------- |
| **Primary**    | `#1D4ED8` | Buttons, links, brand |
| **Secondary**  | `#4B5563` | Text, borders         |
| **Background** | `#F3F4F6` | Page backgrounds      |
| **Surface**    | `#FFFFFF` | Cards, containers     |
| **Footer**     | `#111827` | Footer background     |

### ✍️ Typography
- **Font**: Inter (Google Fonts)
- **Weights**: 400, 500, 600, 700

### 📱 Responsive Design
- **Mobile-first** approach
- Breakpoints: `sm:640px`, `md:768px`, `lg:1024px`, `xl:1280px`

### 🎯 Design Principles
- ✅ Minimal & clean
- ✅ Flat design
- ✅ Consistent patterns
- ✅ Accessible UI

---

## 🔐 Authentication

### 🔑 Key Features

#### **Role-Based Access Control**
```python
# Users can ONLY login with roles they're registered for
if role == 'vendor' and not user.is_vendor:
    flash('Not registered as vendor', 'danger')
    return redirect('auth.signup')
```

#### **Password Security**
- ✅ **Bcrypt hashing** with salt
- ✅ **No plain text** storage
- ✅ **One-way encryption**

#### **Session Management**
- ✅ **Flask-Login** for secure sessions
- ✅ **Role tracking** via `last_role`
- ✅ **Profile verification** before dashboard access

### 🔄 Authentication Flow

```
Signup → Select Role → Create Account
  ↓
Login → Verify Role → Check Profile
  ↓
Profile Setup (if needed) → Dashboard
```

### 🛡️ Security Features

| Feature                   | Status |
| ------------------------- | ------ |
| Password Hashing (Bcrypt) | ✅      |
| Session Management        | ✅      |
| Role Verification         | ✅      |
| Route Protection          | ✅      |
| SQL Injection Prevention  | ✅      |
| Environment Variables     | ✅      |

---

## 💼 Business Logic

### 📝 User Registration

1. **New User**: Creates account with selected role
2. **Existing User**: 
   - Validates password
   - Adds role if not assigned
   - Shows message if role exists

### 🔐 Login Process

1. **Username & Password** validation
2. **Role Verification** ⚠️ (Critical: Must be registered for role)
3. **Profile Check**:
   - No profile → Redirect to setup
   - Profile exists → Dashboard

### 🏪 Vendor Profile Setup

**Required Fields:**
- Business name, address
- Contact numbers (phone, WhatsApp)
- Business hours, payment methods
- Year of establishment
- **Business images** (multiple, Cloudinary)

**Process:**
- Images uploaded to `vendora/{user_id}/business_img/`
- URLs stored in `business_imgs` JSON array
- Initial rating set to 0.0

### 👤 Customer Profile Setup

**Required Fields:**
- Full name
- Address
- Phone number

### 🔍 Vendor Discovery

- **Browse all vendors** on homepage
- **Search** by business name (case-insensitive)
- **View details** with images, ratings, contact info

### 🖼️ Image Management

| Type     | Storage    | Path Pattern                             |
| -------- | ---------- | ---------------------------------------- |
| Profile  | Cloudinary | `vendora/{uid}/profile_img`              |
| Business | Cloudinary | `vendora/{uid}/business_img/img_{index}` |

**Features:**
- ✅ Multiple business images
- ✅ Overwrite profile image
- ✅ Append business images
- ✅ CDN delivery

---

## ✨ Features

### ✅ Implemented Features

#### 🔐 Authentication
- [x] User signup with role selection
- [x] Login with role verification
- [x] Logout & session management
- [x] Profile update (name, image)
- [x] Account deletion

#### 🏪 Vendor Features
- [x] Dashboard
- [x] Profile setup & update
- [x] Business image uploads
- [x] Profile management

#### 👤 Customer Features
- [x] Dashboard
- [x] Profile setup
- [x] Vendor discovery
- [x] Search functionality
- [x] Vendor detail view

#### 🎨 UI Features
- [x] Responsive design
- [x] Flash messages
- [x] Role-based navigation
- [x] Image galleries

### 🚧 UI Ready (Backend Extendable)

- [ ] Appointment booking system
- [ ] Analytics dashboard
- [ ] Reviews & ratings
- [ ] Support system

---

## ☁️ Deployment

### 🚀 Vercel Configuration

```json
{
  "version": 2,
  "builds": [{"src": "run.py", "use": "@vercel/python"}],
  "routes": [{"src": "/(.*)", "dest": "run.py"}]
}
```

### 🗄️ Database: Aiven Cloud

- **Host**: `mysql-3b0838a6-priyamjainsocial-b642.i.aivencloud.com`
- **Port**: `27509`
- **Type**: Managed MySQL
- **Connection**: Environment variable `DB_PASSWORD`

### ☁️ Cloudinary

- **Purpose**: Image storage & CDN
- **Config**: Environment variables (`c_cloud_name`, `c_api_key`, `c_api_secret`)

### 🔐 Environment Variables

```env
DB_PASSWORD=your_password
c_cloud_name=your_cloud_name
c_api_key=your_api_key
c_api_secret=your_api_secret
SECRET_KEY=your_secret_key
```

### 📋 Deployment Checklist

- [ ] Set environment variables
- [ ] Run database migrations
- [ ] Test database connection
- [ ] Verify Cloudinary credentials
- [ ] Deploy to Vercel

---

## 🚀 Quick Start

### 🛠️ Development Setup

```bash
# 1. Clone repository
git clone <repo-url>
cd vendora2

# 2. Create virtual environment
python -m venv vendenv
vendenv\Scripts\activate  # Windows
# source vendenv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables
# Create .env file with required variables

# 5. Run migrations
flask db upgrade

# 6. Run application
python run.py
```

### 🌐 Access Routes

| Route                | URL                   | Description       |
| -------------------- | --------------------- | ----------------- |
| 🏠 Home               | `/`                   | Vendor discovery  |
| 🔐 Login              | `/auth/login`         | User login        |
| 📝 Signup             | `/auth/signup`        | User registration |
| 🏪 Vendor Dashboard   | `/vendor/dashboard`   | Vendor portal     |
| 👤 Customer Dashboard | `/customer/dashboard` | Customer portal   |
| 🔍 Browse Vendors     | `/customer/homepage`  | Vendor list       |

### 📍 Key File Locations

| Component       | Location                                     |
| --------------- | -------------------------------------------- |
| **Models**      | `vendora_app/blueprints/{module}/models.py`  |
| **Routes**      | `vendora_app/blueprints/{module}/routes.py`  |
| **Templates**   | `vendora_app/blueprints/{module}/templates/` |
| **App Config**  | `vendora_app/app.py`                         |
| **Entry Point** | `run.py`                                     |

### 🔄 Common Commands

```bash
# Create migration
flask db migrate -m "description"

# Apply migration
flask db upgrade

# Rollback migration
flask db downgrade
```

---

## 📊 System Flow

```
User → Login → Role Check → Profile Check → Dashboard
  ↓
Customer: Browse Vendors → View Details → Book (Future)
  ↓
Vendor: Manage Profile → View Appointments → Analytics
```

---

## 🎯 Key Highlights

- ✅ **Modular Architecture** - Blueprint pattern for scalability
- ✅ **Secure Authentication** - Role-based access with strict verification
- ✅ **Cloud Infrastructure** - Vercel + Aiven + Cloudinary
- ✅ **Modern UI** - Tailwind CSS with responsive design
- ✅ **Image Management** - Cloudinary integration
- ✅ **Database Migrations** - Version-controlled schema

---

## 📞 Support

For questions or contributions, visit the developer page at `/developer` or contact the development team.

---

**📝 Documentation Version**: 1.0  
**📅 Last Updated**: 2025  
**👨‍💻 Maintained By**: Vendora Development Team

---

<div align="center">

**Made with ❤️ for local vendors in India**

</div>
