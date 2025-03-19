from config.config import ALLOWED_EXTENSIONS
import os

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_file_size_kb(file_path):
    return round(os.path.getsize(file_path) / 1024, 2)
