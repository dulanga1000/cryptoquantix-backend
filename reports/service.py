from fpdf import FPDF
from datetime import datetime
import os
import tempfile
import uuid

def generate_portfolio_pdf(username, performance_data):
    """Draws the PDF report and returns the temporary file path."""
    pdf = FPDF()
    pdf.add_page()

    # --- Header Section ---
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt="CryptoQuantix - Portfolio Performance Report", ln=True, align='C')

    pdf.set_font("Arial", 'I', 11)
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    pdf.cell(0, 8, txt=f"Generated for: {username} | Date: {date_str}", ln=True, align='C')
    pdf.ln(10) 

    # --- Summary Section ---
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="Financial Summary", ln=True)

    pdf.set_font("Arial", '', 11)
    
    # 🔥 FIXED: Using .get() makes this 100% crash-proof even if data is missing
    inv = performance_data.get('total_invested', 0.0)
    c_val = performance_data.get('crypto_value', 0.0)
    usd_bal = performance_data.get('usd_balance', 0.0)
    p_l = performance_data.get('overall_p_l', 0.0)

    pdf.cell(0, 8, txt=f"Total Capital Invested: ${inv:,.2f}", ln=True)
    pdf.cell(0, 8, txt=f"Current Crypto Value: ${c_val:,.2f}", ln=True)
    pdf.cell(0, 8, txt=f"Available USD Cash: ${usd_bal:,.2f}", ln=True)
    pdf.cell(0, 8, txt=f"Net Profit / Loss: ${p_l:,.2f}", ln=True)
    pdf.ln(5)

    # --- Trade Counts ---
    pdf.set_font("Arial", 'I', 10)
    buys = performance_data.get('buy_count', 0)
    sells = performance_data.get('sell_count', 0)
    swaps = performance_data.get('swap_count', 0)
    pdf.cell(0, 8, txt=f"Total Trading Activity -> Buys: {buys} | Sells: {sells} | Swaps: {swaps}", ln=True)
    pdf.ln(10)

    # --- Table Header ---
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 10, txt="Asset Breakdown", ln=True)

    # Table Column Widths
    col_w = [40, 30, 60, 60] 
    
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(col_w[0], 10, "Asset Symbol", border=1, align='C')
    pdf.cell(col_w[1], 10, "Quantity", border=1, align='C')
    pdf.cell(col_w[2], 10, "Avg Buy Price", border=1, align='C')
    pdf.cell(col_w[3], 10, "Current P&L", border=1, align='C')
    pdf.ln()

    # --- Table Rows (Data) ---
    pdf.set_font("Arial", '', 10)
    assets = performance_data.get('assets', [])
    
    if not assets:
        pdf.cell(sum(col_w), 10, "No crypto assets currently held in portfolio.", border=1, align='C')
        pdf.ln()
    else:
        for asset in assets:
            sym = str(asset.get('symbol', ''))
            qty = str(asset.get('quantity', 0))
            buy_p = asset.get('buy_price', 0.0)
            pl = asset.get('p_l', 0.0)
            
            pdf.cell(col_w[0], 10, sym, border=1, align='C')
            pdf.cell(col_w[1], 10, qty, border=1, align='C')
            pdf.cell(col_w[2], 10, f"${buy_p:,.2f}", border=1, align='C')
            pdf.cell(col_w[3], 10, f"${pl:,.2f}", border=1, align='C')
            pdf.ln()

    # 🔥 FIXED: Safe Temporary File Generation that bypasses Windows Lock restrictions
    temp_dir = tempfile.gettempdir()
    unique_filename = f"report_{uuid.uuid4().hex}.pdf"
    temp_path = os.path.join(temp_dir, unique_filename)
    
    pdf.output(temp_path)
    
    return temp_path