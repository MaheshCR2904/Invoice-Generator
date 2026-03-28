"""
Invoice Generator System - CLI Interface
=========================================
Command-line interface for the Invoice Generator System.

Author: Invoice Generator System
Date: 2026-03-28
"""

import os
import sys
from datetime import datetime
from typing import List, Optional

from invoice_models import (
    Invoice, Customer, Product, CompanyDetails, 
    InvoiceError, ValidationError
)
from invoice_manager import InvoiceManager
from pdf_generator import PDFGenerator


class CLIInterface:
    """
    Command-line interface for Invoice Generator.
    """
    
    def __init__(self):
        """Initialize CLI interface."""
        self.manager = InvoiceManager()
        self.pdf_generator = PDFGenerator()
        self.invoice: Optional[Invoice] = None
    
    def clear_screen(self):
        """Clear the screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """Print application header."""
        print("=" * 60)
        print("      INVOICE GENERATOR SYSTEM")
        print("      Professional PDF Invoice Generator")
        print("=" * 60)
        print()
    
    def print_menu(self):
        """Print main menu."""
        print("\n--- MAIN MENU ---")
        print("1. Create New Invoice")
        print("2. View Invoice")
        print("3. List All Invoices")
        print("4. Search Invoice")
        print("5. Export Data")
        print("6. Statistics")
        print("7. Create Sample Invoice")
        print("0. Exit")
        print("-" * 20)
    
    def get_input(self, prompt: str, required: bool = True) -> str:
        """
        Get input from user with validation.
        
        Args:
            prompt: Input prompt
            required: Whether input is required
            
        Returns:
            User input
        """
        while True:
            value = input(prompt).strip()
            
            if required and not value:
                print("Error: This field is required. Please try again.")
                continue
            
            return value
    
    def get_email(self, prompt: str = "Email: ") -> str:
        """Get email with validation."""
        while True:
            email = input(prompt).strip()
            
            if not email:
                print("Error: Email is required.")
                continue
            
            if '@' not in email or '.' not in email:
                print("Error: Invalid email format. Please enter a valid email.")
                continue
            
            return email
    
    def get_number(self, prompt: str, positive: bool = True) -> float:
        """Get numeric input with validation."""
        while True:
            try:
                value = float(input(prompt).strip())
                
                if positive and value <= 0:
                    print("Error: Value must be positive.")
                    continue
                
                return value
                
            except ValueError:
                print("Error: Please enter a valid number.")
    
    def get_integer(self, prompt: str, min_value: int = 1) -> int:
        """Get integer input with validation."""
        while True:
            try:
                value = int(input(prompt).strip())
                
                if value < min_value:
                    print(f"Error: Value must be at least {min_value}.")
                    continue
                
                return value
                
            except ValueError:
                print("Error: Please enter a valid integer.")
    
    def get_yes_no(self, prompt: str = "Continue? (y/n): ") -> bool:
        """Get yes/no confirmation."""
        while True:
            response = input(prompt).strip().lower()
            
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("Please enter 'y' or 'n'.")
    
    def get_company_details(self) -> CompanyDetails:
        """Get company details from user."""
        print("\n--- Company Details ---")
        
        name = self.get_input("Company Name: ")
        address = self.get_input("Address: ")
        phone = self.get_input("Phone: ")
        email = self.get_email("Email: ")
        gst = self.get_input("GST Number (optional): ", required=False)
        
        return CompanyDetails(
            name=name,
            address=address,
            phone=phone,
            email=email,
            gst_number=gst
        )
    
    def get_customer_details(self) -> Customer:
        """Get customer details from user."""
        print("\n--- Customer Details ---")
        
        name = self.get_input("Customer Name: ")
        phone = self.get_input("Phone: ")
        email = self.get_email("Email: ")
        address = self.get_input("Address (optional): ", required=False)
        gst = self.get_input("GST Number (optional): ", required=False)
        
        return Customer(
            name=name,
            phone=phone,
            email=email,
            address=address,
            gst_number=gst
        )
    
    def get_products(self) -> List[Product]:
        """Get products from user."""
        products = []
        
        print("\n--- Products ---")
        print("Enter product details (press Enter twice to finish)")
        
        while True:
            print(f"\nProduct {len(products) + 1}:")
            
            name = self.get_input("  Product Name: ")
            if not name:
                break
            
            quantity = self.get_integer("  Quantity: ")
            price = self.get_number("  Price per unit (₹): ")
            
            products.append(Product(name=name, quantity=quantity, price_per_unit=price))
            
            print(f"  Added: {name} x {quantity} = ₹{products[-1].total:,.2f}")
        
        return products
    
    def get_tax_rate(self) -> float:
        """Get tax rate from user."""
        print("\n--- Pricing ---")
        
        while True:
            try:
                rate = float(input("Tax Rate (%): ").strip())
                
                if rate < 0:
                    print("Error: Tax rate cannot be negative.")
                    continue
                
                return rate
                
            except ValueError:
                print("Error: Please enter a valid number.")
    
    def get_discount(self) -> tuple:
        """Get discount details."""
        print("Discount (optional - press Enter to skip):")
        
        has_discount = input("  Apply discount? (y/n): ").strip().lower() == 'y'
        
        if not has_discount:
            return (0, "fixed")
        
        discount_type = input("  Type (percentage/fixed): ").strip().lower()
        if discount_type not in ['percentage', 'fixed']:
            discount_type = 'fixed'
        
        discount_value = self.get_number("  Value: ")
        
        return (discount_value, discount_type)
    
    def get_signature(self) -> str:
        """Get digital signature."""
        print("\n--- Digital Signature ---")
        return input("Signature (optional): ").strip()
    
    def create_invoice(self):
        """Create a new invoice."""
        print("\n" + "=" * 60)
        print("CREATE NEW INVOICE")
        print("=" * 60)
        
        # Get company details
        company = self.get_company_details()
        
        # Get customer details
        customer = self.get_customer_details()
        
        # Get products
        print("\nAdd at least one product:")
        products = self.get_products()
        
        if not products:
            print("Error: At least one product is required.")
            return
        
        # Get pricing details
        tax_rate = self.get_tax_rate()
        discount, discount_type = self.get_discount()
        signature = self.get_signature()
        
        # Create invoice
        try:
            invoice = Invoice(
                customer=customer,
                company=company,
                tax_rate=tax_rate,
                discount=discount,
                discount_type=discount_type,
                signature=signature
            )
            
            for product in products:
                invoice.add_product(product)
            
            # Display summary
            print("\n" + "-" * 40)
            print("INVOICE SUMMARY")
            print("-" * 40)
            print(f"Invoice ID: {invoice.invoice_id}")
            print(f"Date: {invoice.get_formatted_date()}")
            print(f"Customer: {invoice.customer.name}")
            print(f"Products: {len(invoice.products)}")
            print(f"Subtotal: ₹{invoice.subtotal:,.2f}")
            print(f"Tax ({invoice.tax_rate}%): ₹{invoice.tax_amount:,.2f}")
            print(f"Total: ₹{invoice.total:,.2f}")
            print("-" * 40)
            
            # Save invoice
            self.manager.save_invoice(invoice)
            print(f"\nInvoice saved: {invoice.invoice_id}")
            
            # Generate PDF
            pdf_path = self.pdf_generator.generate(invoice)
            print(f"PDF generated: {pdf_path}")
            
            # Ask to preview
            if self.get_y_n("\nPreview invoice? (y/n): "):
                self.pdf_generator.preview_invoice(invoice)
            
            self.invoice = invoice
            
        except (ValidationError, InvoiceError) as e:
            print(f"Error: {e}")
    
    def view_invoice(self):
        """View an invoice."""
        invoice_id = input("Enter Invoice ID: ").strip()
        
        invoice = self.manager.load_invoice(invoice_id)
        
        if not invoice:
            print(f"Invoice not found: {invoice_id}")
            return
        
        print("\n" + "=" * 60)
        print(f"INVOICE: {invoice.invoice_id}")
        print("=" * 60)
        print(f"Date: {invoice.get_formatted_date()}")
        print(f"Customer: {invoice.customer.name}")
        print(f"Email: {invoice.customer.email}")
        print(f"Phone: {invoice.customer.phone}")
        print()
        
        print("Products:")
        for idx, product in enumerate(invoice.products, 1):
            print(f"  {idx}. {product.name} x {product.quantity} = ₹{product.total:,.2f}")
        
        print()
        print(f"Subtotal: ₹{invoice.subtotal:,.2f}")
        print(f"Tax ({invoice.tax_rate}%): ₹{invoice.tax_amount:,.2f}")
        print(f"Total: ₹{invoice.total:,.2f}")
        print("=" * 60)
        
        # Options
        print("\n1. Preview PDF")
        print("2. Generate New PDF")
        print("0. Back")
        
        choice = input("Choice: ").strip()
        
        if choice == '1':
            self.pdf_generator.preview_invoice(invoice)
        elif choice == '2':
            pdf_path = self.pdf_generator.generate(invoice)
            print(f"PDF generated: {pdf_path}")
    
    def list_invoices(self):
        """List all invoices."""
        invoices = self.manager.get_all_invoices()
        
        if not invoices:
            print("No invoices found.")
            return
        
        print(f"\nTotal Invoices: {len(invoices)}")
        print("-" * 60)
        
        for invoice in sorted(invoices, key=lambda x: x.created_at, reverse=True):
            print(f"{invoice.invoice_id} | {invoice.get_formatted_date()} | "
                  f"{invoice.customer.name} | ₹{invoice.total:,.2f}")
        
        print("-" * 60)
    
    def search_invoices(self):
        """Search invoices."""
        query = input("Search (Customer Name or Invoice ID): ").strip()
        
        results = self.manager.search_invoices(query)
        
        if not results:
            print("No invoices found.")
            return
        
        print(f"\nFound {len(results)} invoice(s):")
        print("-" * 60)
        
        for invoice in results:
            print(f"{invoice.invoice_id} | {invoice.get_formatted_date()} | "
                  f"{invoice.customer.name} | ₹{invoice.total:,.2f}")
        
        print("-" * 60)
    
    def export_data(self):
        """Export invoice data."""
        print("\nExport Options:")
        print("1. Export to CSV")
        print("2. Export to JSON")
        print("0. Back")
        
        choice = input("Choice: ").strip()
        
        try:
            if choice == '1':
                path = self.manager.export_to_csv()
                print(f"Exported to: {path}")
            elif choice == '2':
                path = self.manager.export_to_json()
                print(f"Exported to: {path}")
        except Exception as e:
            print(f"Error: {e}")
    
    def show_statistics(self):
        """Show invoice statistics."""
        stats = self.manager.get_statistics()
        
        print("\n" + "=" * 60)
        print("STATISTICS")
        print("=" * 60)
        print(f"Total Invoices: {stats['total_invoices']}")
        print(f"Total Revenue: ₹{stats['total_revenue']:,.2f}")
        print(f"Total Tax: ₹{stats['total_tax']:,.2f}")
        print("=" * 60)
    
    def create_sample_invoice(self):
        """Create a sample invoice."""
        print("\nCreating sample invoice...")
        
        # Create sample invoice
        invoice = self.manager.create_sample_invoice()
        
        # Save and generate PDF
        self.manager.save_invoice(invoice)
        pdf_path = self.pdf_generator.generate(invoice)
        
        print(f"Sample invoice created: {invoice.invoice_id}")
        print(f"PDF generated: {pdf_path}")
        
        # Preview
        if self.get_y_n("\nPreview sample invoice? (y/n): "):
            self.pdf_generator.preview_invoice(invoice)
    
    def get_y_n(self, prompt: str) -> bool:
        """Get yes/no input."""
        while True:
            response = input(prompt).strip().lower()
            
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            else:
                print("Please enter 'y' or 'n'.")
    
    def run(self):
        """Run the CLI interface."""
        self.clear_screen()
        self.print_header()
        
        while True:
            self.print_menu()
            choice = input("Enter choice: ").strip()
            
            if choice == '0':
                print("\nThank you for using Invoice Generator!")
                break
            elif choice == '1':
                self.create_invoice()
            elif choice == '2':
                self.view_invoice()
            elif choice == '3':
                self.list_invoices()
            elif choice == '4':
                self.search_invoices()
            elif choice == '5':
                self.export_data()
            elif choice == '6':
                self.show_statistics()
            elif choice == '7':
                self.create_sample_invoice()
            else:
                print("Invalid choice. Please try again.")


def main():
    """Main entry point for CLI."""
    cli = CLIInterface()
    cli.run()


if __name__ == "__main__":
    main()