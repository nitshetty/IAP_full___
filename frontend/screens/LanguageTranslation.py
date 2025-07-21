import streamlit as st
import requests
from utils.config import BACKEND_URL
from docx import Document
import io

def app():
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
    st.markdown("<h1 style='text-align:center;'>Language Translation</h1>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background-color:#1E1E1E; padding:15px; margin-bottom:20px; border-radius:10px; border-left:4px solid #4CAF50;'>
        <h3 style='color:#4CAF50; margin-top:0;'>📋 Use Case Description</h3>
        <p style='color:#CCCCCC; margin-bottom:10px;'> A company has operations in multiple countries and want to translate all their documents to multiple languages. The document have both text and images in them.</p>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("Step 1: Enter Languages")
    st.info("You can enter language names (e.g., English, French) or language codes (e.g., en, fr, es, de)")
    input_lang = st.text_input("Enter input language (e.g., English, es, fr, etc.)", key="input_lang_text")
    output_lang = st.text_input("Enter output language (e.g., French, en, de, etc.)", key="output_lang_text")

    st.subheader("Step 2: Upload or Enter Text")
    st.info("Please provide either text input OR upload a file, not both.")
    uploaded_file = st.file_uploader("Upload a document (.pdf, .docx, .txt)", type=["pdf", "docx", "txt"])
    text_input = st.text_area("Or enter text manually", key="language_translation_text_input")

    st.subheader("Step 3: Output Type")
    download_options = ["docx", "txt", "string"]
    download_format = st.selectbox("Select output type", options=download_options, key="output_type_select")

    if st.button("Translate"):
        # Validate that languages are provided
        if not input_lang.strip():
            st.error("Please enter the input language.")
            st.stop()
        
        if not output_lang.strip():
            st.error("Please enter the output language.")
            st.stop()
        
        # Validate that input and output languages are different
        if input_lang.strip().lower() == output_lang.strip().lower():
            st.error("Input language and output language cannot be the same.")
            st.stop()
        
        # Validate that user provides either text OR file, not both
        if uploaded_file and text_input.strip():
            st.error("Please provide either text input OR upload a file, not both.")
            st.stop()
        
        if not uploaded_file and not text_input.strip():
            st.error("Please provide either text input OR upload a file.")
            st.stop()

        # Validate download_format
        if download_format not in download_options:
            st.error("Invalid download option selected.")
            st.stop()

        token = st.session_state.get("access_token")
        if not token:
            st.error("Please login first.")
            st.stop()

        headers = {"Authorization": f"Bearer {token}"}
        response = None

        # file is uploaded
        if uploaded_file:
            files = {"file": uploaded_file}
            data = {
                "input_lang": input_lang,
                "output_lang": output_lang,
                "download_filetype": download_format
            }
            response = requests.post(f"{BACKEND_URL}/usecase/language-translation", data=data, files=files, headers=headers)
        else:
            payload = {
                "text_input": text_input,
                "input_lang": input_lang,
                "output_lang": output_lang,
                "download_filetype": download_format
            }
            response = requests.post(f"{BACKEND_URL}/usecase/language-translation", data=payload, headers=headers)

        if response is None:
            st.error("No response from backend.")
            st.stop()

        if response.status_code == 403:
            st.error("You do not have permission to access this service. Please check your license or role.")
        elif response.status_code == 200:
            content_type = response.headers.get("content-type", "")
            translated_text = ""
            download_label = None
            download_data = None
            download_filename = None
            download_mime = None

            if content_type.strip().lower() == "text/plain; charset=utf-8" or content_type.strip().lower().startswith("text/plain"):
                try:
                    translated_text = response.content.decode("utf-8")
                except Exception:
                    translated_text = "(Could not decode TXT file content)"
                download_label = "Download TXT"
                download_data = response.content
                download_filename = "translated_output.txt"
                download_mime = content_type

            elif content_type.strip().lower() == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                try:
                    doc = Document(io.BytesIO(response.content))
                    translated_text = "\n".join([para.text for para in doc.paragraphs])
                except Exception as e:
                    st.error(f"Could not decode DOCX file content: {e}")
                    translated_text = ""
                download_label = "Download DOCX"
                download_data = response.content
                download_filename = "translated_output.docx"
                download_mime = content_type

            else:
                # Fallback to JSON/text
                try:
                    result = response.json()
                except Exception:
                    result = None
                if result and "translated_text" in result:
                    translated_text = result.get("translated_text", "")
                else:
                    st.error("Unknown response format from backend.")
                    st.stop()

            # Show the translated text 
            if download_format == "string":
                st.subheader("Translated Output")
                st.text_area("Translated Text", translated_text, height=200)
            # Show download button 
            if download_label and download_data:
                st.download_button(
                    label=download_label,
                    data=download_data,
                    file_name=download_filename,
                    mime=download_mime
                )
        else:
            st.error(f"Translation failed: {response.text}")