# Certificate OCR Backend

Flask-based backend for certificate OCR processing using Tesseract.

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install Tesseract OCR:
   - **Windows**: Download from https://github.com/UB-Mannheim/tesseract/wiki
   - **macOS**: `brew install tesseract`
   - **Linux**: `sudo apt-get install tesseract-ocr`

3. (Optional) Configure Tesseract path on Windows if not in PATH:

    Set an environment variable `TESSERACT_CMD` to the full path of `tesseract.exe`, e.g.:

    - PowerShell:
       ```powershell
       $env:TESSERACT_CMD = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
       ```
    - cmd.exe:
       ```bat
       set TESSERACT_CMD=C:\\Program Files\\Tesseract-OCR\\tesseract.exe
       ```
    - Bash (Git Bash):
       ```bash
       export TESSERACT_CMD="/c/Program Files/Tesseract-OCR/tesseract.exe"
       ```

PDFs are processed using PyMuPDF (no Poppler required).

## Running the Server

```bash
# Using Windows cmd
venv\Scripts\activate && python app.py

# Using Git Bash
source venv/Scripts/activate && python app.py
```

Server runs on `http://localhost:5000`.

## API Endpoints

### POST /api/ocr
Upload image or PDF file for OCR processing.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: file (image or PDF)

**Response:**
```json
{
  "success": true,
  "file_type": "image|pdf",
  "text": "extracted text content",
  "pages": 1,
  "original_filename": "certificate.pdf",
  "file_size": 1234567,
  "message": "Text extracted successfully"
}
```

### GET /
Health check endpoint.

## Supported File Types
- Images: PNG, JPG, JPEG, BMP, TIFF
- Documents: PDF

## Features
- Handles both images and PDFs
- Converts PDF pages to images for OCR
- Configurable OCR settings for better accuracy
- CORS enabled for frontend integration
- Error handling and logging
- File cleanup after processing
- 16MB file size limit