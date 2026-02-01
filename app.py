import streamlit as st
from PIL import Image
import os

from main import add_known_face, run_detection

st.set_page_config(page_title="HATSS", layout="centered")

st.title("🏠 HATSS – Smart Security System")

st.header("Step 1: Add Known People")
known_file = st.file_uploader(
    "Upload image of a trusted person",
    type=["jpg", "jpeg", "png"],
    key="known"
)

if known_file:
    img = Image.open(known_file)
    st.image(img, caption="Known Person", use_column_width=True)

    img.save("known_temp.jpg")
    success = add_known_face("known_temp.jpg")
    os.remove("known_temp.jpg")

    if success:
        st.success("Known face added successfully")
    else:
        st.error("No face detected")

st.divider()

st.header("Step 2: Detect Intrusion")
test_file = st.file_uploader(
    "Upload image to test",
    type=["jpg", "jpeg", "png"],
    key="test"
)

if test_file:
    img = Image.open(test_file)
    st.image(img, caption="Detected Person", use_column_width=True)

    img.save("test_temp.jpg")
    result = run_detection("test_temp.jpg")
    os.remove("test_temp.jpg")

    if result == "Known":
        st.success("✅ Known person – no alert")
    elif result == "Unknown":
        st.error("🚨 Unknown person detected – ALERT")
    else:
        st.warning(result)
