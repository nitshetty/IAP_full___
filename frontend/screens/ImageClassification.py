import streamlit as st
import requests
from PIL import Image
import io
from utils.config import BACKEND_URL

def app():
    image_classification()
    
def image_classification():
    st.markdown("<h1 style='text-align:center;'>Image Classification</h1>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background-color:#1E1E1E; padding:15px; margin-bottom:20px; border-radius:10px; border-left:4px solid #4CAF50;'>
    <h3 style='color:#4CAF50; margin-top:0;'>📋 Use Case Description</h3>
    <p style='color:#CCCCCC; margin-bottom:10px;'>A wholesale food company wants to classify their product images – name of the food and categorise under food/beverage.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Removed file type restriction to allow all files to be uploaded
    uploaded_image = st.file_uploader("Upload an image", key="image_upload")

    if uploaded_image:
        # Check MIME type of the uploaded file
        if uploaded_image.type not in ["image/jpeg", "image/png"]:
            st.error("Only .jpg and .png formats are supported.")
            return

        # Ensure the file is sent as multipart/form-data
        uploaded_image.seek(0)  # Reset file pointer to the beginning
        files = {"file": (uploaded_image.name, uploaded_image, uploaded_image.type)}

        # Show uploaded image preview
        st.image(Image.open(io.BytesIO(uploaded_image.read())), caption="Uploaded Image", use_container_width=True)
        uploaded_image.seek(0)  # Reset file pointer again for the request

        # Validate file content before previewing
        uploaded_image.seek(0)
        if len(uploaded_image.read()) <= 7:
            st.error("Uploaded image is invalid or empty.")
            return
        uploaded_image.seek(0)  # Reset file pointer again

        if st.button("Classify"):
            token = st.session_state.get("access_token")
            if not token:
                st.error("You must log in first.")
                return

            headers = {"Authorization": f"Bearer {token}"}

            # Updated API request to use files parameter for multipart/form-data
            response = requests.post(f"{BACKEND_URL}/usecase/image-classification", files=files, headers=headers)

            if response.status_code == 403:
                st.error("You do not have permission to access this service. Please check your license or role.")
            elif response.status_code == 400:
                st.error(response.json().get("detail", "Invalid input. Please check your file."))
            elif response.status_code == 200:
                result = response.json()

                # Iterate over the list of results and display product_name and category
                st.subheader("Classification Results")
                for item in result:
                    product_name = item.get("product_name", "Unknown")
                    category = item.get("category", "Unknown")
                    st.success(f"Product Name: {product_name}, Category: {category}")
            else:
                st.error(f"Image classification failed: {response.text}")

# Ensure the Streamlit page renders by calling the main function
image_classification()