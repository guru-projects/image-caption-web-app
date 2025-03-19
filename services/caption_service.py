import os
import datetime
from PIL import Image
from models.caption_model import generate_caption
from database.db_handler import load_metadata, save_metadata
from config.config import UPLOAD_FOLDER

def process_image_upload(uploaded_file):
    filename = uploaded_file.name
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    image = Image.open(file_path).convert("RGB")
    caption = generate_caption(image)
    
    upload_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    metadata = load_metadata()
    metadata[filename] = {
        "caption": caption,
        "upload_time": upload_time
    }
    save_metadata(metadata)
    
    return filename, file_path, caption, upload_time
