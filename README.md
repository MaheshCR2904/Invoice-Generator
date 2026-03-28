# Invoice Generator System
### Professional PDF Invoice Generator in Python

A complete Invoice Generator System built in Python with support for generating professional PDF invoices, managing multiple invoices, and exporting data.

## Features

### Core Features
- ✅ **Customer Details**: Name, Phone, Email, Address, GST Number
- ✅ **Product Management**: Add multiple products with quantity and price
- ✅ **Automatic Calculations**: Subtotal, Tax (configurable %), Discount, Total
- ✅ **Unique Invoice ID**: Auto-generated unique invoice IDs
- ✅ **Date & Time**: Current timestamp on each invoice
- ✅ **Company Details**: Name, Logo, Address, Phone, Email, GST

### PDF Generation
- ✅ **Professional Layout**: Clean, modern PDF design
- ✅ **Header**: Company name and details
- ✅ **Customer Section**: Bill-to information
- ✅ **Product Table**: Detailed product listing
- ✅ **Pricing Summary**: Subtotal, Tax, Discount, Total
- ✅ **Auto-save**: PDFs saved automatically

### Additional Features
- ✅ **Preview**: Open PDF before downloading
- ✅ **Data Storage**: JSON format for invoice data
- ✅ **Multiple Invoices**: Handle unlimited invoices
- ✅ **Error Handling**: Validation for all inputs
- ✅ **Search**: Search invoices by customer or ID
- ✅ **Export**: Export to CSV or JSON
- ✅ **Statistics**: View invoice statistics

### Bonus Features
- ✅ **Discount**: Percentage or fixed discount
- ✅ **Digital Signature**: Signature field
- ✅ **GST Support**: GST number fields for company and customer

## Installation

### 1. Install Dependencies

```bash
pip install reportlab
```

### 2. Run the Application

#### GUI Mode (Default)
```bash
python main.py
```
Or:
```bash
python main.py --gui
```

#### CLI Mode
```bash
python main.py --cli
```

#### Create Sample Invoice
```bash
python main.py --sample
```

## Usage

### GUI Interface
1. Run `python main.py` to open the GUI
2. Fill in Company Details
3. Fill in Customer Details
4. Add Products (click "Add Product" for multiple)
5. Set Tax Rate and Discount (optional)
6. Click "Generate Invoice"
7. Preview the PDF or find it in the `invoices/` folder

### CLI Interface
1. Run `python main.py --cli`
2. Follow the menu-driven interface
3. Choose options from the main menu

## File Structure

```
invoice_generator/
├── main.py                 # Main entry point
├── invoice_models.py      # Data models (Invoice, Customer, Product)
├── pdf_generator.py       # PDF generation with reportlab
├── invoice_manager.py    # Invoice storage and management
├── cli_interface.py    # Command-line interface
├── gui_interface.py    # Tkinter GUI interface
├── requirements.txt    # Dependencies
├── README.md          # This file
├── data/              # Invoice data storage (JSON)
└── invoices/          # Generated PDFs
```

## Dependencies

- **reportlab** - For PDF generation
- Python 3.7+ (standard library modules: datetime, tkinter, json, csv, os, sys, uuid, typing, pathlib)

## Example Usage

### Creating an Invoice Programmatically

```python
from invoice_models import Invoice, Customer, Product, CompanyDetails
from invoice_manager import InvoiceManager
from pdf_generator import PDFGenerator

# Create company details
company = CompanyDetails(
    name="Your Company Name",
    address="123 Business Street, City - PIN",
    phone="+91 9876543210",
    email="contact@company.com",
    gst_number="XX9999XX999999"
)

# Create customer
customer = Customer(
    name="Customer Name",
    phone="+91 9876543210",
    email="customer@example.com"
)

# Create invoice
invoice = Invoice(
    customer=customer,
    company=company,
    tax_rate=18.0,
    discount=0,
    discount_type="fixed"
)

# Add products
invoice.add_product(Product("Product 1", 2, 10000))
invoice.add_product(Product("Product 2", 1, 5000))

# Save invoice
manager = InvoiceManager()
manager.save_invoice(invoice)

# Generate PDF
pdf_gen = PDFGenerator()
pdf_path = pdf_gen.generate(invoice)
print(f"PDF generated: {pdf_path}")
```

## Output

The system generates professional PDF invoices with:
- Company header with contact details
- Invoice ID and date
- Customer billing information
- Product table with quantities and prices
- Pricing summary with subtotal, tax, and total
- Terms and conditions
- Digital signature area

## License

This project is open source and available for free use.

## Author

Invoice Generator System
Date: 2026-03-28