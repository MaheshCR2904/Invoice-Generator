"""
Invoice Generator System - Invoice Manager
=============================================
This module handles invoice storage, retrieval, and management of multiple invoices.

Author: Invoice Generator System
Date: 2026-03-28
"""

import os
import json
import csv
from datetime import datetime
from typing import List, Optional, Dict
from pathlib import Path

from invoice_models import Invoice, Customer, Product, CompanyDetails, StorageError


class InvoiceManager:
    """
    Manages multiple invoices, including storage and retrieval.
    
    Attributes:
        data_dir: Directory to store invoice data
    """
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize Invoice Manager.
        
        Args:
            data_dir: Directory to store invoice data
        """
        self.data_dir = data_dir
        self._create_data_directory()
    
    def _create_data_directory(self):
        """Create data directory if it doesn't exist."""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def save_invoice(self, invoice: Invoice) -> str:
        """
        Save invoice to JSON file.
        
        Args:
            invoice: Invoice object to save
            
        Returns:
            Path to saved invoice file
            
        Raises:
            StorageError: If saving fails
        """
        try:
            filename = f"{invoice.invoice_id}.json"
            filepath = os.path.join(self.data_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(invoice.to_dict(), f, indent=2, ensure_ascii=False)
            
            return filepath
            
        except Exception as e:
            raise StorageError(f"Failed to save invoice: {str(e)}")
    
    def load_invoice(self, invoice_id: str) -> Optional[Invoice]:
        """
        Load invoice from JSON file.
        
        Args:
            invoice_id: Invoice ID to load
            
        Returns:
            Invoice object if found, None otherwise
            
        Raises:
            StorageError: If loading fails
        """
        try:
            filename = f"{invoice_id}.json"
            filepath = os.path.join(self.data_dir, filename)
            
            if not os.path.exists(filepath):
                return None
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return Invoice.from_dict(data)
            
        except Exception as e:
            raise StorageError(f"Failed to load invoice: {str(e)}")
    
    def delete_invoice(self, invoice_id: str) -> bool:
        """
        Delete invoice from storage.
        
        Args:
            invoice_id: Invoice ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        try:
            filename = f"{invoice_id}.json"
            filepath = os.path.join(self.data_dir, filename)
            
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            
            return False
            
        except Exception as e:
            raise StorageError(f"Failed to delete invoice: {str(e)}")
    
    def list_invoices(self) -> List[str]:
        """
        List all invoice IDs.
        
        Returns:
            List of invoice IDs
        """
        try:
            invoice_ids = []
            
            for filename in os.listdir(self.data_dir):
                if filename.endswith('.json'):
                    invoice_id = filename[:-5]  # Remove .json
                    invoice_ids.append(invoice_id)
            
            return sorted(invoice_ids)
            
        except Exception as e:
            raise StorageError(f"Failed to list invoices: {str(e)}")
    
    def get_all_invoices(self) -> List[Invoice]:
        """
        Get all invoices.
        
        Returns:
            List of Invoice objects
        """
        invoices = []
        
        for invoice_id in self.list_invoices():
            invoice = self.load_invoice(invoice_id)
            if invoice:
                invoices.append(invoice)
        
        return invoices
    
    def search_invoices(self, query: str) -> List[Invoice]:
        """
        Search invoices by customer name or invoice ID.
        
        Args:
            query: Search query
            
        Returns:
            List of matching Invoice objects
        """
        query = query.lower()
        results = []
        
        for invoice in self.get_all_invoices():
            # Check invoice ID
            if query in invoice.invoice_id.lower():
                results.append(invoice)
            # Check customer name
            elif invoice.customer and query in invoice.customer.name.lower():
                results.append(invoice)
        
        return results
    
    def export_to_csv(self, export_path: Optional[str] = None) -> str:
        """
        Export all invoices to CSV file.
        
        Args:
            export_path: Path for export file (optional)
            
        Returns:
            Path to exported CSV file
        """
        try:
            if export_path is None:
                export_path = os.path.join(
                    self.data_dir,
                    f"invoices_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                )
            
            invoices = self.get_all_invoices()
            
            with open(export_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Header
                writer.writerow([
                    'Invoice ID', 'Date', 'Customer Name', 'Customer Email',
                    'Customer Phone', 'Products', 'Subtotal', 'Tax Rate',
                    'Tax Amount', 'Discount', 'Total'
                ])
                
                # Data rows
                for inv in invoices:
                    product_names = ', '.join(p.name for p in inv.products)
                    writer.writerow([
                        inv.invoice_id,
                        inv.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                        inv.customer.name if inv.customer else '',
                        inv.customer.email if inv.customer else '',
                        inv.customer.phone if inv.customer else '',
                        product_names,
                        inv.subtotal,
                        inv.tax_rate,
                        inv.tax_amount,
                        inv.discount,
                        inv.total
                    ])
            
            return export_path
            
        except Exception as e:
            raise StorageError(f"Failed to export to CSV: {str(e)}")
    
    def export_to_json(self, export_path: Optional[str] = None) -> str:
        """
        Export all invoices to JSON file.
        
        Args:
            export_path: Path for export file (optional)
            
        Returns:
            Path to exported JSON file
        """
        try:
            if export_path is None:
                export_path = os.path.join(
                    self.data_dir,
                    f"invoices_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                )
            
            invoices = self.get_all_invoices()
            data = [inv.to_dict() for inv in invoices]
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            return export_path
            
        except Exception as e:
            raise StorageError(f"Failed to export to JSON: {str(e)}")
    
    def get_statistics(self) -> Dict:
        """
        Get invoice statistics.
        
        Returns:
            Dictionary containing statistics
        """
        invoices = self.get_all_invoices()
        
        total_invoices = len(invoices)
        total_revenue = sum(inv.total for inv in invoices)
        total_tax = sum(inv.tax_amount for inv in invoices)
        
        # Monthly statistics
        monthly_data = {}
        for inv in invoices:
            month_key = inv.created_at.strftime('%Y-%m')
            if month_key not in monthly_data:
                monthly_data[month_key] = {'count': 0, 'revenue': 0}
            monthly_data[month_key]['count'] += 1
            monthly_data[month_key]['revenue'] += inv.total
        
        return {
            'total_invoices': total_invoices,
            'total_revenue': total_revenue,
            'total_tax': total_tax,
            'monthly_data': monthly_data
        }
    
    def create_sample_invoice(self) -> Invoice:
        """
        Create a sample invoice for demonstration.
        
        Returns:
            Sample Invoice object
        """
        # Sample company
        company = CompanyDetails(
            name="Tech Solutions Pvt Ltd",
            address="123 Tech Park, Bangalore - 560001",
            phone="+91 9876543210",
            email="info@techsolutions.com",
            gst_number="29AABCT1234N1Z5"
        )
        
        # Sample customer
        customer = Customer(
            name="John Doe",
            phone="+91 9876543210",
            email="john.doe@example.com",
            address="456 Business Ave, Mumbai - 400001",
            gst_number="27AABJD1234N1Z4"
        )
        
        # Create products list first
        products = [
            Product("Laptop", 2, 45000),
            Product("Mouse", 5, 500),
            Product("Keyboard", 3, 1500)
        ]
        
        # Create invoice
        invoice = Invoice(
            customer=customer,
            company=company,
            tax_rate=18.0,
            discount=0,
            discount_type="fixed",
            products=products
        )
        
        # Add signature
        invoice.signature = "Authorized Signatory"
        
        return invoice


# Simple invoice storage for CLI
class InvoiceStorage:
    """
    Simple JSON-based storage for invoices.
    """
    
    def __init__(self, storage_file: str = "data/invoices.json"):
        """
        Initialize storage.
        
        Args:
            storage_file: Path to storage file
        """
        self.storage_file = storage_file
        self._ensure_storage_file()
    
    def _ensure_storage_file(self):
        """Ensure storage file exists."""
        storage_dir = os.path.dirname(self.storage_file)
        if not os.path.exists(storage_dir):
            os.makedirs(storage_dir)
        
        if not os.path.exists(self.storage_file):
            self._save_data({})
    
    def _load_data(self) -> dict:
        """Load data from file."""
        try:
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def _save_data(self, data: dict):
        """Save data to file."""
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def save(self, invoice: Invoice):
        """Save invoice to storage."""
        data = self._load_data()
        data[invoice.invoice_id] = invoice.to_dict()
        self._save_data(data)
    
    def load(self, invoice_id: str) -> Optional[Invoice]:
        """Load invoice from storage."""
        data = self._load_data()
        if invoice_id in data:
            return Invoice.from_dict(data[invoice_id])
        return None
    
    def delete(self, invoice_id: str) -> bool:
        """Delete invoice from storage."""
        data = self._load_data()
        if invoice_id in data:
            del data[invoice_id]
            self._save_data(data)
            return True
        return False
    
    def get_all(self) -> List[Invoice]:
        """Get all invoices."""
        data = self._load_data()
        return [Invoice.from_dict(v) for v in data.values()]
    
    def get_ids(self) -> List[str]:
        """Get all invoice IDs."""
        data = self._load_data()
        return list(data.keys())