"""
Invoice Generator System - Data Models
=====================================
This module contains all the data models and classes for the Invoice Generator System.

Author: Invoice Generator System
Date: 2026-03-28
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Optional
import uuid
import json


@dataclass
class Product:
    """
    Represents a product in an invoice.
    
    Attributes:
        name: Product name
        quantity: Number of units
        price_per_unit: Price per unit in rupees
    """
    name: str
    quantity: int
    price_per_unit: float
    
    def __post_init__(self):
        """Validate product data after initialization."""
        if not self.name or not self.name.strip():
            raise ValueError("Product name cannot be empty")
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")
        if self.price_per_unit < 0:
            raise ValueError("Price cannot be negative")
        
        # Clean the name
        self.name = self.name.strip()
    
    @property
    def total(self) -> float:
        """Calculate total for this product (quantity * price_per_unit)."""
        return self.quantity * self.price_per_unit
    
    def to_dict(self) -> dict:
        """Convert product to dictionary."""
        return {
            'name': self.name,
            'quantity': self.quantity,
            'price_per_unit': self.price_per_unit,
            'total': self.total
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Product':
        """Create product from dictionary."""
        return cls(
            name=data['name'],
            quantity=data['quantity'],
            price_per_unit=data['price_per_unit']
        )


@dataclass
class Customer:
    """
    Represents a customer who receives an invoice.
    
    Attributes:
        name: Customer name
        phone: Phone number
        email: Email address
        address: Customer address (optional)
        gst_number: GST number (optional)
    """
    name: str
    phone: str
    email: str
    address: str = ""
    gst_number: str = ""
    
    def __post_init__(self):
        """Validate customer data after initialization."""
        if not self.name or not self.name.strip():
            raise ValueError("Customer name cannot be empty")
        if not self.phone or not self.phone.strip():
            raise ValueError("Phone number cannot be empty")
        if not self.email or not self.email.strip():
            raise ValueError("Email cannot be empty")
        
        # Validate email format
        if '@' not in self.email or '.' not in self.email:
            raise ValueError("Invalid email format")
        
        # Clean the data
        self.name = self.name.strip()
        self.phone = self.phone.strip()
        self.email = self.email.strip()
        self.address = self.address.strip() if self.address else ""
        self.gst_number = self.gst_number.strip() if self.gst_number else ""
    
    def to_dict(self) -> dict:
        """Convert customer to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Customer':
        """Create customer from dictionary."""
        return cls(
            name=data['name'],
            phone=data['phone'],
            email=data['email'],
            address=data.get('address', ''),
            gst_number=data.get('gst_number', '')
        )


