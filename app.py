import streamlit as st
import os
from config.config import UPLOAD_FOLDER
from utils.file_utils import allowed_file, get_file_size_kb
from utils.ui_components import display_caption, display_feedback
from services.caption_service import process_image_upload
from services.feedback_service import submit_feedback, get_all_feedback
from database.db_handler import load_metadata, remove_image_metadata
import pandas as pd

# Setup folders
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

st.title("🖼️ Image Captioning Web Application")

# Sidebar navigation
st.sidebar.title("Navigation")
tabs = ["Home", "Gallery", "Statistics", "Feedback"]
icons = ["🏠", "🖼️", "📊", "💬"]

if "page" not in st.session_state:
    st.session_state.page = "Home"

for i, tab in enumerate(tabs):
    if st.sidebar.button(f"{icons[i]} {tab}", key=tab):
        st.session_state.page = tab

# Home Page
if st.session_state.page == "Home":
    st.header("Upload an Image")
    uploaded_file = st.file_uploader("Choose an image...", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        if allowed_file(uploaded_file.name):
            filename, file_path, caption, upload_time = process_image_upload(uploaded_file)

            st.image(file_path, caption="Uploaded Image", use_container_width=True, width=600)
            display_caption(caption, upload_time)
        else:
            st.error("Invalid file type.")

# Gallery Page
elif st.session_state.page == "Gallery":
    st.header("🖼️ Image Gallery")
    metadata = load_metadata()
    image_files = [f for f in os.listdir(UPLOAD_FOLDER) if allowed_file(f)]

    if image_files:
        for image_file in image_files:
            image_path = os.path.join(UPLOAD_FOLDER, image_file)
            image_data = metadata.get(image_file, {})
            caption = image_data.get("caption", "No caption available")
            upload_time = image_data.get("upload_time", "Unknown upload time")

            col1, col2 = st.columns([1, 2])

            with col1:
                st.image(image_path, caption=image_file, use_container_width=True)

            with col2:
                st.markdown(
                    f"""
                    <div style="padding:15px; border-radius:10px; border: 1px solid #ccc; margin-bottom:15px">
                        <h4 style="color:#4CAF50;">📝 Caption:</h4>
                        <p style="font-size:18px; color:#ccc;"><strong>{caption}</strong></p>
                        <p style="color:gray; font-size:12px;">Uploaded at: {upload_time}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                if st.button(f"🗑️ Delete {image_file}", key=f"delete_{image_file}"):
                    os.remove(image_path)
                    remove_image_metadata(image_file)
                    st.success(f"Deleted {image_file}")
                    st.rerun()
    else:
        st.info("No images uploaded yet.")

# Statistics Page
elif st.session_state.page == "Statistics":
    st.header("📊 Application Statistics")
    metadata = load_metadata()
    total_files = len(metadata)

    st.write(f"**Total Uploaded Images:** {total_files}")

    if total_files > 0:
        df_data = []
        for filename, data in metadata.items():
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.exists(file_path):
                df_data.append({
                    "Filename": filename,
                    "Upload Time": data.get("upload_time", "N/A"),
                    "File Size": f"{get_file_size_kb(file_path)} KB",
                    "Caption": data.get("caption", "N/A")
                })

        df = pd.DataFrame(df_data)
        st.dataframe(df)
    else:
        st.info("No statistics to show.")

# Feedback Page
elif st.session_state.page == "Feedback":
    st.header("💬 User Feedback")

    name = st.text_input("Your Name")
    feedback = st.text_area("Your Feedback")

    if st.button("Submit Feedback"):
        if name.strip() == "" or feedback.strip() == "":
            st.warning("Fill both fields.")
        else:
            submit_feedback(name, feedback)
            st.success("Feedback submitted!")
            st.balloons()

    st.subheader("📋 Previous Feedback")
    feedback_entries = get_all_feedback()

    if feedback_entries:
        for entry in feedback_entries:
            display_feedback(entry)
    else:
        st.info("No feedback submitted yet.")
