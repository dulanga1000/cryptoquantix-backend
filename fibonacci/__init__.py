from flask import Blueprint
fibonacci_bp = Blueprint('fibonacci', __name__, url_prefix='/api/fibonacci')

from . import routes