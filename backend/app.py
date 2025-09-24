from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import logging
import json
from utils.ocr_processor import OCRProcessor
from utils.extractors import extract_fields, extract_qr_content
from utils.auth import require_api_key, AuthError
from db.store import CertificateStore
from utils.file_handler import save_uploaded_file, cleanup_file, UPLOAD_FOLDER
from typing import Optional
from bson import ObjectId

try:
    from PIL import Image  # type: ignore
except Exception:  # pragma: no cover
    Image = None  # type: ignore
try:
    import fitz  # type: ignore
except Exception:  # pragma: no cover
    fitz = None  # type: ignore

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JSONEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle MongoDB ObjectId and other special types."""
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)


# Initialize Flask app
app = Flask(__name__)
app.json_encoder = JSONEncoder

# Enable CORS for all routes with custom headers for admin auth
CORS(
    app,
    resources={
        r"/*": {
            "origins": [
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "http://192.168.29.115:3000",
                "*",
            ],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "X-API-Key"],
            "supports_credentials": False,
        }
    },
)

# Configure upload settings
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Initialize OCR processor and store
ocr_processor = OCRProcessor()

# Initialize MongoDB store
try:
    store = CertificateStore()
    if store.health_check():
        logger.info("✅ MongoDB connection established successfully")
        logger.info("🚀 Using professional MongoDB storage")
    else:
        raise Exception("MongoDB health check failed")
        
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {e}")
    logger.error("Please ensure MongoDB is running on localhost:27017")
    raise

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint with database status"""
    db_status = "connected" if store.health_check() else "disconnected"
    
    return jsonify({
        'status': 'healthy' if db_status == "connected" else 'degraded',
        'message': 'Certificate OCR API is running - Professional MongoDB Edition',
        'version': '2.0.0',
        'database': {
            'type': 'MongoDB',
            'status': db_status,
            'connection_string': 'mongodb://localhost:27017/'
        }
    })

@app.route('/api/ocr', methods=['POST', 'OPTIONS'])
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

@app.route('/api/import', methods=['POST', 'OPTIONS'])
def import_records():
    """Import certificate records in bulk for institutions.

    Body: { records: [ { certificate_id, name, roll_number, course, issue_date, issuer, hash, ... } ] }
    """
    try:
        # Allow CORS preflight without auth
        if request.method == 'OPTIONS':
            return ('', 204)
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


@app.route('/api/admin/stats', methods=['GET', 'OPTIONS'])
def admin_stats():
    try:
        if request.method == 'OPTIONS':
            return ('', 204)
        try:
            _ = require_api_key(request.headers)
        except AuthError as e:
            return jsonify({ 'success': False, 'error': str(e) }), 401
        return jsonify({ 'success': True, 'stats': store.stats() })
    except Exception as e:
        return jsonify({ 'success': False, 'error': str(e) }), 500


@app.route('/api/admin/records', methods=['GET', 'OPTIONS'])
def admin_list_records():
    try:
        if request.method == 'OPTIONS':
            return ('', 204)
        try:
            _ = require_api_key(request.headers)
        except AuthError as e:
            return jsonify({ 'success': False, 'error': str(e) }), 401
        admin = require_api_key(request.headers)
        limit = int(request.args.get('limit', '50'))
        offset = int(request.args.get('offset', '0'))
        items, total = store.list_records(limit=limit, offset=offset)
        issuer_id = admin.get('issuer_id')
        if issuer_id and issuer_id != '*':
            items = [r for r in items if r.get('issuer_id') == issuer_id]
        return jsonify({ 'success': True, 'total': total, 'items': items, 'limit': limit, 'offset': offset })
    except Exception as e:
        return jsonify({ 'success': False, 'error': str(e) }), 500


 


 


