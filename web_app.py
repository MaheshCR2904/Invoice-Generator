"""
Invoice Generator System - Web Application (Flask)
================================================

Author: Invoice Generator System
Date: 2026-03-28
"""

from flask import Flask, render_template, request, redirect, url_for, flash, send_file, make_response
from datetime import datetime
import os
import uuid

# Add current directory to path
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from invoice_manager import InvoiceManager
from pdf_generator import PDFGenerator
from invoice_models import Invoice, Customer, Product, CompanyDetails

app = Flask(__name__)
app.secret_key = 'invoice-generator-secret-key-2026'

# Data directory
DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)


def get_manager():
    """Get InvoiceManager instance."""
    return InvoiceManager()


def get_pdf_generator():
    """Get PDFGenerator instance."""
    return PDFGenerator()


def get_all_invoices():
    """Get all invoices from data directory."""
    invoices = []
    if DATA_DIR.exists():
        for f in DATA_DIR.glob("*.json"):
            try:
                import json
                with open(f, 'r') as fp:
                    data = json.load(fp)
                    invoice = Invoice.from_dict(data)
                    invoices.append(invoice)
            except Exception:
                pass
    return sorted(invoices, key=lambda x: x.created_at, reverse=True)


def get_stats():
    """Get invoice statistics."""
    invoices = get_all_invoices()
    if not invoices:
        return {
            'total_invoices': 0,
            'total_amount': 0,
            'avg_amount': 0,
            'max_amount': 0,
            'min_amount': 0,
            'total_tax': 0
        }
    
    totals = [inv.total for inv in invoices]
    taxes = [inv.tax_amount for inv in invoices]
    
    return {
        'total_invoices': len(invoices),
        'total_amount': sum(totals),
        'avg_amount': sum(totals) / len(totals) if totals else 0,
        'max_amount': max(totals) if totals else 0,
        'min_amount': min(totals) if totals else 0,
        'total_tax': sum(taxes)
    }


def get_monthly_stats():
    """Get monthly statistics."""
    invoices = get_all_invoices()
    monthly = {}
    
    for inv in invoices:
        month_key = inv.created_at.strftime("%Y-%m")
        if month_key not in monthly:
            monthly[month_key] = {'count': 0, 'total': 0}
        monthly[month_key]['count'] += 1
        monthly[month_key]['total'] += inv.total
    
    return dict(sorted(monthly.items(), reverse=True))


@app.route('/')
def index():
    """Home page."""
    stats = get_stats()
    all_invoices = get_all_invoices()
    recent = all_invoices[:5] if len(all_invoices) > 5 else all_invoices
    return render_template('index.html', stats=stats, recent_invoices=recent)


@app.route('/create', methods=['GET', 'POST'])
def create_invoice():
    """Create new invoice."""
    if request.method == 'POST':
        try:
            # Get form data
            customer_name = request.form.get('customer_name', '').strip()
            customer_address = request.form.get('customer_address', '').strip()
            customer_email = request.form.get('customer_email', '').strip()
            customer_phone = request.form.get('customer_phone', '').strip()
            tax_rate = float(request.form.get('tax_rate', '18'))
            notes = request.form.get('notes', '').strip()
            
            # Get items
            descriptions = request.form.getlist('item_description[]')
            quantities = request.form.getlist('item_quantity[]')
            unit_prices = request.form.getlist('item_unit_price[]')
            
            # Validate
            if not customer_name:
                flash('Customer name is required', 'error')
                return redirect(url_for('create_invoice'))
            
            # Create items
            items = []
            for i, desc in enumerate(descriptions):
                if desc and i < len(quantities) and i < len(unit_prices):
                    qty = int(quantities[i]) if i < len(quantities) else 1
                    price = float(unit_prices[i]) if i < len(unit_prices) else 0
                    if desc.strip():
                        items.append(Product(
                            name=desc.strip(),
                            quantity=qty,
                            price_per_unit=price
                        ))
            
            if not items:
                flash('At least one item is required', 'error')
                return redirect(url_for('create_invoice'))
            
            # Create default company
            company = CompanyDetails(
                name="Your Company Name",
                address="123 Business Street, City, State - PIN Code",
                phone="+91 1234567890",
                email="contact@company.com",
                gst_number="XX9999XX999999"
            )
            
            # Create customer (make phone and email optional for web)
            if not customer_phone:
                customer_phone = "N/A"
            if not customer_email:
                customer_email = "N/A"
            
            customer = Customer(
                name=customer_name,
                phone=customer_phone,
                email=customer_email,
                address=customer_address
            )
            
            # Create invoice
            invoice = Invoice(
                customer=customer,
                company=company,
                tax_rate=tax_rate,
                signature=""
            )
            
            # Add products
            for item in items:
                invoice.add_product(item)
            
            # Add notes if provided
            if notes:
                invoice.signature = notes
            
            # Save invoice
            manager = get_manager()
            manager.save_invoice(invoice)
            
            # Generate PDF
            pdf_gen = get_pdf_generator()
            pdf_path = pdf_gen.generate(invoice)
            
            flash(f'Invoice {invoice.invoice_id} created successfully!', 'success')
            return redirect(url_for('view_invoice', invoice_id=invoice.invoice_id))
            
        except Exception as e:
            flash(f'Error creating invoice: {str(e)}', 'error')
            return redirect(url_for('create_invoice'))
    
    return render_template('create_invoice.html')


