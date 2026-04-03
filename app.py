from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import psycopg2
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text  


load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

from database.models import db  

db.init_app(app)
CORS(app)

from flask_migrate import Migrate

migrate = Migrate(app, db)


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
        db.session.execute(text('SELECT 1'))   # ✅ FIXED
        return "ORM Connected ✅"
    except Exception as e:
        return str(e)
        
# Fibonacci API
@app.route('/api/fibonacci')
def fibonacci():
    n = int(request.args.get('n'))
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return jsonify({"result": a})

# Tonelli (simple placeholder)
@app.route('/api/verify', methods=['POST'])
def verify():
    data = request.json
    n = data.get('n')
    p = data.get('p')
    return jsonify({
        "message": "Verification logic here",
        "n": n,
        "p": p
    })
@app.route("/api/health")
def health():
    return jsonify({
        "status": "ok",
        "message": "API is running ✅"
    })

@app.route("/api/db/status")
def db_status():
    try:
        db.session.execute(text('SELECT 1'))
        return jsonify({
            "db": "connected ✅"
        })
    except Exception as e:
        return jsonify({"error": str(e)})

@app.route("/api/seed")
def seed_data():
    try:
        from database.models import User

        
        if User.query.first():
            return {"message": "Data already exists ✅"}

        # Insert sample users
        user1 = User(email="test1@example.com", password="123456")
        user2 = User(email="test2@example.com", password="123456")

        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        return {"message": "Seed data inserted ✅"}

    except Exception as e:
        return {"error": str(e)}



if __name__ == '__main__':
    print("THIS FILE IS RUNNING ✅")   
    app.run(debug=True)