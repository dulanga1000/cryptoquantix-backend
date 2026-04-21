from fpdf import FPDF
from datetime import datetime
import os
from tempfile import NamedTemporaryFile

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
    pdf.ln(10) # Add empty line

    # --- Summary Section ---
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, txt="Financial Summary", ln=True)

    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 8, txt=f"Total Capital Invested: ${performance_data['total_invested']:,.2f}", ln=True)
    
    # 🔥 FIXED: Use crypto_value and usd_balance instead of total_value
    pdf.cell(0, 8, txt=f"Current Crypto Value: ${performance_data['crypto_value']:,.2f}", ln=True)
    pdf.cell(0, 8, txt=f"Available USD Cash: ${performance_data['usd_balance']:,.2f}", ln=True)
    
    p_l = performance_data['overall_p_l']
    pdf.cell(0, 8, txt=f"Net Profit / Loss: ${p_l:,.2f}", ln=True)
    pdf.ln(5)

    # 🔥 NEW: Output the Action Counts
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 8, txt=f"Total Trading Activity -> Buys: {performance_data.get('buy_count', 0)} | Sells: {performance_data.get('sell_count', 0)} | Swaps: {performance_data.get('swap_count', 0)}", ln=True)
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
    if not performance_data['assets']:
        pdf.cell(sum(col_w), 10, "No crypto assets currently held in portfolio.", border=1, align='C')
        pdf.ln()
    else:
        for asset in performance_data['assets']:
            pdf.cell(col_w[0], 10, str(asset['symbol']), border=1, align='C')
            pdf.cell(col_w[1], 10, str(asset['quantity']), border=1, align='C')
            pdf.cell(col_w[2], 10, f"${asset['buy_price']:,.2f}", border=1, align='C')
            pdf.cell(col_w[3], 10, f"${asset['p_l']:,.2f}", border=1, align='C')
            pdf.ln()

    # --- Save to Temporary File ---
    temp_file = NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_file.name)
    
    return temp_file.name