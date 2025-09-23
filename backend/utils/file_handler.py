import os
from werkzeug.utils import secure_filename

# File upload configuration
UPLOAD_FOLDER = 'uploads'
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'tiff', 'pdf'}

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_extension(filename):
    """Get file extension from filename"""
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

def save_uploaded_file(file, upload_folder):
    """Save uploaded file securely and return the file path"""
    if not file or file.filename == '':
        raise ValueError("No file selected")
    
    if not allowed_file(file.filename):
        raise ValueError(f"File type not allowed. Supported types: {', '.join(ALLOWED_EXTENSIONS)}")
    
    # Create upload folder if it doesn't exist
    os.makedirs(upload_folder, exist_ok=True)
    
    # Secure the filename
    filename = secure_filename(file.filename)
    
    # Create unique filename to avoid conflicts
    import uuid
    unique_filename = f"{uuid.uuid4()}_{filename}"
    file_path = os.path.join(upload_folder, unique_filename)
    
    # Save the file
    file.save(file_path)
    
    return file_path, get_file_extension(filename)

def cleanup_file(file_path):
    """Remove uploaded file after processing"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Error cleaning up file {file_path}: {e}")