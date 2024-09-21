import os

class Config:
    # Secret key for session management and cryptographic purposes
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'fallback_secret_key')

    # Configure upload folder (ensure it is set to the absolute path)
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')

    # Limit maximum file upload size (e.g., 16 MB)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
