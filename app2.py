import streamlit as st
import os
from PIL import Image
import datetime
from werkzeug.utils import secure_filename
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration

# Define the upload folder and allowed extensions
UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load BLIP model and processor
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

def allowed_file(filename):
    """Check if the uploaded file is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Streamlit app
st.title("Image Captioning Web Application")

# Sidebar for navigation
st.sidebar.title("Navigation")

tabs = ["Home", "Gallery", "Statistics", "Feedback"]
icons = ["🏠", "🖼️", "📊", "💬"]

if "page" not in st.session_state:
    st.session_state.page = "Home"

for i, tab in enumerate(tabs):
    if st.sidebar.button(f"{icons[i]} {tab}", key=tab):
        st.session_state.page = tab

if st.session_state.page == "Home":
    st.header("Upload an Image")
    uploaded_file = st.file_uploader("Choose an image...", type=["png", "jpg", "jpeg"])
    
    if uploaded_file is not None:
        if allowed_file(uploaded_file.name):
            filename = secure_filename(uploaded_file.name)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            st.image(file_path, caption="Uploaded Image", use_container_width=True, width=600)
            
            caption = generate_caption(file_path)
            upload_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            st.subheader("**Caption:**")
            st.write(caption)
            st.write("**Upload Time:**", upload_time)
        else:
            st.error("File type not allowed. Please upload a PNG, JPG, or JPEG file.")

elif st.session_state.page == "Gallery":
    st.header("Image Gallery")
    image_files = [f for f in os.listdir(UPLOAD_FOLDER) if allowed_file(f)]

    if "gallery_rerun" not in st.session_state:
        st.session_state.gallery_rerun = 0  # Initialize to an integer

    if image_files:
        for image_file in image_files:
            image_path = os.path.join(UPLOAD_FOLDER, image_file)
            st.image(image_path, caption=image_file, use_container_width=True, width=600)

            if st.button(f"Delete {image_file}"):
                os.remove(image_path)
                st.success(f"Deleted {image_file}")
                st.session_state.gallery_rerun += 1  # Increment the counter
                st.rerun()  # Trigger rerun using st.rerun()

    else:
        st.write("No images uploaded yet.")

elif st.session_state.page == "Statistics":
    st.header("Application Statistics")
    total_files = len([f for f in os.listdir(UPLOAD_FOLDER) if allowed_file(f)])
    st.write(f"**Total Uploaded Images:** {total_files}")

elif st.session_state.page == "Feedback":
    st.header("User Feedback")
    user_feedback = st.text_area("Please provide your feedback here:")
    
    if st.button("Submit Feedback"):
        feedback_file = os.path.join('static', 'feedback.txt')
        with open(feedback_file, 'a') as f:
            f.write(user_feedback + '\n')
        st.success("Thank you for your feedback!")
        st.balloons()
