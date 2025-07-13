"""
PDF Header Detector - A library for extracting headers from PDF documents
=========================================================================

This library provides intelligent header detection from PDF documents using
font size analysis and hierarchy detection.

Main classes:
    HeaderDetector: The main class for header detection

Example usage:
    from pdf_header_detector import HeaderDetector
    
    detector = HeaderDetector()
    headers = detector.detect_headers_by_font_size("document.pdf")
    print(detector.get_headers_json("document.pdf"))
"""

from .detector import HeaderDetector

__version__ = "1.0.0"
__author__ = "Assistant"
__email__ = "assistant@example.com"
__description__ = "A library for intelligent PDF header detection using font analysis"

__all__ = ["HeaderDetector"]
