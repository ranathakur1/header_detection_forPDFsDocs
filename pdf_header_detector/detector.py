 #!/usr/bin/env python3

"""
PDF Header Detector Module
=========================

This module contains the main CleanHybridPDFChunker class for detecting
headers in PDF documents using intelligent font size analysis.
"""

import os
import json
import logging
from typing import List, Dict, Any
import fitz  # PyMuPDF

# Set up logging
logger = logging.getLogger(__name__)


class HeaderDetector:
    """
    Intelligent PDF Header Detection Engine
    
    This class provides intelligent header detection from PDF documents using
    font size analysis and hierarchy detection.
    
    Attributes:
        detected_headers (List[Dict]): List of detected headers
        full_text (str): Full text content of the PDF
        full_text_words (List[str]): List of words from the PDF
    
    Example:
        >>> detector = HeaderDetector()
        >>> headers = detector.detect_headers_by_font_size("document.pdf")
        >>> json_output = detector.get_headers_json("document.pdf")
    """
    
    def __init__(self):
        """Initialize the PDF header detector."""
        self.detected_headers = []
        self.full_text = ""
        self.full_text_words = []
    
    def detect_headers_by_font_size(self, pdf_path: str, min_size: float = None) -> List[Dict[str, Any]]:
        """
        Enhanced header detection with adaptive font hierarchy analysis
        
        Args:
            pdf_path (str): Path to the PDF file
            min_size (float, optional): Minimum font size for headers (None for auto-detection)
            
        Returns:
            List[Dict[str, Any]]: List of detected headers with their properties and hierarchy levels
            
        Raises:
            FileNotFoundError: If the PDF file doesn't exist
            Exception: If there's an error reading the PDF
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
        # First pass: analyze all font sizes to determine optimal threshold
        if min_size is None:
            min_size = self._auto_detect_header_threshold(pdf_path)
            
        logger.info(f"Detecting headers with font size > {min_size}pt")
        
        try:
            doc = fitz.open(pdf_path)
        except Exception as e:
            raise Exception(f"Error opening PDF file: {e}")
            
        all_text_elements = []
        all_font_sizes = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("dict")["blocks"]
            
            for block in blocks:
                if "lines" not in block:
                    continue
                    
                for line in block["lines"]:
                    for span in line["spans"]:
                        text = span["text"].strip()
                        if text:
                            font_size = round(span["size"], 1)  # Round to nearest 0.1pt
                            all_font_sizes.append(font_size)
                            
                            bbox = span.get("bbox", [0, 0, 0, 0])
                            all_text_elements.append({
                                "text": text,
                                "font_size": font_size,
                                "font_name": span["font"],
                                "is_bold": span["flags"] & 16,
                                "page": page_num + 1,
                                "bbox": bbox,
                                "x": bbox[0],
                                "y": bbox[1]
                            })
        
        doc.close()
        
        # Analyze font size distribution
        font_analysis = self._analyze_font_hierarchy(all_font_sizes, min_size)
        logger.info(f"Font analysis: {font_analysis}")
        
        # Group text elements by Y position (same line across blocks)
        grouped_elements = self._group_by_y_position(all_text_elements)
        
        # Filter for headers based on enhanced font analysis
        headers = []
        for group in grouped_elements:
            max_font_size = max(elem["font_size"] for elem in group)
            
            # Check if this font size qualifies as a header
            if max_font_size in font_analysis["header_levels"]:
                # Combine text from all elements in the group
                combined_text = " ".join(elem["text"] for elem in sorted(group, key=lambda x: x["x"]))
                
                # Check length criteria (more flexible for different header types)
                if 2 < len(combined_text) < 300 and not self._is_likely_body_text(combined_text, max_font_size):
                    # Use properties from the element with max font size
                    main_element = max(group, key=lambda x: x["font_size"])
                    
                    # Determine hierarchy level
                    header_level = font_analysis["header_levels"][max_font_size]
                    
                    headers.append({
                        "header": combined_text,
                        "header_level_name": f"level {header_level}",
                        "page": main_element["page"],
                        "header_level": header_level,
                        "_font_size": max_font_size  # Temporary for logging
                    })
        
        # Remove duplicates (same text appearing multiple times)
        unique_headers = []
        seen_texts = set()
        
        for header in headers:
            if header["header"] not in seen_texts:
                unique_headers.append(header)
                seen_texts.add(header["header"])
        
        # Sort by page order only since we removed bbox
        unique_headers.sort(key=lambda x: x["page"])
        
        logger.info(f"Found {len(unique_headers)} unique headers with enhanced detection")
        
        for i, header in enumerate(unique_headers):
            logger.info(f"  {i+1}. Page {header['page']}: '{header['header']}' ({header['_font_size']:.1f}pt) - {header['header_level_name']}")
        
        self.detected_headers = unique_headers
        return unique_headers

    def _auto_detect_header_threshold(self, pdf_path: str) -> float:
        """
        Automatically detect the optimal threshold for header detection
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            float: Optimal minimum font size for headers
        """
        doc = fitz.open(pdf_path)
        all_font_sizes = []
        
        # Quick scan to get all font sizes
        for page_num in range(min(5, len(doc))):  # Sample first 5 pages
            page = doc[page_num]
            blocks = page.get_text("dict")["blocks"]
            
            for block in blocks:
                if "lines" not in block:
                    continue
                    
                for line in block["lines"]:
                    for span in line["spans"]:
                        if span["text"].strip():
                            all_font_sizes.append(round(span["size"], 1))
        
        doc.close()
        
        # Analyze font distribution
        from collections import Counter
        size_counts = Counter(all_font_sizes)
        unique_sizes = sorted(set(all_font_sizes), reverse=True)
        
        # Find the most common font sizes (likely body text)
        most_common = size_counts.most_common(3)
        logger.info(f"Font size analysis for threshold detection: {most_common}")
        
        # Conservative approach: start with a low threshold to capture more headers
        # We'll filter out body text in the hierarchy analysis
        min_threshold = 12.0  # Conservative minimum
        
        # Check if we have large headers (>25pt) - these are definitely headers
        large_headers = [s for s in unique_sizes if s > 25.0]
        if large_headers:
            # If we have large headers, use a more permissive threshold
            threshold = min_threshold
        else:
            # No large headers found, be more conservative
            most_common_size = most_common[0][0] if most_common else 12.0
            threshold = most_common_size + 1.0
            
        logger.info(f"Auto-detected header threshold: {threshold}pt")
        return threshold

    def _is_likely_body_text(self, text: str, font_size: float = None) -> bool:
        """
        Heuristic to identify if text is likely body text rather than a header
        
        Args:
            text (str): The text to analyze
            font_size (float, optional): The font size of the text (if available)
            
        Returns:
            bool: True if text appears to be body text
        """
        # Large fonts are likely headers, not body text
        if font_size and font_size > 20.0:
            return False
            
        # Very long text is probably body text
        if len(text) > 200:
            return True
            
        # Text with common body text patterns
        body_indicators = [
            "the", "and", "of", "in", "to", "for", "with", "on", "at", "by",
            "this", "that", "these", "those", "such", "can", "will", "should",
            "figure", "table", "page", "section", "chapter", "appendix", "see"
        ]
        
        words = text.lower().split()
        if len(words) > 15:  # Very long sentences are usually body text
            return True
            
        # Count body text indicators
        body_count = sum(1 for word in words if word in body_indicators)
        
        # If more than 40% are common words, likely body text
        # But be less strict for shorter text (potential headers)
        threshold = 0.5 if len(words) > 8 else 0.6
        return body_count > len(words) * threshold
    
    def _group_by_y_position(self, elements: List[Dict[str, Any]], tolerance: float = 1.0) -> List[List[Dict[str, Any]]]:
        """
        Group text elements that are on the same Y position (same line) and same page
        
        Args:
            elements (List[Dict[str, Any]]): List of text elements
            tolerance (float): Y-position tolerance for grouping
            
        Returns:
            List[List[Dict[str, Any]]]: Grouped elements
        """
        if not elements:
            return []
        
        # Group by page first, then by Y position within each page
        pages = {}
        for element in elements:
            page_num = element["page"]
            if page_num not in pages:
                pages[page_num] = []
            pages[page_num].append(element)
        
        all_groups = []
        
        for page_num, page_elements in pages.items():
            # Sort by Y position within the page
            sorted_elements = sorted(page_elements, key=lambda x: x["y"])
            
            if not sorted_elements:
                continue
                
            page_groups = []
            current_group = [sorted_elements[0]]
            current_y = sorted_elements[0]["y"]
            
            for element in sorted_elements[1:]:
                if abs(element["y"] - current_y) <= tolerance:
                    # Same line - add to current group
                    current_group.append(element)
                else:
                    # Different line - start new group
                    if current_group:
                        page_groups.append(current_group)
                    current_group = [element]
                    current_y = element["y"]
            
            # Don't forget the last group
            if current_group:
                page_groups.append(current_group)
                
            all_groups.extend(page_groups)
        
        return all_groups

    def _analyze_font_hierarchy(self, all_font_sizes: List[float], min_size: float) -> Dict[str, Any]:
        """
        Enhanced font hierarchy analysis with automatic body text detection
        
        Args:
            all_font_sizes (List[float]): List of all font sizes in the document
            min_size (float): Minimum font size threshold for initial filtering
            
        Returns:
            Dict[str, Any]: Dictionary with font analysis and hierarchy levels
        """
        # Round font sizes to handle floating-point precision issues (to nearest 0.1pt)
        rounded_sizes = [round(size, 1) for size in all_font_sizes]
        all_unique_sizes = sorted(set(rounded_sizes), reverse=True)
        
        logger.info(f"All font sizes (rounded): {all_unique_sizes[:10]}")
        
        # Get font sizes above minimum threshold
        header_font_sizes = [size for size in rounded_sizes if size > min_size]
        header_unique_sizes = sorted(set(header_font_sizes), reverse=True)
        
        logger.info(f"Header font sizes (>{min_size}pt): {header_unique_sizes}")
        
        # Enhanced logic: Auto-detect body text as the most common small font
        # Count frequency of each font size
        from collections import Counter
        size_counts = Counter(rounded_sizes)
        
        # Find the most common font sizes (likely body text)
        most_common = size_counts.most_common(5)
        logger.info(f"Most common font sizes: {most_common}")
        
        # Identify body text candidates (frequent, smaller fonts)
        # Only consider fonts below a reasonable header threshold (20pt)
        body_text_candidates = [size for size, count in most_common 
                               if size <= 20.0 and count > 5]
        
        if body_text_candidates:
            # Use the largest frequent small font as body text
            body_text_size = max(body_text_candidates)
            logger.info(f"Detected body text size: {body_text_size}pt")
            
            # Filter headers: must be significantly larger than body text
            # But ensure we don't lose any fonts > 20pt (definitely headers)
            filtered_sizes = []
            for size in header_unique_sizes:
                if size > 20.0:  # Always include larger fonts
                    filtered_sizes.append(size)
                elif size > body_text_size + 2.0:  # Include fonts significantly larger than body
                    filtered_sizes.append(size)
        else:
            # Fallback: use original logic with conservative body text detection
            body_text_size = min_size
            filtered_sizes = header_unique_sizes
        
        logger.info(f"Final header sizes for hierarchy (excluding body text): {filtered_sizes}")
        
        # Group very similar font sizes (within 0.5pt) to handle rounding issues
        grouped_sizes = []
        used_sizes = set()
        
        for size in filtered_sizes:
            if size in used_sizes:
                continue
                
            # Find all sizes within 0.5pt of this one
            similar_sizes = [s for s in filtered_sizes 
                           if abs(s - size) <= 0.5 and s not in used_sizes]
            
            if similar_sizes:
                # Use the most common size in the group, or the largest if tied
                group_representative = max(similar_sizes)
                grouped_sizes.append(group_representative)
                used_sizes.update(similar_sizes)
        
        # Sort grouped sizes in descending order
        grouped_sizes.sort(reverse=True)
        logger.info(f"Grouped header sizes: {grouped_sizes}")
        
        # Create hierarchy levels (level1 = largest font, level2 = second largest, etc.)
        header_levels = {}
        size_to_level = {}
        
        for i, grouped_size in enumerate(grouped_sizes, 1):
            # Map all similar sizes to the same level
            for original_size in header_unique_sizes:
                if abs(original_size - grouped_size) <= 0.5:
                    header_levels[original_size] = i
                    size_to_level[original_size] = i
        
        return {
            "all_sizes": all_unique_sizes,
            "header_sizes": header_unique_sizes,
            "body_text_size": body_text_size,
            "filtered_sizes": grouped_sizes,
            "header_levels": header_levels,
            "size_to_level": size_to_level,
            "total_levels": len(grouped_sizes),
            "font_frequency": dict(most_common)
        }

    def _get_header_level(self, font_size: float, header_levels: Dict[float, int]) -> int:
        """
        Get the hierarchy level for a given font size
        
        Args:
            font_size (float): The font size to classify
            header_levels (Dict[float, int]): Dictionary mapping font sizes to levels
            
        Returns:
            int: Integer level (1 = highest level, 2 = second level, etc.)
        """
        return header_levels.get(font_size, 99)  # Return 99 for unclassified sizes

    def save_headers_to_json(self, headers: List[Dict[str, Any]], output_file: str = "detected_headers.json") -> bool:
        """
        Save detected headers to JSON file
        
        Args:
            headers (List[Dict[str, Any]]): List of headers to save
            output_file (str): Output file path
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Remove temporary fields before saving
            clean_headers = []
            for header in headers:
                clean_header = {k: v for k, v in header.items() if not k.startswith('_')}
                clean_headers.append(clean_header)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(clean_headers, f, indent=2, ensure_ascii=False)
            logger.info(f"Headers saved to {output_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving headers to JSON: {e}")
            return False

    def get_headers_json(self, pdf_path: str, min_size: float = None) -> str:
        """
        Get headers as JSON string with enhanced detection
        
        Args:
            pdf_path (str): Path to the PDF file
            min_size (float, optional): Minimum font size for headers
            
        Returns:
            str: JSON string representation of detected headers
        """
        headers = self.detect_headers_by_font_size(pdf_path, min_size)
        # Remove temporary fields before converting to JSON
        clean_headers = []
        for header in headers:
            clean_header = {k: v for k, v in header.items() if not k.startswith('_')}
            clean_headers.append(clean_header)
        return json.dumps(clean_headers, indent=2, ensure_ascii=False)

    def get_font_analysis(self, pdf_path: str) -> Dict[str, Any]:
        """
        Get detailed font analysis of the PDF without detecting headers
        
        Args:
            pdf_path (str): Path to the PDF file
            
        Returns:
            Dict[str, Any]: Font analysis results
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
        doc = fitz.open(pdf_path)
        all_font_sizes = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            blocks = page.get_text("dict")["blocks"]
            
            for block in blocks:
                if "lines" not in block:
                    continue
                    
                for line in block["lines"]:
                    for span in line["spans"]:
                        if span["text"].strip():
                            all_font_sizes.append(round(span["size"], 1))
        
        doc.close()
        
        threshold = self._auto_detect_header_threshold(pdf_path)
        return self._analyze_font_hierarchy(all_font_sizes, threshold)
