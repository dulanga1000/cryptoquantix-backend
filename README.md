# 🚀 Flask Backend Setup Guide

Follow these steps to set up and run the project locally.

---

## 📦 1. Create a Virtual Environment

It is highly recommended to isolate your Python dependencies.

```bash
python -m venv venv
```

### Activate the Virtual Environment

**On Windows:**

```bash
venv\Scripts\activate
```

**On Mac/Linux:**

```bash
source venv/bin/activate
```

---

## 📥 2. Install Dependencies

Install all required packages:

```bash
pip install flask flask-cors python-dotenv psycopg2-binary flask-sqlalchemy flask-migrate flask-bcrypt flask-jwt-extended
```

---

## 🗄️ 3. Apply Database Migrations

Initialize and update your database tables based on SQLAlchemy models:

```bash
flask db upgrade
```

---

## ▶️ 4. Run the Application

Start the Flask development server:

```bash
python app.py
```

---

## ⚙️ Notes

* Ensure your `.env` file is properly configured before running the app.
* Make sure PostgreSQL is running if you're using it as your database.
* Activate the virtual environment every time before running the project.

---
