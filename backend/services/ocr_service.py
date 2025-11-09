import easyocr
import cv2
import numpy as np
from PIL import Image
# Compatibility shim: Pillow 10 removed Image.ANTIALIAS constant.
# Define ANTIALIAS alias for older libraries (easyocr) that expect it.
try:
    if not hasattr(Image, 'ANTIALIAS'):
        Image.ANTIALIAS = Image.Resampling.LANCZOS
except Exception:
    pass
import io
import re
from typing import Dict, Optional
import logging
from fastapi import HTTPException
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OCRService:
    def __init__(self):
        """Initialize OCR reader (lazy loading for better startup time)"""
        self.reader = None
    
    def _get_reader(self):
        """Lazy initialization of EasyOCR reader"""
        if self.reader is None:
            logger.info("Initializing EasyOCR reader...")
            self.reader = easyocr.Reader(['en'], gpu=False)
            logger.info("EasyOCR reader initialized")
        return self.reader
    
    async def extract_form16_data(self, file_content: bytes, content_type: str) -> Optional[Dict]:
        """
        Extract structured data from Form-16 document
        
        Args:
            file_content: Binary content of the uploaded file
            content_type: MIME type of the file
            
        Returns:
            Dictionary containing extracted Form-16 data
        """
        try:
            # Convert file to image
            image = self._preprocess_image(file_content, content_type)
            
            # Perform OCR
            reader = self._get_reader()
            results = reader.readtext(image)
            
            # Extract text
            full_text = ' '.join([result[1] for result in results])
            
            # Parse Form-16 data
            form16_data = self._parse_form16_text(full_text, results)
            
            return form16_data
            
        except Exception as e:
            logger.error(f"Error in OCR extraction: {str(e)}")
            return None
    
    def _preprocess_image(self, file_content: bytes, content_type: str) -> np.ndarray:
        """Preprocess image for better OCR accuracy"""
        try:
            if content_type == 'application/pdf':
                try:
                    # For PDF, try to convert first page to image
                    from pdf2image import convert_from_bytes

                    # Prefer explicit POPPLER_PATH environment variable if provided
                    poppler_path = os.getenv("POPPLER_PATH")
                    if poppler_path:
                        images = convert_from_bytes(file_content, first_page=1, last_page=1, poppler_path=poppler_path)
                    else:
                        # Try without explicit path (expects poppler in PATH)
                        images = convert_from_bytes(file_content, first_page=1, last_page=1)

                    image = np.array(images[0])
                except Exception as e:
                    logger.error(f"PDF conversion failed: {str(e)}")

                    # Try a common user-download location as a fallback
                    default_poppler = os.path.join(os.path.expanduser("~"), "poppler", "poppler-23.11.0", "Library", "bin")
                    if os.path.isdir(default_poppler):
                        try:
                            images = convert_from_bytes(file_content, first_page=1, last_page=1, poppler_path=default_poppler)
                            image = np.array(images[0])
                        except Exception as e2:
                            logger.error(f"PDF conversion failed with default poppler path: {str(e2)}")
                            raise HTTPException(
                                status_code=400,
                                detail="PDF processing failed even though Poppler was found. Check Poppler installation."
                            )
                    else:
                        # Clear, actionable error for the client
                        logger.error("Unable to get page count. Is poppler installed and in PATH?")
                        raise HTTPException(
                            status_code=400,
                            detail="PDF processing requires Poppler to be installed and available in PATH, or set POPPLER_PATH to the Poppler bin folder."
                        )
            else:
                # For images
                image = Image.open(io.BytesIO(file_content))
                image = np.array(image)
            
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            
            # Enhance contrast
            image = cv2.convertScaleAbs(image, alpha=1.5, beta=30)
            
            return image
            
        except Exception as e:
            logger.error(f"Error preprocessing image: {str(e)}")
            raise
    
    def _parse_form16_text(self, text: str, ocr_results: list) -> Dict:
        """
        Parse OCR text to extract Form-16 fields
        
        This is a simplified parser. In production, you'd use more sophisticated
        NLP or ML models for better accuracy.
        """
        text_upper = text.upper()
        
        # Initialize data structure
        data = {
            "employee_name": "",
            "pan": "",
            "assessment_year": "",
            "financial_year": "",
            "gross_salary": 0.0,
            "deductions": {
                "section_80c": 0.0,
                "section_80d": 0.0,
                "section_80ccd_1b": 0.0,
                "hra": 0.0,
                "standard_deduction": 0.0,
                "other_deductions": 0.0
            },
            "taxable_income": 0.0,
            "tds": 0.0
        }
        
        # Extract PAN (10 alphanumeric characters)
        pan_pattern = r'\b[A-Z]{5}\d{4}[A-Z]\b'
        pan_match = re.search(pan_pattern, text_upper)
        if pan_match:
            data["pan"] = pan_match.group()
        
        # Extract financial year (e.g., 2023-24, 2023-2024)
        fy_pattern = r'(\d{4})[-/](\d{2,4})'
        fy_match = re.search(fy_pattern, text)
        if fy_match:
            year1 = fy_match.group(1)
            year2 = fy_match.group(2)
            if len(year2) == 2:
                year2 = "20" + year2
            data["financial_year"] = f"{year1}-{year2}"
            data["assessment_year"] = str(int(year1) + 1) + "-" + str(int(year2) + 1)
        
        # Extract monetary values
        # Gross Salary
        gross_patterns = [
            r'GROSS\s+SALARY[:\s]+[₹\s]*([\d,]+\.?\d*)',
            r'SALARY[:\s]+[₹\s]*([\d,]+\.?\d*)',
            r'TOTAL\s+INCOME[:\s]+[₹\s]*([\d,]+\.?\d*)'
        ]
        for pattern in gross_patterns:
            match = re.search(pattern, text_upper, re.IGNORECASE)
            if match:
                data["gross_salary"] = self._parse_amount(match.group(1))
                break
        
        # Section 80C
        sec80c_patterns = [
            r'80C[:\s]+[₹\s]*([\d,]+\.?\d*)',
            r'SECTION\s+80C[:\s]+[₹\s]*([\d,]+\.?\d*)'
        ]
        for pattern in sec80c_patterns:
            match = re.search(pattern, text_upper, re.IGNORECASE)
            if match:
                data["deductions"]["section_80c"] = self._parse_amount(match.group(1))
                break
        
        # Section 80D
        sec80d_patterns = [
            r'80D[:\s]+[₹\s]*([\d,]+\.?\d*)',
            r'SECTION\s+80D[:\s]+[₹\s]*([\d,]+\.?\d*)'
        ]
        for pattern in sec80d_patterns:
            match = re.search(pattern, text_upper, re.IGNORECASE)
            if match:
                data["deductions"]["section_80d"] = self._parse_amount(match.group(1))
                break
        
        # Section 80CCD(1B) - NPS
        sec80ccd_patterns = [
            r'80CCD[:\s]+[₹\s]*([\d,]+\.?\d*)',
            r'NPS[:\s]+[₹\s]*([\d,]+\.?\d*)'
        ]
        for pattern in sec80ccd_patterns:
            match = re.search(pattern, text_upper, re.IGNORECASE)
            if match:
                data["deductions"]["section_80ccd_1b"] = self._parse_amount(match.group(1))
                break
        
        # HRA
        hra_patterns = [
            r'HRA[:\s]+[₹\s]*([\d,]+\.?\d*)',
            r'HOUSE\s+RENT\s+ALLOWANCE[:\s]+[₹\s]*([\d,]+\.?\d*)'
        ]
        for pattern in hra_patterns:
            match = re.search(pattern, text_upper, re.IGNORECASE)
            if match:
                data["deductions"]["hra"] = self._parse_amount(match.group(1))
                break
        
        # Standard Deduction
        std_patterns = [
            r'STANDARD\s+DEDUCTION[:\s]+[₹\s]*([\d,]+\.?\d*)',
            r'STD\s+DEDUCTION[:\s]+[₹\s]*([\d,]+\.?\d*)'
        ]
        for pattern in std_patterns:
            match = re.search(pattern, text_upper, re.IGNORECASE)
            if match:
                data["deductions"]["standard_deduction"] = self._parse_amount(match.group(1))
                break
        
        # TDS
        tds_patterns = [
            r'TDS[:\s]+[₹\s]*([\d,]+\.?\d*)',
            r'TAX\s+DEDUCTED[:\s]+[₹\s]*([\d,]+\.?\d*)'
        ]
        for pattern in tds_patterns:
            match = re.search(pattern, text_upper, re.IGNORECASE)
            if match:
                data["tds"] = self._parse_amount(match.group(1))
                break
        
        # Calculate taxable income if not explicitly found
        if data["taxable_income"] == 0:
            total_deductions = sum(data["deductions"].values())
            data["taxable_income"] = max(0, data["gross_salary"] - total_deductions)
        
        # Extract employee name (look for name patterns near "NAME" or "EMPLOYEE NAME")
        name_patterns = [
            r'NAME[:\s]+([A-Z\s]+?)(?:\n|PAN|EMPLOYEE|DESIGNATION)',
            r'EMPLOYEE\s+NAME[:\s]+([A-Z\s]+?)(?:\n|PAN|EMPLOYEE)'
        ]
        for pattern in name_patterns:
            match = re.search(pattern, text_upper)
            if match:
                data["employee_name"] = match.group(1).strip()
                break
        
        return data
    
    def _parse_amount(self, amount_str: str) -> float:
        """Convert amount string to float"""
        try:
            # Remove commas and currency symbols
            amount_str = re.sub(r'[₹,\s]', '', amount_str)
            return float(amount_str)
        except:
            return 0.0