@app.route('/invoices')
def list_invoices():
    """List all invoices."""
    invoices = get_all_invoices()
    return render_template('list_invoices.html', invoices=invoices)


@app.route('/invoice/<invoice_id>')
def view_invoice(invoice_id):
    """View invoice details."""
    invoices = get_all_invoices()
    invoice = None
    for inv in invoices:
        if inv.invoice_id == invoice_id:
            invoice = inv
            break
    
    if not invoice:
        flash('Invoice not found', 'error')
        return redirect(url_for('list_invoices'))
    
    return render_template('view_invoice.html', invoice=invoice)


@app.route('/pdf/<invoice_id>')
def download_pdf(invoice_id):
    """Download invoice PDF."""
    invoices = get_all_invoices()
    invoice = None
    for inv in invoices:
        if inv.invoice_id == invoice_id:
            invoice = inv
            break
    
    if not invoice:
        flash('Invoice not found', 'error')
        return redirect(url_for('list_invoices'))
    
    pdf_gen = get_pdf_generator()
    pdf_path = pdf_gen.generate(invoice)
    
    if os.path.exists(pdf_path):
        return send_file(pdf_path, as_attachment=True, download_name=f"{invoice.invoice_id}.pdf")
    
    flash('PDF not found', 'error')
    return redirect(url_for('view_invoice', invoice_id=invoice_id))


@app.route('/search')
def search_invoices():
    """Search invoices."""
    query = request.args.get('query', '').strip().lower()
    invoices = get_all_invoices()
    
    if query:
        invoices = [inv for inv in invoices if query in inv.invoice_id.lower() or query in inv.customer.name.lower()]
    
    return render_template('list_invoices.html', invoices=invoices)


@app.route('/statistics')
def statistics():
    """Statistics page."""
    stats = get_stats()
    monthly = get_monthly_stats()
    return render_template('statistics.html', stats=stats, monthly_stats=monthly)


@app.route('/sample')
def create_sample():
    """Create sample invoice."""
    try:
        manager = get_manager()
        pdf_gen = get_pdf_generator()
        
        invoice = manager.create_sample_invoice()
        manager.save_invoice(invoice)
        pdf_path = pdf_gen.generate(invoice)
        
        flash(f'Sample invoice {invoice.invoice_id} created!', 'success')
        return redirect(url_for('view_invoice', invoice_id=invoice.invoice_id))
        
    except Exception as e:
        flash(f'Error creating sample: {str(e)}', 'error')
        return redirect(url_for('index'))


def main():
    """Run the web application."""
    print("=" * 60)
    print("Starting Invoice Generator Web Application...")
    print("=" * 60)
    print("\nOpen your browser and go to: http://127.0.0.1:5000")
    print("\nPress Ctrl+C to stop the server.\n")
    
    app.run(host='127.0.0.1', port=5000, debug=True)


if __name__ == "__main__":
    main()