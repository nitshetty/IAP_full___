import streamlit as st
import requests
from PIL import Image
import io
from utils.config import BACKEND_URL

def app():
    image_classification()
    
def image_classification():
    col_spacer, col_service, col_logout = st.columns([7, 2, 1])
    with col_service:
        if st.button("Go to Service Selection", key="go_service_selection"):
            st.session_state.page = "ServiceSelection"
            st.rerun()
    with col_logout:
        if st.button("Logout", key="logout_btn"):
            st.session_state.authenticated = False
            st.session_state.user_email = None
            st.session_state.access_token = None
            st.session_state.page = "Login"
            st.rerun()
    st.markdown("<h1 style='text-align:center;'>Image Classification</h1>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background-color:#1E1E1E; padding:15px; margin-bottom:20px; border-radius:10px; border-left:4px solid #4CAF50;'>
    <h3 style='color:#4CAF50; margin-top:0;'>📋 Use Case Description</h3>
    <p style='color:#CCCCCC; margin-bottom:10px;'>A wholesale food company wants to classify their product images – name of the food and categorise under food/beverage.</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Step 1: Upload Image")
    # file type restriction to allow all files to be uploaded
    uploaded_image = st.file_uploader("Upload an image", key="image_upload")

    if uploaded_image:
        # Check MIME type of the uploaded file
        if uploaded_image.type not in ["image/jpeg", "image/png"]:
            st.error("Only .jpg and .png formats are supported.")
            return

        # Validate file size (max 10MB)
        uploaded_image.seek(0)
        file_size = len(uploaded_image.read())
        uploaded_image.seek(0)
        
        if file_size == 0:
            st.error("Uploaded image is empty.")
            return
        
        if file_size > 10 * 1024 * 1024:  # 10MB limit
            st.error("Image file is too large. Please upload an image smaller than 10MB.")
            return

        # Ensure the file is sent as multipart/form-data
        files = {"file": (uploaded_image.name, uploaded_image, uploaded_image.type)}        # Show uploaded image preview
        try:
            st.image(Image.open(io.BytesIO(uploaded_image.read())), caption="Uploaded Image", use_container_width=True)
            uploaded_image.seek(0)  # Reset file pointer for the request
        except Exception as e:
            st.error(f"Error displaying image: {e}")
            return

        st.subheader("Step 2: Classify Image")

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

# Streamlit page renders by calling the main function
image_classification()