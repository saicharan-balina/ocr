import os
from typing import List, Optional
import logging

import pytesseract
from PIL import Image
import fitz  # PyMuPDF

# Optional OpenCV for preprocessing (improves OCR accuracy if installed)
try:
    import cv2  # type: ignore
    import numpy as np  # type: ignore
    _CV2_AVAILABLE = True
except Exception:  # pragma: no cover - optional dependency
    _CV2_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OCRProcessor:
    """Handles OCR processing for images and PDFs"""
    
    def __init__(self):
        # Configure Tesseract path via environment variable if provided (Windows-friendly)
        # Set TESSERACT_CMD to something like: C:\\Program Files\\Tesseract-OCR\\tesseract.exe
        tesseract_cmd = os.getenv('TESSERACT_CMD')
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
            logger.info(f"Using Tesseract at: {tesseract_cmd}")
        
        # Language and tuning via environment (defaults for general English docs)
        self.lang = os.getenv('TESSERACT_LANG', 'eng')
        # Zoom factor for rasterizing PDFs (higher -> sharper images, more CPU/RAM)
        self.pdf_zoom: float = float(os.getenv('OCR_PDF_ZOOM', '3.0'))  # ~216 DPI
        # Candidate PSMs to try; we'll select the best by mean confidence
        self.psm_candidates = [int(x) for x in os.getenv('OCR_PSM_LIST', '6,4,3,11').split(',') if x]

        # Base OCR configuration; PSM will be appended dynamically
        default_whitelist = (
            "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
            "0123456789.,!?@#$%^&*()_+-=[]{}|;:,.<>? "
        )
        whitelist = os.getenv('OCR_WHITELIST', default_whitelist)
        self.base_config = f"--oem 3 -l {self.lang} -c tessedit_char_whitelist={whitelist}"

    # ----------------------------
    # Internal helpers
    # ----------------------------
    def _preprocess_image(self, image: Image.Image) -> Image.Image:
        """Apply light preprocessing to improve OCR accuracy.

        Uses OpenCV if available: grayscale, denoise, and Otsu thresholding.
        Falls back to the original image if OpenCV isn't available.
        """
        if not _CV2_AVAILABLE:
            return image

        try:
            # Convert PIL -> OpenCV (RGB -> BGR conversions handled explicitly)
            img_rgb = np.array(image)
            if img_rgb.ndim == 2:  # already grayscale
                gray = img_rgb
            else:
                gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)

            # Denoise a bit without losing edges
            gray = cv2.bilateralFilter(gray, d=7, sigmaColor=50, sigmaSpace=50)

            # Global Otsu thresholding; keep text dark on light background
            _, th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # Optional small morphology to clean noise
            kernel = np.ones((1, 1), np.uint8)
            th = cv2.morphologyEx(th, cv2.MORPH_OPEN, kernel, iterations=1)

            return Image.fromarray(th)
        except Exception as e:  # fallback gracefully
            logger.debug(f"Preprocessing skipped due to error: {e}")
            return image

    def _ocr_with_best_psm(self, image: Image.Image) -> str:
        """Try multiple PSM modes and choose the result with highest mean confidence."""
        best_text = ""
        best_conf = -1.0
        chosen_psm: Optional[int] = None

        for psm in self.psm_candidates:
            config = f"{self.base_config} --psm {psm}"
            try:
                data = pytesseract.image_to_data(image, config=config, output_type=pytesseract.Output.DICT)
                confs = [float(c) for c in data.get('conf', []) if str(c).strip() not in ('', '-1')]
                mean_conf = sum(confs) / len(confs) if confs else 0.0
                if mean_conf > best_conf:
                    best_conf = mean_conf
                    chosen_psm = psm
            except Exception as e:
                logger.debug(f"PSM {psm} scoring failed: {e}")

        # Final OCR with the chosen PSM (or default 6 if none worked)
        final_psm = chosen_psm if chosen_psm is not None else 6
        final_config = f"{self.base_config} --psm {final_psm}"
        text = pytesseract.image_to_string(image, config=final_config)
        logger.info(f"OCR used PSM={final_psm} mean_conf={best_conf:.2f} length={len(text)}")
        return text
    
    def extract_text_from_image(self, image_path: str) -> str:
        """Extract text from a single image using Tesseract OCR"""
        try:
            # Open and process the image
            image = Image.open(image_path)

            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Preprocess to improve OCR accuracy
            preprocessed = self._preprocess_image(image)

            # Extract text using best PSM selection
            text = self._ocr_with_best_psm(preprocessed)
            
            logger.info(f"Successfully extracted text from image: {len(text)} characters")
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from image: {str(e)}")
            raise Exception(f"OCR processing failed: {str(e)}")
    
    def extract_text_from_pdf(self, pdf_path: str) -> List[str]:
        """Extract text from a PDF.

        Strategy per page:
        1) Try direct text extraction via PyMuPDF (great when PDFs are not scans).
        2) If not enough text, rasterize at high res and run OCR with preprocessing.
        """
        try:
            extracted_texts: List[str] = []

            # Open the PDF with PyMuPDF (no external Poppler dependency)
            with fitz.open(pdf_path) as doc:
                if doc.page_count == 0:
                    raise Exception("PDF has no pages")

                mat = fitz.Matrix(self.pdf_zoom, self.pdf_zoom)

                for i, page in enumerate(doc):
                    try:
                        # 1) Try built-in text extraction first
                        direct_text = page.get_text("text") or ""
                        direct_text = direct_text.strip()

                        # Heuristic: if we have enough characters, trust direct extract
                        if len(direct_text) >= 20:
                            extracted_texts.append(direct_text)
                            logger.info(f"Page {i+1}: used direct text extraction (len={len(direct_text)})")
                            continue

                        # 2) Rasterize and OCR
                        pix = page.get_pixmap(matrix=mat, alpha=False)

                        # Convert to PIL Image
                        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

                        # Preprocess and OCR on the image
                        preprocessed = self._preprocess_image(image)
                        text = self._ocr_with_best_psm(preprocessed)
                        extracted_texts.append(text.strip())
                        logger.info(f"Page {i+1}: used OCR (len={len(text)})")

                    except Exception as page_error:
                        logger.error(f"Error processing page {i+1}: {str(page_error)}")
                        extracted_texts.append(f"Error processing page {i+1}: {str(page_error)}")

            logger.info(f"Successfully processed PDF with {len(extracted_texts)} pages")
            return extracted_texts

        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise Exception(f"PDF processing failed: {str(e)}")
    
    def process_file(self, file_path: str, file_type: str) -> dict:
        """Main method to process uploaded files"""
        try:
            if file_type.lower() in ['jpg', 'jpeg', 'png', 'bmp', 'tiff']:
                # Process image file
                text = self.extract_text_from_image(file_path)
                return {
                    'success': True,
                    'file_type': 'image',
                    'text': text,
                    'pages': 1,
                    'message': 'Text extracted successfully from image'
                }
                
            elif file_type.lower() == 'pdf':
                # Process PDF file
                texts = self.extract_text_from_pdf(file_path)
                combined_text = '\n\n--- Page Break ---\n\n'.join(texts)
                
                return {
                    'success': True,
                    'file_type': 'pdf',
                    'text': combined_text,
                    'pages': len(texts),
                    'page_texts': texts,
                    'message': f'Text extracted successfully from {len(texts)} pages'
                }
            
            else:
                raise Exception(f"Unsupported file type: {file_type}")
                
        except Exception as e:
            logger.error(f"Error processing file: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to process file'
            }