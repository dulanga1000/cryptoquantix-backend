from flask import Blueprint, send_file, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from database.models import User, Trade
from user_analytics.service import calculate_portfolio_performance
from .service import generate_portfolio_pdf
import os

reports_bp = Blueprint('reports', __name__, url_prefix='/api/reports')

@reports_bp.route('/portfolio/download', methods=['GET'])
@jwt_required()
def download_portfolio_report():
    # 1. Identify the user
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({"msg": "User not found"}), 404

    # 2. Gather their financial data using M5's existing logic
    trades = Trade.query.filter_by(user_id=user_id).all()
    performance_data = calculate_portfolio_performance(trades)

    try:
        # 3. Generate the PDF and get the file path
        pdf_path = generate_portfolio_pdf(user.username, performance_data)

        # 4. Send the file securely to the user's browser
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"{user.username}_CryptoQuantix_Report.pdf",
            mimetype='application/pdf'
        )
    except Exception as e:
        print(f"PDF ERROR: {e}")
        return jsonify({"msg": "Failed to generate PDF report"}), 500