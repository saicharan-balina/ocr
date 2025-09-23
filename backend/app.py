from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
from utils.ocr_processor import OCRProcessor
from utils.file_handler import save_uploaded_file, cleanup_file, UPLOAD_FOLDER

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all routes
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])

# Configure upload settings
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize OCR processor
ocr_processor = OCRProcessor()

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'Certificate OCR API is running',
        'version': '1.0.0'
    })

@app.route('/api/ocr', methods=['POST'])
def process_ocr():
    """Main OCR endpoint that accepts file uploads and returns extracted text"""
    try:
        # Check if file is present in request
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'error': 'No file provided',
                'message': 'Please select a file to upload'
            }), 400
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return jsonify({
                'success': False,
                'error': 'No file selected',
                'message': 'Please select a file to upload'
            }), 400
        
        # Save the uploaded file
        try:
            file_path, file_extension = save_uploaded_file(file, app.config['UPLOAD_FOLDER'])
            logger.info(f"File uploaded: {file.filename} -> {file_path}")
        except ValueError as e:
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'File upload failed'
            }), 400
        
        # Process the file with OCR
        try:
            result = ocr_processor.process_file(file_path, file_extension)
            
            # Add metadata
            result['original_filename'] = file.filename
            result['file_size'] = os.path.getsize(file_path)
            
            logger.info(f"OCR processing completed for {file.filename}")
            
            return jsonify(result)
            
        except Exception as e:
            logger.error(f"OCR processing error: {str(e)}")
            return jsonify({
                'success': False,
                'error': str(e),
                'message': 'OCR processing failed'
            }), 500
            
        finally:
            # Clean up uploaded file
            cleanup_file(file_path)
    
    except Exception as e:
        logger.error(f"Unexpected error in OCR endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': 'An unexpected error occurred'
        }), 500

@app.errorhandler(413)
def file_too_large(error):
    """Handle file size limit exceeded"""
    return jsonify({
        'success': False,
        'error': 'File too large',
        'message': 'File size exceeds 16MB limit'
    }), 413

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'error': 'Endpoint not found',
        'message': 'The requested endpoint does not exist'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle internal server errors"""
    return jsonify({
        'success': False,
        'error': 'Internal server error',
        'message': 'An unexpected error occurred'
    }), 500

if __name__ == '__main__':
    # Create upload directory if it doesn't exist
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    # Run the Flask app
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000
    )