"""
Invoice Generator System - GUI Interface
=======================================
Graphical User Interface (Tkinter) for Invoice Generator System.

Author: Invoice Generator System
Date: 2026-03-28
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, List

from invoice_models import (
    Invoice, Customer, Product, CompanyDetails,
    ValidationError, InvoiceError
)
from invoice_manager import InvoiceManager
from pdf_generator import PDFGenerator


class InvoiceApp:
    """
    Tkinter GUI application for Invoice Generator.
    """
    
    # Color scheme
    PRIMARY_COLOR = "#1a237e"
    SECONDARY_COLOR = "#f5f5f5"
    ACCENT_COLOR = "#3949ab"
    TEXT_COLOR = "#212121"
    
    def __init__(self, root: tk.Tk):
        """
        Initialize GUI application.
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("Invoice Generator System")
        self.root.geometry("900x700")
        self.root.configure(bg=self.SECONDARY_COLOR)
        
        self.manager = InvoiceManager()
        self.pdf_generator = PDFGenerator()
        
        self._setup_styles()
        self._create_widgets()
        self._bind_events()
    
    def _setup_styles(self):
        """Setup custom styles."""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure styles
        self.style.configure('Title.TLabel', 
                         font=('Helvetica', 18, 'bold'),
                         foreground=self.PRIMARY_COLOR,
                         background=self.SECONDARY_COLOR)
        
        self.style.configure('Header.TLabel',
                         font=('Helvetica', 12, 'bold'),
                         foreground=self.ACCENT_COLOR,
                         background=self.SECONDARY_COLOR)
        
        self.style.configure('Normal.TLabel',
                         font=('Helvetica', 10),
                         foreground=self.TEXT_COLOR,
                         background=self.SECONDARY_COLOR)
        
        self.style.configure('Primary.TButton',
                         font=('Helvetica', 10, 'bold'),
                         background=self.PRIMARY_COLOR,
                         foreground='white')
        
        self.style.configure('Accent.TButton',
                         font=('Helvetica', 10),
                         background=self.ACCENT_COLOR,
                         foreground='white')
        
        self.style.configure('TFrame',
                         background=self.SECONDARY_COLOR)
    
    def _create_widgets(self):
        """Create main widgets."""
        # Main container
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="INVOICE GENERATOR",
            style='Title.TLabel'
        )
        title_label.pack(pady=10)
        
        # Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create tabs
        self._create_create_tab()
        self._create_list_tab()
        self._create_export_tab()
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            style='Normal.TLabel'
        )
        status_bar.pack(pady=5)
    
    def _create_create_tab(self):
        """Create invoice creation tab."""
        create_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(create_frame, text="Create Invoice")
        
        # Scrollable canvas
        canvas = tk.Canvas(create_frame)
        scrollbar = ttk.Scrollbar(create_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, padding=10)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Company Section
        self._add_section_header(scrollable_frame, "Company Details")
        
        self.company_name = self._add_entry(scrollable_frame, "Company Name:")
        self.company_address = self._add_entry(scrollable_frame, "Address:")
        self.company_phone = self._add_entry(scrollable_frame, "Phone:")
        self.company_email = self._add_entry(scrollable_frame, "Email:")
        self.company_gst = self._add_entry(scrollable_frame, "GST Number (optional):")
        
        # Customer Section
        self._add_section_header(scrollable_frame, "Customer Details")
        
        self.customer_name = self._add_entry(scrollable_frame, "Customer Name:")
        self.customer_phone = self._add_entry(scrollable_frame, "Phone:")
        self.customer_email = self._add_entry(scrollable_frame, "Email:")
        self.customer_address = self._add_entry(scrollable_frame, "Address (optional):")
        self.customer_gst = self._add_entry(scrollable_frame, "GST Number (optional):")
        
        # Products Section
        self._add_section_header(scrollable_frame, "Products")
        
        self.product_frame = ttk.Frame(scrollable_frame)
        self.product_frame.pack(fill=tk.X, pady=5)
        
        self.products: List[tuple] = []  # (name_entry, qty_entry, price_entry)
        self._add_product_row()
        
        add_product_btn = ttk.Button(
            self.product_frame,
            text="+ Add Product",
            command=self._add_product_row
        )
        add_product_btn.grid(row=0, column=3, padx=5)
        
        # Tax and Discount
        self._add_section_header(scrollable_frame, "Pricing")
        
        self.tax_rate = self._add_entry(scrollable_frame, "Tax Rate (%):", default="18")
        self.discount = self._add_entry(scrollable_frame, "Discount (₹):", default="0")
        self.signature = self._add_entry(scrollable_frame, "Signature (optional):")
        
        # Buttons
        button_frame = ttk.Frame(scrollable_frame)
        button_frame.pack(pady=20)
        
        generate_btn = ttk.Button(
            button_frame,
            text="Generate Invoice",
            style='Primary.TButton',
            command=self._generate_invoice
        )
        generate_btn.pack(side=tk.LEFT, padx=5)
        
        preview_btn = ttk.Button(
            button_frame,
            text="Preview",
            command=self._preview_invoice
        )
        preview_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = ttk.Button(
            button_frame,
            text="Clear",
            command=self._clear_form
        )
        clear_btn.pack(side=tk.LEFT, padx=5)
    
    def _create_list_tab(self):
        """Create invoice list tab."""
        list_frame = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(list_frame, text="View Invoices")
        
        # Search
        search_frame = ttk.Frame(list_frame)
        search_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        search_btn = ttk.Button(search_frame, text="Search", command=self._search_invoices)
        search_btn.pack(side=tk.LEFT, padx=5)
        
        refresh_btn = ttk.Button(search_frame, text="Refresh", command=self._refresh_list)
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Treeview
        columns = ('ID', 'Date', 'Customer', 'Total')
        self.invoice_tree = ttk.Treeview(list_frame, columns=columns, show='headings')
        
        for col in columns:
            self.invoice_tree.heading(col, text=col)
            self.invoice_tree.column(col, width=150)
        
        self.invoice_tree.column('Total', width=100)
        
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", 
                              command=self.invoice_tree.yview)
        self.invoice_tree.configure(yscrollcommand=scrollbar.set)
        
        self.invoice_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Action buttons
        action_frame = ttk.Frame(list_frame)
        action_frame.pack(pady=5)
        
        view_btn = ttk.Button(action_frame, text="View Selected", 
                            command=self._view_selected)
        view_btn.pack(side=tk.LEFT, padx=5)
        
        delete_btn = ttk.Button(action_frame, text="Delete Selected",
                               command=self._delete_invoice)
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        # Load initial data
        self._refresh_list()
    
    def _create_export_tab(self):
        """Create export tab."""
        export_frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(export_frame, text="Export")
        
        # Statistics
        self._add_section_header(export_frame, "Statistics")
        
        stats_frame = ttk.Frame(export_frame)
        stats_frame.pack(fill=tk.X, pady=10)
        
        self.stats_label = ttk.Label(stats_frame, text="No data")
        self.stats_label.pack()
        
        refresh_stats_btn = ttk.Button(
            stats_frame,
            text="Refresh Statistics",
            command=self._refresh_stats
        )
        refresh_stats_btn.pack(pady=5)
        
        # Export options
        self._add_section_header(export_frame, "Export Options")
        
        export_button_frame = ttk.Frame(export_frame)
        export_button_frame.pack(pady=10)
        
        csv_btn = ttk.Button(
            export_button_frame,
            text="Export to CSV",
            command=self._export_csv
        )
        csv_btn.pack(side=tk.LEFT, padx=5)
        
        json_btn = ttk.Button(
            export_button_frame,
            text="Export to JSON",
            command=self._export_json
        )
        json_btn.pack(side=tk.LEFT, padx=5)
        
        # Sample invoice
        self._add_section_header(export_frame, "Sample Invoice")
        
        sample_btn = ttk.Button(
            export_frame,
            text="Create Sample Invoice",
            command=self._create_sample_invoice
        )
        sample_btn.pack(pady=10)
    
    def _add_section_header(self, parent, text: str):
        """Add section header."""
        header = ttk.Label(parent, text=text, style='Header.TLabel')
        header.pack(pady=(15, 5), anchor=tk.W)
    
    def _add_entry(self, parent, label: str, default: str = "") -> ttk.Entry:
        """Add labeled entry field."""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(frame, text=label, width=20, style='Normal.TLabel').pack(side=tk.LEFT)
        
        entry = ttk.Entry(frame, width=40)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        entry.insert(0, default)
        
        return entry
    
    def _add_product_row(self):
        """Add a product row."""
        row = len(self.products)
        
        frame = ttk.Frame(self.product_frame)
        frame.grid(row=row, column=0, columnspan=3, pady=2, sticky='ew')
        self.product_frame.columnconfigure(0, weight=1)
        
        name_entry = ttk.Entry(frame, width=25)
        name_entry.pack(side=tk.LEFT, padx=2)
        
        qty_entry = ttk.Entry(frame, width=10)
        qty_entry.pack(side=tk.LEFT, padx=2)
        
        price_entry = ttk.Entry(frame, width=15)
        price_entry.pack(side=tk.LEFT, padx=2)
        
        # Add remove button for rows beyond first
        if row > 0:
            remove_btn = ttk.Button(
                frame,
                text="-",
                width=3,
                command=lambda: self._remove_product_row(frame)
            )
            remove_btn.pack(side=tk.LEFT, padx=2)
        
        self.products.append((name_entry, qty_entry, price_entry))
    
    def _remove_product_row(self, frame):
        """Remove a product row."""
        frame.destroy()
        # Note: In production, you'd also remove from self.products list
    
    def _bind_events(self):
        """Bind events."""
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
    def _generate_invoice(self):
        """Generate invoice from form data."""
        try:
            # Validate and get company details
            company = CompanyDetails(
                name=self.company_name.get().strip(),
                address=self.company_address.get().strip(),
                phone=self.company_phone.get().strip(),
                email=self.company_email.get().strip(),
                gst_number=self.company_gst.get().strip()
            )
            
            # Get customer details
            customer = Customer(
                name=self.customer_name.get().strip(),
                phone=self.customer_phone.get().strip(),
                email=self.customer_email.get().strip(),
                address=self.customer_address.get().strip(),
                gst_number=self.customer_gst.get().strip()
            )
            
            # Get products
            products = []
            for name_entry, qty_entry, price_entry in self.products:
                name = name_entry.get().strip()
                qty = qty_entry.get().strip()
                price = price_entry.get().strip()
                
                if name and qty and price:
                    products.append(Product(
                        name=name,
                        quantity=int(qty),
                        price_per_unit=float(price)
                    ))
            
            if not products:
                messagebox.showerror("Error", "Please add at least one product")
                return
            
            # Get pricing
            tax_rate = float(self.tax_rate.get().strip() or "18")
            discount = float(self.discount.get().strip() or "0")
            signature = self.signature.get().strip()
            
            # Create invoice
            invoice = Invoice(
                customer=customer,
                company=company,
                tax_rate=tax_rate,
                discount=discount,
                signature=signature
            )
            
            for product in products:
                invoice.add_product(product)
            
            # Save invoice
            self.manager.save_invoice(invoice)
            
            # Generate PDF
            pdf_path = self.pdf_generator.generate(invoice)
            
            messagebox.showinfo(
                "Success",
                f"Invoice generated!\n\nID: {invoice.invoice_id}\nTotal: ₹{invoice.total:,.2f}\n\nPDF: {pdf_path}"
            )
            
            # Refresh list
            self._refresh_list()
            self._refresh_stats()
            
            # Ask to preview
            if messagebox.askyesno("Preview", "Open PDF for preview?"):
                self.pdf_generator.preview_invoice(invoice)
            
        except ValidationError as e:
            messagebox.showerror("Validation Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate invoice: {str(e)}")
    
    def _preview_invoice(self):
        """Preview invoice (requires generating first)."""
        messagebox.showinfo("Preview", "Please generate an invoice first using 'Generate Invoice' button.")
    
    def _clear_form(self):
        """Clear the form."""
        for entry in [self.company_name, self.company_address, 
                     self.company_phone, self.company_email,
                     self.customer_name, self.customer_phone,
                     self.customer_email, self.customer_address]:
            entry.delete(0, tk.END)
        
        for name_entry, qty_entry, price_entry in self.products[1:]:
            name_entry.destroy()
            qty_entry.destroy()
            price_entry.destroy()
        
        self.products = []
        self._add_product_row()
    
    def _refresh_list(self):
        """Refresh invoice list."""
        # Clear tree
        for item in self.invoice_tree.get_children():
            self.invoice_tree.delete(item)
        
        # Add invoices
        invoices = self.manager.get_all_invoices()
        for invoice in sorted(invoices, key=lambda x: x.created_at, reverse=True):
            self.invoice_tree.insert('', tk.END, values=(
                invoice.invoice_id,
                invoice.get_formatted_date(),
                invoice.customer.name,
                f"₹{invoice.total:,.2f}"
            ))
        
        self._refresh_stats()
    
    def _search_invoices(self):
        """Search invoices."""
        query = self.search_var.get().strip()
        
        # Clear tree
        for item in self.invoice_tree.get_children():
            self.invoice_tree.delete(item)
        
        # Search
        if query:
            results = self.manager.search_invoices(query)
        else:
            results = self.manager.get_all_invoices()
        
        # Add results
        for invoice in results:
            self.invoice_tree.insert('', tk.END, values=(
                invoice.invoice_id,
                invoice.get_formatted_date(),
                invoice.customer.name,
                f"₹{invoice.total:,.2f}"
            ))
    
    def _view_selected(self):
        """View selected invoice."""
        selection = self.invoice_tree.selection()
        
        if not selection:
            messagebox.showwarning("Select", "Please select an invoice")
            return
        
        item = self.invoice_tree.item(selection[0])
        invoice_id = item['values'][0]
        
        invoice = self.manager.load_invoice(invoice_id)
        
        if not invoice:
            messagebox.showerror("Error", "Invoice not found")
            return
        
        # Show details
        details = f"""
Invoice: {invoice.invoice_id}
Date: {invoice.get_formatted_date()}

Customer: {invoice.customer.name}
Email: {invoice.customer.email}
Phone: {invoice.customer.phone}

Products:
"""
        for product in invoice.products:
            details += f"  - {product.name} x {product.quantity} = ₹{product.total:,.2f}\n"
        
        details += f"""
Subtotal: ₹{invoice.subtotal:,.2f}
Tax ({invoice.tax_rate}%): ₹{invoice.tax_amount:,.2f}
Total: ₹{invoice.total:,.2f}
"""
        
        if messagebox.askyesno("Invoice Details", details + "\n\nOpen PDF?"):
            self.pdf_generator.preview_invoice(invoice)
    
    def _delete_invoice(self):
        """Delete selected invoice."""
        selection = self.invoice_tree.selection()
        
        if not selection:
            messagebox.showwarning("Select", "Please select an invoice")
            return
        
        item = self.invoice_tree.item(selection[0])
        invoice_id = item['values'][0]
        
        if messagebox.askyesno("Delete", f"Delete invoice {invoice_id}?"):
            self.manager.delete_invoice(invoice_id)
            self._refresh_list()
            messagebox.showinfo("Success", "Invoice deleted")
    
    def _refresh_stats(self):
        """Refresh statistics."""
        stats = self.manager.get_statistics()
        
        self.stats_label.config(text=(
            f"Total Invoices: {stats['total_invoices']}\n"
            f"Total Revenue: ₹{stats['total_revenue']:,.2f}\n"
            f"Total Tax: ₹{stats['total_tax']:,.2f}"
        ))
    
    def _export_csv(self):
        """Export to CSV."""
        try:
            path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv")]
            )
            
            if path:
                self.manager.export_to_csv(path)
                messagebox.showinfo("Success", f"Exported to {path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _export_json(self):
        """Export to JSON."""
        try:
            path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json")]
            )
            
            if path:
                self.manager.export_to_json(path)
                messagebox.showinfo("Success", f"Exported to {path}")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _create_sample_invoice(self):
        """Create sample invoice."""
        try:
            invoice = self.manager.create_sample_invoice()
            self.manager.save_invoice(invoice)
            pdf_path = self.pdf_generator.generate(invoice)
            
            messagebox.showinfo(
                "Success",
                f"Sample invoice created!\n\nID: {invoice.invoice_id}\n\nPDF: {pdf_path}"
            )
            
            self._refresh_list()
            
            if messagebox.askyesno("Preview", "Open PDF?"):
                self.pdf_generator.preview_invoice(invoice)
                
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _on_close(self):
        """Handle window close."""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.root.destroy()


def main():
    """Main entry point for GUI."""
    root = tk.Tk()
    app = InvoiceApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()