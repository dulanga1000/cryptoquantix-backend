from flask import Blueprint

market_bp = Blueprint('market', __name__, url_prefix='/api/market')

from . import routes