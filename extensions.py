from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

# 🔥 Database instance (SQLAlchemy)
db = SQLAlchemy()

# 🔐 Password hashing (bcrypt)
bcrypt = Bcrypt()

# 🔑 JWT authentication
jwt = JWTManager()