from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
from utils.ocr_processor import OCRProcessor
from utils.extractors import extract_fields
from utils.auth import require_api_key, AuthError
from db.store import CertificateStore
from utils.file_handler import save_uploaded_file, cleanup_file, UPLOAD_FOLDER

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for all routes with custom headers for admin auth
CORS(
    app,
    origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_headers=["Content-Type", "X-API-Key"],
    methods=["GET", "POST", "OPTIONS"],
)

# Configure upload settings
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize OCR processor and store
ocr_processor = OCRProcessor()
store = CertificateStore()

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

            # Simple field extraction from combined text (for prototype)
            combined = result.get('text') or ''
            fields = extract_fields(combined)
            result['extracted_fields'] = fields
            
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

 

# -----------------------
# Prototype verification APIs
# -----------------------

@app.route('/api/import', methods=['POST'])
def import_records():
    """Import certificate records in bulk for institutions.

    Body: { records: [ { certificate_id, name, roll_number, course, issue_date, issuer, hash, ... } ] }
    """
    try:
        # admin auth
        try:
            admin = require_api_key(request.headers)
        except AuthError as e:
            return jsonify({ 'success': False, 'error': str(e) }), 401
        data = request.get_json(force=True, silent=True) or {}
        records = data.get('records') or []
        if not isinstance(records, list):
            return jsonify({ 'success': False, 'error': 'records must be a list' }), 400
        # Stamp issuer_id from admin context if scoped
        issuer_id = admin.get('issuer_id')
        stamped = []
        for r in records:
            r = dict(r)
            if issuer_id and issuer_id != '*':
                r.setdefault('issuer_id', issuer_id)
            stamped.append(r)
        summary = store.import_records(stamped)
        return jsonify({ 'success': True, 'summary': summary })
    except Exception as e:
        return jsonify({ 'success': False, 'error': str(e) }), 500


 


 


@app.route('/api/verify', methods=['POST'])
def verify_certificate():
    """Verify a certificate via OCR text or provided fields.

    Accepts either:
      - file upload like /api/ocr (use same OCR path then match), or
      - JSON body with fields { certificate_id?, name?, roll_number?, course? }
    """
    try:
        if request.files.get('file'):
            # Reuse OCR pipeline
            file = request.files['file']
            if file.filename == '':
                return jsonify({ 'success': False, 'error': 'No file selected' }), 400
            file_path, file_extension = save_uploaded_file(file, app.config['UPLOAD_FOLDER'])
            try:
                result = ocr_processor.process_file(file_path, file_extension)
                combined = result.get('text') or ''
                fields = extract_fields(combined)
                cert_id = fields.get('certificate_id')
                roll = fields.get('roll_number')
                name = fields.get('name')
                course = fields.get('course')
                # Compute file hash for integrity
                try:
                    with open(file_path, 'rb') as f:
                        file_bytes = f.read()
                    file_hash = store.sha256(file_bytes)
                except Exception:
                    file_hash = None
            finally:
                cleanup_file(file_path)
        else:
            payload = request.get_json(force=True, silent=True) or {}
            cert_id = payload.get('certificate_id')
            roll = payload.get('roll_number')
            name = payload.get('name')
            course = payload.get('course')
            file_hash = payload.get('file_hash')

        record = None
        matched_by = None
        if cert_id:
            record = store.get_by_certificate_id(cert_id)
            matched_by = 'certificate_id'
        if not record:
            record = store.find_candidate(name=name, roll=roll, course=course)
            if record:
                matched_by = 'fields'

        verdict = 'valid' if record else 'not_found'
        integrity = 'unknown'
        if record and file_hash and record.get('file_hash'):
            integrity = 'match' if record.get('file_hash') == file_hash else 'mismatch'
        response = {
            'success': True,
            'verdict': verdict,
            'matched_by': matched_by,
            'record': record,
            'integrity': integrity,
            'observed_file_hash': file_hash
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({ 'success': False, 'error': str(e) }), 500


@app.route('/api/register', methods=['POST'])
def register_certificate_file():
    """Admin-only: register a certificate by uploading its file and metadata.

    Multipart form expected fields:
      - file: PDF/image
      - certificate_id, name, roll_number, course, issue_date, issuer, issuer_id (optional)
      - auto_ocr: '1' to run OCR and extract fields if not provided
    Computes file_hash (sha256) and stores with metadata.
    """
    try:
        try:
            admin = require_api_key(request.headers)
        except AuthError as e:
            return jsonify({ 'success': False, 'error': str(e) }), 401

        if 'file' not in request.files:
            return jsonify({ 'success': False, 'error': 'No file provided' }), 400
        file = request.files['file']
        if not file.filename:
            return jsonify({ 'success': False, 'error': 'Empty filename' }), 400

        file_path, file_extension = save_uploaded_file(file, app.config['UPLOAD_FOLDER'])
        try:
            with open(file_path, 'rb') as f:
                file_bytes = f.read()
            file_hash = store.sha256(file_bytes)

            record = {
                'certificate_id': (request.form.get('certificate_id') or '').strip(),
                'name': request.form.get('name'),
                'roll_number': request.form.get('roll_number'),
                'course': request.form.get('course'),
                'issue_date': request.form.get('issue_date'),
                'issuer': request.form.get('issuer'),
                'issuer_id': request.form.get('issuer_id') or (admin.get('issuer_id') if admin.get('issuer_id') != '*' else None),
                'file_hash': file_hash,
                'file_name': file.filename,
                'file_ext': file_extension,
            }

            # Optionally OCR to auto-fill missing fields
            if request.form.get('auto_ocr') == '1':
                try:
                    ocr_result = ocr_processor.process_file(file_path, file_extension)
                    combined = ocr_result.get('text') or ''
                    auto_fields = extract_fields(combined)
                    for k, v in auto_fields.items():
                        if not record.get(k) and v:
                            record[k] = v
                except Exception:
                    pass

            inserted, stored = store.upsert_record(record)
            # log registration
            store.log_verification({
                'type': 'registration',
                'admin_role': admin.get('role'),
                'issuer_id': admin.get('issuer_id'),
                'certificate_id': record.get('certificate_id'),
                'file_hash': file_hash,
                'inserted': inserted,
            })

            return jsonify({ 'success': True, 'inserted': inserted, 'record': stored })
        finally:
            cleanup_file(file_path)
    except Exception as e:
        return jsonify({ 'success': False, 'error': str(e) }), 500


if __name__ == '__main__':
    # Ensure upload dir exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    # Start server after all routes are registered
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000
    )