from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import sys
import psycopg2
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text

# Set higher limit for large integer string conversions
sys.set_int_max_str_digits(20577)  

# import auth + extensions
from extensions import bcrypt, jwt
from auth import auth_bp   
from fibonacci import fibonacci_bp
from tonelli_shanks import tonelli_bp
from market_data import market_bp
from user_analytics import analytics_bp
from reports import reports_bp

load_dotenv()

# Safely fetch the database URL from Azure's environment variables
DATABASE_URL = os.getenv("DATABASE_URI") or os.getenv("DATABASE_URL")

app = Flask(__name__)

# DB CONFIG
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# JWT CONFIG
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY", "super-secret-key")

from database.models import db  

# INIT EXTENSIONS
db.init_app(app)
bcrypt.init_app(app)   
jwt.init_app(app)      
CORS(app)

from flask_migrate import Migrate
migrate = Migrate(app, db)

# REGISTER BLUEPRINTS
app.register_blueprint(auth_bp)   
app.register_blueprint(fibonacci_bp) 
app.register_blueprint(tonelli_bp) 
app.register_blueprint(market_bp)
app.register_blueprint(analytics_bp)
app.register_blueprint(reports_bp)

def get_connection():
    return psycopg2.connect(DATABASE_URL)

@app.route("/")
def home():
    return "HOME WORKING ✅"

@app.route("/check")
def check():
    return "NEW CODE LOADED ✅"

# TEST DB CONNECTION
@app.route("/test-db")
def test_db():
    try:
        conn = get_connection()
        conn.close()
        return "DB Connected ✅"
    except Exception as e:
        return str(e)

# ORM TEST (SQLAlchemy)
@app.route("/orm-test")
def orm_test():
    try:
        db.session.execute(text('SELECT 1'))
        return "ORM Connected ✅"
    except Exception as e:
        return str(e)

# HEALTH CHECK
@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "message": "API is running ✅"
    })

# DB STATUS
@app.route("/api/db/status")
def db_status():
    try:
        db.session.execute(text('SELECT 1'))
        return jsonify({
            "db": "connected ✅"
        })
    except Exception as e:
        return jsonify({"error": str(e)})

# EMERGENCY AZURE DATABASE FIX ROUTE
@app.route("/api/db/fix")
def fix_db():
    try:
        db.session.execute(text("ALTER TABLE trades ADD COLUMN action VARCHAR(20) DEFAULT 'SYSTEM';"))
        db.session.commit()
        return jsonify({"status": "SUCCESS", "msg": "The 'action' column was successfully added to your Azure Database! Your app will now work."}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "NOTE", "msg": f"Column might already exist or error occurred: {str(e)}"}), 200

# SEED DATA
@app.route("/api/seed")
def seed_data():
    try:
        from database.models import User

        if User.query.first():
            return {"message": "Data already exists ✅"}

        user1 = User(username="testuser1", password="123456")
        user2 = User(username="testuser2", password="123456")

        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        return {"message": "Seed data inserted ✅"}

    except Exception as e:
        return {"error": str(e)}

if __name__ == '__main__':
    print("THIS FILE IS RUNNING ✅")   
    app.run(host="0.0.0.0", port=5000, debug=True)