@dataclass
class CompanyDetails:
    """
    Represents company details for invoice header.
    
    Attributes:
        name: Company name
        address: Company address
        phone: Company phone
        email: Company email
        gst_number: Company GST number
    """
    name: str
    address: str
    phone: str
    email: str
    gst_number: str = ""
    
    def __post_init__(self):
        """Validate company data after initialization."""
        if not self.name or not self.name.strip():
            raise ValueError("Company name cannot be empty")
        
        # Clean the data
        self.name = self.name.strip()
        self.address = self.address.strip() if self.address else ""
        self.phone = self.phone.strip() if self.phone else ""
        self.email = self.email.strip() if self.email else ""
        self.gst_number = self.gst_number.strip() if self.gst_number else ""
    
    def to_dict(self) -> dict:
        """Convert company details to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'CompanyDetails':
        """Create company details from dictionary."""
        return cls(
            name=data['name'],
            address=data['address'],
            phone=data['phone'],
            email=data['email'],
            gst_number=data.get('gst_number', '')
        )


@dataclass
class Invoice:
    """
    Represents a complete invoice.
    
    Attributes:
        invoice_id: Unique invoice ID
        customer: Customer object
        products: List of Product objects
        company: CompanyDetails object
        tax_rate: Tax rate as percentage (default 18%)
        discount: Discount amount (optional)
        discount_type: Type of discount ('percentage' or 'fixed')
        created_at: Invoice creation timestamp
    """
    invoice_id: str = field(default_factory=lambda: f"INV-{uuid.uuid4().hex[:8].upper()}")
    customer: Optional[Customer] = None
    products: List[Product] = field(default_factory=list)
    company: Optional[CompanyDetails] = None
    tax_rate: float = 18.0
    discount: float = 0.0
    discount_type: str = "fixed"  # 'percentage' or 'fixed'
    created_at: datetime = field(default_factory=datetime.now)
    signature: str = ""  # Digital signature text
    _validated: bool = field(default=False, repr=False)
    
    def __post_init__(self):
        """Validate invoice data after initialization."""
        if self._validated:
            return
        # Only validate if we have enough data
        if self.customer is not None and self.company is not None:
            # If we have customer and company, check products
            if not self.products:
                # Don't raise yet, allow adding products later
                pass
            else:
                self._validated = True
                self._validate()
    
    def _validate(self):
        """Internal validation method."""
        if self.customer is None:
            raise ValueError("Customer is required")
        if not self.products:
            raise ValueError("At least one product is required")
        if self.company is None:
            raise ValueError("Company details are required")
        if self.tax_rate < 0:
            raise ValueError("Tax rate cannot be negative")
        if self.discount < 0:
            raise ValueError("Discount cannot be negative")
        if self.discount_type not in ['percentage', 'fixed']:
            raise ValueError("Discount type must be 'percentage' or 'fixed'")
    
    def validate(self):
        """Validate the invoice when ready."""
        self._validated = True
        self._validate()
    
    def add_product(self, product: Product):
        """Add a product to the invoice."""
        self.products.append(product)
    
    def remove_product(self, index: int):
        """Remove a product by index."""
        if 0 <= index < len(self.products):
            self.products.pop(index)
        else:
            raise IndexError("Invalid product index")
    
    @property
    def subtotal(self) -> float:
        """Calculate subtotal (sum of all product totals)."""
        if not self.products:
            return 0.0
        return sum(product.total for product in self.products)
    
    @property
    def discount_amount(self) -> float:
        """Calculate discount amount based on discount type."""
        if self.discount_type == 'percentage':
            return (self.subtotal * self.discount) / 100
        return self.discount
    
    @property
    def taxable_amount(self) -> float:
        """Calculate taxable amount after discount."""
        return self.subtotal - self.discount_amount
    
    @property
    def tax_amount(self) -> float:
        """Calculate tax amount."""
        return (self.taxable_amount * self.tax_rate) / 100
    
    @property
    def total(self) -> float:
        """Calculate total amount (taxable amount + tax)."""
        return self.taxable_amount + self.tax_amount
    
    def to_dict(self) -> dict:
        """Convert invoice to dictionary."""
        return {
            'invoice_id': self.invoice_id,
            'customer': self.customer.to_dict() if self.customer else None,
            'products': [p.to_dict() for p in self.products],
            'company': self.company.to_dict() if self.company else None,
            'tax_rate': self.tax_rate,
            'discount': self.discount,
            'discount_type': self.discount_type,
            'subtotal': self.subtotal,
            'discount_amount': self.discount_amount,
            'taxable_amount': self.taxable_amount,
            'tax_amount': self.tax_amount,
            'total': self.total,
            'created_at': self.created_at.isoformat(),
            'signature': self.signature
        }
    
    def to_json(self) -> str:
        """Convert invoice to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Invoice':
        """Create invoice from dictionary."""
        invoice = cls(
            invoice_id=data.get('invoice_id', f"INV-{uuid.uuid4().hex[:8].upper()}"),
            customer=Customer.from_dict(data['customer']) if data.get('customer') else None,
            company=CompanyDetails.from_dict(data['company']) if data.get('company') else None,
            tax_rate=data.get('tax_rate', 18.0),
            discount=data.get('discount', 0.0),
            discount_type=data.get('discount_type', 'fixed'),
            signature=data.get('signature', '')
        )
        
        # Add products
        for product_data in data.get('products', []):
            invoice.add_product(Product.from_dict(product_data))
        
        # Handle created_at
        if 'created_at' in data:
            invoice.created_at = datetime.fromisoformat(data['created_at'])
        
        return invoice
    
    @classmethod
    def from_json(cls, json_str: str) -> 'Invoice':
        """Create invoice from JSON string."""
        return cls.from_dict(json.loads(json_str))
    
    def get_formatted_date(self) -> str:
        """Get formatted date string."""
        return self.created_at.strftime("%d %B %Y, %I:%M %p")
    
    def get_formatted_id(self) -> str:
        """Get formatted invoice ID."""
        return self.invoice_id


# Default company details for demo
DEFAULT_COMPANY = CompanyDetails(
    name="Your Company Name",
    address="123 Business Street, City, State - PIN Code",
    phone="+91 1234567890",
    email="contact@company.com",
    gst_number="XX9999XX999999"
)


# Error handling classes
class InvoiceError(Exception):
    """Base exception for invoice errors."""
    pass


class ValidationError(InvoiceError):
    """Exception for validation errors."""
    pass


class PDFGenerationError(InvoiceError):
    """Exception for PDF generation errors."""
    pass


class StorageError(InvoiceError):
    """Exception for storage errors."""
    pass