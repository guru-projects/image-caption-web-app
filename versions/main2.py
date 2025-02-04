from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
from PIL import Image

# Initialize the Flask app
app = Flask(__name__)

# Define the upload folder and allowed extensions
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

try:
    import torch
    from transformers import BlipProcessor, BlipForConditionalGeneration

    # Load BLIP model and processor
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

    def generate_caption(image_path):
        """Generate a caption for the given image using BLIP."""
        image = Image.open(image_path).convert("RGB")
        inputs = processor(images=image, return_tensors="pt")
        out = model.generate(**inputs)
        caption = processor.decode(out[0], skip_special_tokens=True)
        return caption

except ImportError:
    torch = None
    def generate_caption(image_path):
        """Fallback for missing AI libraries."""
        return "Error: PyTorch and Transformers libraries are not available."

# Workaround to handle multiprocessing issue in restricted environments
def workaround_multiprocessing():
    try:
        import multiprocessing as mp
        mp.get_start_method()  # Check or initialize a valid multiprocessing start method
    except ImportError:
        pass
    except RuntimeError:
        pass  # Handle cases where get_start_method fails due to restrictions

workaround_multiprocessing()

def allowed_file(filename):
    """Check if the uploaded file is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Render the main page."""
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Handle image upload and caption generation."""
    if 'file' not in request.files:
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        return redirect(request.url)

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        caption = generate_caption(file_path)
        return render_template('result.html', image_url=file_path, caption=caption)
    else:
        return redirect(request.url)

# Additional routes for enhancing the application
@app.route('/about')
def about():
    """Render the about page."""
    return render_template('about.html')

@app.route('/gallery')
def gallery():
    """Render a gallery page with previously uploaded images."""
    image_files = [os.path.join(UPLOAD_FOLDER, f) for f in os.listdir(UPLOAD_FOLDER) if allowed_file(f)]
    return render_template('gallery.html', images=image_files)

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    """Delete an uploaded file."""
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
    return redirect(url_for('gallery'))

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