@app.route('/api/verify', methods=['POST', 'OPTIONS'])
def verify_certificate():
    """Verify a certificate via OCR text or provided fields.

    Accepts either:
      - file upload like /api/ocr (use same OCR path then match), or
      - JSON body with fields { certificate_id?, name?, roll_number?, course? }
    """
    try:
        qr_payload: Optional[str] = None
        qr_verified = False
        qr_id: Optional[str] = None
        qr_hash: Optional[str] = None
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

                # Try QR decode from first page/image
                try:
                    ext = (file_extension or '').lower()
                    if Image is not None:
                        if ext in ['jpg', 'jpeg', 'png', 'bmp', 'tiff']:
                            img = Image.open(file_path)
                            qr_payload = extract_qr_content(img)
                        elif ext == 'pdf' and fitz is not None:
                            with fitz.open(file_path) as doc:
                                if doc.page_count > 0:
                                    mat = fitz.Matrix(getattr(ocr_processor, 'pdf_zoom', 3.0), getattr(ocr_processor, 'pdf_zoom', 3.0))
                                    pix = doc[0].get_pixmap(matrix=mat, alpha=False)
                                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                                    qr_payload = extract_qr_content(img)
                    # attempt to parse fields from QR string
                    if qr_payload:
                        try:
                            import json, urllib.parse, re as _re
                            try:
                                obj = json.loads(qr_payload)
                                qr_id = obj.get('certificate_id') or obj.get('cert_id') or obj.get('id')
                                qr_hash = obj.get('file_hash') or obj.get('hash')
                            except Exception:
                                if '://' in qr_payload and '?' in qr_payload:
                                    qs = urllib.parse.urlparse(qr_payload).query
                                    qsd = dict(urllib.parse.parse_qsl(qs))
                                    qr_id = qsd.get('certificate_id') or qsd.get('cert_id') or qsd.get('id')
                                    qr_hash = qsd.get('file_hash') or qsd.get('hash')
                                if not qr_id:
                                    m = _re.search(r'[A-Za-z0-9\-/]{6,}', qr_payload)
                                    if m:
                                        qr_id = m.group(0)
                        except Exception:
                            pass
                except Exception:
                    qr_payload = None
            finally:
                cleanup_file(file_path)
        else:
            payload = request.get_json(force=True, silent=True) or {}
            cert_id = payload.get('certificate_id')
            roll = payload.get('roll_number')
            name = payload.get('name')
            course = payload.get('course')
            file_hash = payload.get('file_hash')
            qr_payload = payload.get('qr_payload')

        record = None
        matched_by = None
        # If QR provided and contains ID, prefer it
        if qr_payload and not cert_id and qr_id:
            cert_id = qr_id
            matched_by = 'qr'
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
        # determine qr_verified
        if record and qr_payload:
            try:
                rec_id = (record.get('certificate_id') or '').strip().lower()
                if qr_id and (qr_id or '').strip().lower() == rec_id:
                    qr_verified = True
                elif qr_hash and record.get('file_hash') and qr_hash == record.get('file_hash'):
                    qr_verified = True
            except Exception:
                qr_verified = False

        response = {
            'success': True,
            'verdict': verdict,
            'matched_by': matched_by,
            'record': record,
            'integrity': integrity,
            'observed_file_hash': file_hash,
            'qr_payload': qr_payload,
            'qr_verified': qr_verified if (qr_payload and record) else False,
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({ 'success': False, 'error': str(e) }), 500


@app.route('/api/register', methods=['POST', 'OPTIONS'])
def register_certificate_file():
    """Admin-only: register a certificate by uploading its file and metadata.

    Multipart form expected fields:
      - file: PDF/image
      - certificate_id, name, roll_number, course, issue_date, issuer, issuer_id (optional)
      - auto_ocr: '1' to run OCR and extract fields if not provided
    Computes file_hash (sha256) and stores with metadata.
    """
    try:
        if request.method == 'OPTIONS':
            return ('', 204)
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


@app.route('/api/stats', methods=['GET', 'OPTIONS'])
def stats_alias():
    # Alias to admin_stats for convenience
    return admin_stats()


# NOTE: Do NOT close the global MongoDB client per-request. It is shared across
# requests and will be closed on application shutdown in the __main__ block.


if __name__ == '__main__':
    # Ensure upload dir exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    try:
        # Start server after all routes are registered
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000
        )
    except KeyboardInterrupt:
        logger.info("Shutting down server...")
    except Exception as e:
        logger.error(f"Server error: {e}")
    finally:
        # Ensure database connection is closed
        if 'store' in globals():
            store.close_connection()
        logger.info("Application shutdown complete")