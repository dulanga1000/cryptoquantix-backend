from flask import Blueprint

tonelli_bp = Blueprint('tonelli', __name__, url_prefix='/api/crypto')

from . import routes