import streamlit as st

def display_caption(caption, upload_time):
    st.markdown(
        f"""
        <div style="background-color:#f0f8ff; padding:20px; border-radius:12px; border: 2px solid #4CAF50;">
            <h3 style="color:#4CAF50; text-align:center;">✨ Generated Caption ✨</h3>
            <p style="font-size:22px; color:#333; text-align:center;"><strong>{caption}</strong></p>
            <p style="font-size:14px; text-align:center; color:gray;">Uploaded at {upload_time}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

def display_feedback(entry):
    st.markdown(
        f"""
        <div style='background-color: #f9f9f9; padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 1px solid #ddd;'>
            <p style='margin: 0;'><strong style='color: #4CAF50;'>{entry['name']}</strong> says:</p>
            <p style='margin: 5px 0 0 0; color: #333;'>{entry['feedback']}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
