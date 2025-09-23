# Certificate OCR Application

A full-stack application for extracting text from certificates and documents using OCR technology. Built with Flask backend and Next.js frontend.

## 🚀 Features

- **Multi-format Support**: PDF, PNG, JPG, JPEG, BMP, TIFF
- **Advanced OCR**: Powered by Tesseract OCR engine
- **PDF Processing**: Converts PDF pages to images for text extraction
- **Real-time Processing**: Live status updates and progress indicators
- **Responsive Design**: Works seamlessly on desktop and mobile
- **Secure Processing**: Files are automatically deleted after processing
- **Text Export**: Copy to clipboard or download as text file
- **Error Handling**: Comprehensive error messages and retry mechanisms

## 🏗️ Architecture

```
certificate-ocr/
├── backend/           # Flask API server
│   ├── app.py        # Main Flask application
│   ├── utils/        # OCR and file handling utilities
│   └── uploads/      # Temporary file storage
└── frontend/         # Next.js web application
    ├── app/          # Next.js app directory
    ├── components/   # React components
    └── lib/          # API client and utilities
```

## 🛠️ Installation

### Prerequisites

- Python 3.8+
- Node.js 18+
- Tesseract OCR
- Poppler (for PDF processing)

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Install Tesseract OCR:
   - **Windows**: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
   - **macOS**: `brew install tesseract`
   - **Linux**: `sudo apt-get install tesseract-ocr`

5. Install Poppler (for PDF support):
   - **Windows**: Download from [GitHub](https://github.com/oschwartz10612/poppler-windows/releases)
   - **macOS**: `brew install poppler`
   - **Linux**: `sudo apt-get install poppler-utils`

6. Run the Flask server:
```bash
python app.py
```

Backend will be available at `http://localhost:5000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

Frontend will be available at `http://localhost:3000`

## 📡 API Documentation

### POST /api/ocr

Upload and process documents for text extraction.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Body: file (image or PDF)

**Response:**
```json
{
  "success": true,
  "file_type": "pdf",
  "text": "Extracted text content...",
  "pages": 2,
  "page_texts": ["Page 1 text...", "Page 2 text..."],
  "original_filename": "certificate.pdf",
  "file_size": 1234567,
  "message": "Text extracted successfully from 2 pages"
}
```

### GET /

Health check endpoint returning server status.

## 🔧 Configuration

### Backend Configuration

Edit `backend/utils/ocr_processor.py` to customize OCR settings:

```python
# OCR configuration for better accuracy
self.ocr_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=...'
```

### Frontend Configuration

Create `frontend/.env.local` for custom API URL:

```env
NEXT_PUBLIC_API_URL=http://localhost:5000
```

## 🚀 Future Extensions

The application is designed to be easily extensible:

### Hash/QR Verification
- Add QR code detection and validation
- Implement document hash verification
- Digital signature validation

### Database Integration
- MongoDB integration for document storage
- Search and retrieval functionality
- Document categorization and tagging

### Admin Dashboard
- Document processing analytics
- User management and permissions
- Processing queue monitoring
- Alert system for failed processes

### Enhanced OCR
- OpenCV preprocessing integration
- Multiple OCR engine support
- Confidence scoring and validation
- Custom model training capabilities

## 🧪 Testing

### Backend Testing
```bash
cd backend
python -m pytest tests/
```

### Frontend Testing
```bash
cd frontend
npm test
```

## 📋 File Size Limits

- Maximum file size: 16MB
- Supported formats: PDF, PNG, JPG, JPEG, BMP, TIFF
- PDF pages are converted to 200 DPI images for processing

## 🐛 Troubleshooting

### Common Issues

1. **Tesseract not found**: Ensure Tesseract is installed and in PATH
2. **PDF processing fails**: Install Poppler utilities
3. **CORS errors**: Check backend CORS configuration
4. **File upload fails**: Verify file size is under 16MB

### Logs

Backend logs are available in the console when running in debug mode.

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make changes and add tests
4. Submit a pull request

## 📞 Support

For issues and questions, please create an issue in the GitHub repository.