"""
Invoice Generator System - PDF Generator
=========================================
This module handles the generation of professional PDF invoices using reportlab.

Author: Invoice Generator System
Date: 2026-03-28
"""

import os
from datetime import datetime
from typing import Optional, Tuple
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from invoice_models import Invoice, InvoiceError


class PDFGenerator:
    """
    Generates professional PDF invoices using reportlab.
    
    Attributes:
        output_dir: Directory to save generated PDFs
        invoice: Invoice object to generate PDF from
    """
    
    # Color scheme
    PRIMARY_COLOR = colors.HexColor("#1a237e")  # Dark blue
    SECONDARY_COLOR = colors.HexColor("#f5f5f5")  # Light gray
    ACCENT_COLOR = colors.HexColor("#3949ab")  # Medium blue
    TEXT_COLOR = colors.HexColor("#212121")  # Dark gray
    BORDER_COLOR = colors.HexColor("#e0e0e0")  # Light border
    
    def __init__(self, output_dir: str = "invoices"):
        """
        Initialize PDF Generator.
        
        Args:
            output_dir: Directory to save generated PDFs
        """
        self.output_dir = output_dir
        self._create_output_directory()
        self._setup_styles()
    
    def _create_output_directory(self):
        """Create output directory if it doesn't exist."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def _setup_styles(self):
        """Setup custom paragraph styles."""
        self.styles = getSampleStyleSheet()
        
        # Custom styles for invoice
        self.styles.add(ParagraphStyle(
            name='InvoiceHeader',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=self.PRIMARY_COLOR,
            spaceAfter=10,
            alignment=0  # Left aligned
        ))
        
        self.styles.add(ParagraphStyle(
            name='InvoiceSubHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            textColor=self.ACCENT_COLOR,
            spaceAfter=5
        ))
        
        self.styles.add(ParagraphStyle(
            name='InvoiceNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=self.TEXT_COLOR,
            spaceAfter=3
        ))
        
        self.styles.add(ParagraphStyle(
            name='InvoiceSmall',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=self.TEXT_COLOR,
            spaceAfter=2
        ))
        
        self.styles.add(ParagraphStyle(
            name='InvoiceBold',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=self.TEXT_COLOR,
            spaceAfter=3,
            fontName='Helvetica-Bold'
        ))
    
    def generate(self, invoice: Invoice, preview: bool = False) -> str:
        """
        Generate PDF invoice.
        
        Args:
            invoice: Invoice object to generate PDF from
            preview: If True, return path for preview
            
        Returns:
            Path to generated PDF file
            
        Raises:
            PDFGenerationError: If PDF generation fails
        """
        try:
            # Validate invoice
            invoice.validate()
            
            # Generate file path
            filename = f"{invoice.invoice_id}.pdf"
            filepath = os.path.join(self.output_dir, filename)
            
            # Create PDF document
            doc = SimpleDocTemplate(
                filepath,
                pagesize=A4,
                rightMargin=20*mm,
                leftMargin=20*mm,
                topMargin=20*mm,
                bottomMargin=20*mm
            )
            
            # Build PDF content
            story = []
            story.extend(self._build_header(invoice))
            story.extend(self._build_customer_section(invoice))
            story.extend(self._build_products_table(invoice))
            story.extend(self._build_pricing_summary(invoice))
            story.extend(self._build_footer(invoice))
            
            # Generate PDF
            doc.build(story)
            
            return filepath
            
        except Exception as e:
            raise PDFGenerationError(f"Failed to generate PDF: {str(e)}")
    
    def _build_header(self, invoice: Invoice) -> list:
        """
        Build the header section of the invoice.
        
        Args:
            invoice: Invoice object
            
        Returns:
            List of Platypus elements
        """
        elements = []
        
        # Company info on left, Invoice info on right
        header_data = [
            [
                # Company name and details
                Paragraph(
                    f"<b>{invoice.company.name}</b><br/>"
                    f"{invoice.company.address}<br/>"
                    f"Phone: {invoice.company.phone}<br/>"
                    f"Email: {invoice.company.email}",
                    self.styles['InvoiceNormal']
                ),
                # Invoice details
                Paragraph(
                    f"<b>INVOICE</b><br/>"
                    f"Invoice ID: {invoice.invoice_id}<br/>"
                    f"Date: {invoice.get_formatted_date()}",
                    self.styles['InvoiceNormal']
                )
            ]
        ]
        
        header_table = Table(header_data, colWidths=[300, 200])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ]))
        
        elements.append(header_table)
        elements.append(Spacer(1, 20))
        
        # Horizontal line
        line_data = [['', '']]
        line_table = Table(line_data, colWidths=[520])
        line_table.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (-1, 0), 1, self.PRIMARY_COLOR),
        ]))
        elements.append(line_table)
        elements.append(Spacer(1, 15))
        
        # GST number if available
        if invoice.company.gst_number:
            elements.append(Paragraph(
                f"GST Number: {invoice.company.gst_number}",
                self.styles['InvoiceSmall']
            ))
            elements.append(Spacer(1, 10))
        
        return elements
    
    def _build_customer_section(self, invoice: Invoice) -> list:
        """
        Build the customer details section.
        
        Args:
            invoice: Invoice object
            
        Returns:
            List of Platypus elements
        """
        elements = []
        
        # Section title
        elements.append(Paragraph(
            "<b>Bill To:</b>",
            self.styles['InvoiceSubHeader']
        ))
        elements.append(Spacer(1, 5))
        
        # Customer details
        customer = invoice.customer
        customer_details = f"""
        <b>{customer.name}</b><br/>
        Phone: {customer.phone}<br/>
        Email: {customer.email}
        """
        
        if customer.address:
            customer_details += f"<br/>Address: {customer.address}"
        
        if customer.gst_number:
            customer_details += f"<br/>GST Number: {customer.gst_number}"
        
        elements.append(Paragraph(customer_details, self.styles['InvoiceNormal']))
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _build_products_table(self, invoice: Invoice) -> list:
        """
        Build the products table section.
        
        Args:
            invoice: Invoice object
            
        Returns:
            List of Platypus elements
        """
        elements = []
        
        # Section title
        elements.append(Paragraph(
            "<b>Product Details:</b>",
            self.styles['InvoiceSubHeader']
        ))
        elements.append(Spacer(1, 10))
        
        # Table data
        table_data = [
            ['#', 'Product Name', 'Qty', 'Rate (₹)', 'Total (₹)']
        ]
        
        for idx, product in enumerate(invoice.products, 1):
            table_data.append([
                str(idx),
                product.name,
                str(product.quantity),
                f"{product.price_per_unit:,.2f}",
                f"{product.total:,.2f}"
            ])
        
        # Create table
        products_table = Table(table_data, colWidths=[30, 250, 50, 80, 80])
        
        # Style the table
        style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.PRIMARY_COLOR),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('TEXTCOLOR', (0, 1), (-1, -1), self.TEXT_COLOR),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('ALIGN', (2, 1), (2, -1), 'CENTER'),
            ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 0.5, self.BORDER_COLOR),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, self.SECONDARY_COLOR]),
        ])
        
        products_table.setStyle(style)
        elements.append(products_table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _build_pricing_summary(self, invoice: Invoice) -> list:
        """
        Build the pricing summary section.
        
        Args:
            invoice: Invoice object
            
        Returns:
            List of Platypus elements
        """
        elements = []
        
        # Calculate column widths for summary table
        label_width = 200
        value_width = 100
        
        # Summary data
        summary_data = [
            ['Subtotal:', f"₹ {invoice.subtotal:,.2f}"]
        ]
        
        # Add discount if applicable
        if invoice.discount > 0:
            if invoice.discount_type == 'percentage':
                discount_label = f"Discount ({invoice.discount}%):"
            else:
                discount_label = "Discount:"
            summary_data.append([discount_label, f"- ₹ {invoice.discount_amount:,.2f}"])
        
        # Add tax
        summary_data.append([
            f"Tax ({invoice.tax_rate}%):",
            f"₹ {invoice.tax_amount:,.2f}"
        ])
        
        # Add border before total
        border_row_len = len(summary_data)
        summary_data.append(['', ''])
        
        # Add total
        summary_data.append([
            '<b>Total:</b>',
            f"<b>₹ {invoice.total:,.2f}</b>"
        ])
        
        # Create table
        summary_table = Table(summary_data, colWidths=[label_width, value_width])
        
        # Style the table
        style = TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -3), self.TEXT_COLOR),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            # Border before total
            ('LINEABOVE', (0, border_row_len - 1), (-1, border_row_len - 1), 1, self.BORDER_COLOR),
            # Total row - bold
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('TEXTCOLOR', (0, -1), (-1, -1), self.PRIMARY_COLOR),
        ])
        
        summary_table.setStyle(style)
        
        # Create a wrapper table for alignment
        wrapper_data = [[summary_table]]
        wrapper_table = Table(wrapper_data, colWidths=[300])
        wrapper_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'RIGHT'),
        ]))
        
        elements.append(wrapper_table)
        elements.append(Spacer(1, 30))
        
        return elements
    
    def _build_footer(self, invoice: Invoice) -> list:
        """
        Build the footer section.
        
        Args:
            invoice: Invoice object
            
        Returns:
            List of Platypus elements
        """
        elements = []
        
        # Terms and conditions
        elements.append(Paragraph(
            "<b>Terms & Conditions:</b>",
            self.styles['InvoiceSubHeader']
        ))
        elements.append(Spacer(1, 5))
        elements.append(Paragraph(
            "1. Payment is due within 30 days of invoice date.<br/>"
            "2. Please include invoice number on your payment details.<br/>"
            "3. For queries, contact us at the email mentioned above.",
            self.styles['InvoiceSmall']
        ))
        elements.append(Spacer(1, 20))
        
        # Digital signature
        if invoice.signature:
            elements.append(Paragraph(
                "<b>Authorized Signature:</b>",
                self.styles['InvoiceSubHeader']
            ))
            elements.append(Spacer(1, 5))
            elements.append(Paragraph(
                f"<i>{invoice.signature}</i>",
                self.styles['InvoiceNormal']
            ))
            elements.append(Spacer(1, 10))
        
        # Thank you message
        elements.append(Paragraph(
            "<i>Thank you for your business!</i>",
            self.styles['InvoiceNormal']
        ))
        elements.append(Spacer(1, 20))
        
        # Footer line
        footer_data = [[
            Paragraph(
                f"Generated on {datetime.now().strftime('%d-%m-%Y %I:%M %p')}",
                self.styles['InvoiceSmall']
            )
        ]]
        footer_table = Table(footer_data, colWidths=[520])
        footer_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, -1), 20),
        ]))
        elements.append(footer_table)
        
        return elements
    
    def generate_to_bytes(self, invoice: Invoice) -> bytes:
        """
        Generate PDF to bytes (for preview/download).
        
        Args:
            invoice: Invoice object
            
        Returns:
            PDF as bytes
        """
        try:
            # Create PDF in memory
            buffer = BytesIO()
            
            doc = SimpleDocTemplate(
                buffer,
                pagesize=A4,
                rightMargin=20*mm,
                leftMargin=20*mm,
                topMargin=20*mm,
                bottomMargin=20*mm
            )
            
            # Build PDF content
            story = []
            story.extend(self._build_header(invoice))
            story.extend(self._build_customer_section(invoice))
            story.extend(self._build_products_table(invoice))
            story.extend(self._build_pricing_summary(invoice))
            story.extend(self._build_footer(invoice))
            
            # Generate PDF
            doc.build(story)
            
            # Get PDF bytes
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            return pdf_bytes
            
        except Exception as e:
            raise PDFGenerationError(f"Failed to generate PDF: {str(e)}")
    
    def preview_invoice(self, invoice: Invoice):
        """
        Preview invoice by opening the generated PDF.
        
        Args:
            invoice: Invoice object
        """
        # Generate PDF
        filepath = self.generate(invoice, preview=True)
        
        # Open with default PDF viewer
        try:
            os.startfile(filepath)  # Windows
        except AttributeError:
            # For other OS
            import subprocess
            subprocess.call(['open', filepath])  # macOS
            # or subprocess.call(['xdg-open', filepath])  # Linux
    
    def get_latest_pdf_path(self, invoice_id: str) -> Optional[str]:
        """
        Get the path to the latest PDF for an invoice ID.
        
        Args:
            invoice_id: Invoice ID to search for
            
        Returns:
            Path to PDF if exists, None otherwise
        """
        filename = f"{invoice_id}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        if os.path.exists(filepath):
            return filepath
        return None