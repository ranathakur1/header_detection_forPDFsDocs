#!/usr/bin/env python3
"""
Command Line Interface for PDF Header Detector
==============================================

This module provides a command-line interface for the PDF header detection library.
"""

import argparse
import sys
import os
import logging
from typing import Optional

from .detector import HeaderDetector


def setup_logging(verbose: bool = False):
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )


def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Extract headers from PDF documents using intelligent font analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s document.pdf                    # Auto-detect headers
  %(prog)s document.pdf --min-size 14     # Use minimum font size of 14pt
  %(prog)s document.pdf --output headers.json --verbose
  %(prog)s document.pdf --analyze-fonts   # Show detailed font analysis
        """
    )
    
    parser.add_argument(
        "pdf_path",
        help="Path to the PDF file to analyze"
    )
    
    parser.add_argument(
        "--min-size",
        type=float,
        help="Minimum font size for headers (auto-detected if not specified)"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Output JSON file path (default: detected_headers.json)"
    )
    
    parser.add_argument(
        "--analyze-fonts",
        action="store_true",
        help="Show detailed font analysis without detecting headers"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="PDF Header Detector 1.0.0"
    )
    
    args = parser.parse_args()
    
    # Set up logging
    setup_logging(args.verbose)
    
    # Check if PDF file exists
    if not os.path.exists(args.pdf_path):
        print(f"❌ Error: PDF file not found: {args.pdf_path}", file=sys.stderr)
        sys.exit(1)
    
    print("🔍 PDF HEADER DETECTOR")
    print("=" * 40)
    print(f"Analyzing: {args.pdf_path}")
    print()
    
    try:
        # Create the detector
        detector = HeaderDetector()
        
        if args.analyze_fonts:
            # Show font analysis only
            print("📊 Font Analysis:")
            print("-" * 20)
            analysis = detector.get_font_analysis(args.pdf_path)
            
            print(f"Total unique font sizes: {len(analysis['all_sizes'])}")
            print(f"All font sizes: {analysis['all_sizes'][:10]}")
            print(f"Header font sizes: {analysis['header_sizes']}")
            print(f"Body text size (detected): {analysis.get('body_text_size', 'N/A')}pt")
            print(f"Header hierarchy levels: {analysis['total_levels']}")
            print(f"Font frequency (top 5): {list(analysis['font_frequency'].items())[:5]}")
            
        else:
            # Detect headers
            print("🔍 Detecting headers...")
            headers = detector.detect_headers_by_font_size(args.pdf_path, args.min_size)
            
            if headers:
                print(f"✅ Successfully detected {len(headers)} headers!")
                
                # Group headers by level
                headers_by_level = {}
                for header in headers:
                    level = header['header_level_name']
                    if level not in headers_by_level:
                        headers_by_level[level] = []
                    headers_by_level[level].append(header)
                
                print(f"\n📋 Headers by Level:")
                for level in sorted(headers_by_level.keys()):
                    print(f"  {level.upper()}: {len(headers_by_level[level])} headers")
                    for header in headers_by_level[level]:
                        font_size = header.get('_font_size', 'N/A')
                        print(f"    • Page {header['page']:2d}: '{header['header']}' ({font_size}pt)")
                
                # Save to JSON file
                output_file = args.output or "detected_headers.json"
                if detector.save_headers_to_json(headers, output_file):
                    print(f"\n💾 Headers saved to {output_file}")
                
                # Print JSON output if not saving to file or if verbose
                if args.verbose or not args.output:
                    print("\n📄 JSON Output:")
                    print("-" * 40)
                    headers_json = detector.get_headers_json(args.pdf_path, args.min_size)
                    print(headers_json)
                
            else:
                print("❌ No headers detected")
                print("Try running with a lower font size threshold using --min-size")
                sys.exit(1)
                
    except FileNotFoundError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
