#!/usr/bin/env python3
"""
Header Detection Script - Extract headers from PDF and return as JSON
=====================================================================

This script demonstrates the pdf_header_detector library usage.
For the full library, see the pdf_header_detector package.

Usage:
    python header_detection.py

Author: Assistant
Date: 2025-07-12
"""

import os
import sys
from pdf_header_detector import HeaderDetector


def main():
    """Main function to detect headers and output JSON."""
    
    # Get PDF path from command line argument or use default
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        pdf_path = "input/demo.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        if len(sys.argv) == 1:
            print("Usage: python header_detection.py [PDF_FILE_PATH]")
            print("Example: python header_detection.py 'C:\\Documents\\my_file.pdf'")
        return
    
    print("🔍 PDF HEADER DETECTOR")
    print("=" * 40)
    print(f"Analyzing: {pdf_path}")
    print()
    
    # Create the detector
    detector = HeaderDetector()
    
    # Detect headers with enhanced auto-detection
    print("🔍 Detecting headers with enhanced font analysis...")
    try:
        headers = detector.detect_headers_by_font_size(pdf_path)  # Auto-detect threshold
        
        if headers:
            print(f"✅ Successfully detected {len(headers)} headers!")
            
            # Save to JSON file
            output_file = "detected_headers.json"
            if detector.save_headers_to_json(headers, output_file):
                print(f"\n💾 Headers saved to {output_file}")
            
            # Display first few headers
            print(f"\n📋 Sample Headers:")
            for i, header in enumerate(headers[:5]):
                print(f"  {i+1}. Page {header['page']}: '{header['header']}' (Level {header['header_level']})")
            
            if len(headers) > 5:
                print(f"  ... and {len(headers) - 5} more headers")
                
        else:
            print("❌ No headers detected")
            print("Try running with a lower font size threshold")
            
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
