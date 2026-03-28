"""
Invoice Generator System - Main Entry Point
======================================
This is the main entry point for the Invoice Generator System.

Usage:
    python main.py              - Run with GUI (Tkinter)
    python main.py --cli        - Run with CLI
    python main.py --gui      - Run with GUI
    python main.py --sample   - Create sample invoice

Author: Invoice Generator System
Date: 2026-03-28
"""

import sys
import argparse
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Invoice Generator System - Professional PDF Invoice Generator"
    )
    
    parser.add_argument(
        '--cli',
        action='store_true',
        help='Run with Command Line Interface'
    )
    
    parser.add_argument(
        '--gui',
        action='store_true',
        help='Run with Graphical User Interface (Tkinter)'
    )
    
    parser.add_argument(
        '--sample',
        action='store_true',
        help='Create a sample invoice'
    )
    
    args = parser.parse_args()
    
    # Create sample invoice
    if args.sample:
        from invoice_manager import InvoiceManager
        from pdf_generator import PDFGenerator
        
        print("Creating sample invoice...")
        
        manager = InvoiceManager()
        pdf_gen = PDFGenerator()
        
        invoice = manager.create_sample_invoice()
        manager.save_invoice(invoice)
        pdf_path = pdf_gen.generate(invoice)
        
        print(f"\nSample invoice created!")
        print(f"Invoice ID: {invoice.invoice_id}")
        print(f"PDF: {pdf_path}")
        print(f"Total: Rs. {invoice.total:,.2f}")
        
        # Open PDF
        try:
            import os
            os.startfile(pdf_path)
        except Exception as e:
            print(f"Could not open PDF: {e}")
        
        return
    
    # CLI mode
    if args.cli:
        from cli_interface import main as cli_main
        cli_main()
        return
    
    # GUI mode (default)
    try:
        from gui_interface import main as gui_main
        gui_main()
    except ImportError:
        # Fallback to CLI if Tkinter not available
        print("GUI not available. Starting CLI...")
        from cli_interface import main as cli_main
        cli_main()


if __name__ == "__main__":
    main()