from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
from PIL import Image
import datetime

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
    
    # processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    # model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-large")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-large")

    def generate_caption(image_path):
        """Generate a caption for the given image using BLIP with increased length."""
        image = Image.open(image_path).convert("RGB")
        inputs = processor(images=image, return_tensors="pt")
        
        # Generate caption with increased max_length and beam search
        out = model.generate(**inputs, max_length=50)
        
        # Decode and return the caption
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
        upload_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return render_template('result.html', image_url=file_path, caption=caption, upload_time=upload_time)
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

@app.route('/statistics')
def statistics():
    """Show application statistics."""
    total_files = len([f for f in os.listdir(UPLOAD_FOLDER) if allowed_file(f)])
    return render_template('statistics.html', total_files=total_files)

@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    """Collect user feedback."""
    if request.method == 'POST':
        user_feedback = request.form.get('feedback')
        feedback_file = os.path.join('static', 'feedback.txt')
        with open(feedback_file, 'a') as f:
            f.write(user_feedback + '\n')
        return redirect(url_for('thank_you'))
    return render_template('feedback.html')

@app.route('/thank-you')
def thank_you():
    """Render a thank-you page."""
    return render_template('thank_you.html')

if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    app.run(debug=True)
