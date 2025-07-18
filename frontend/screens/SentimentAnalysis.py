import streamlit as st
import requests
from utils.config import BACKEND_URL

import fitz  
from docx import Document


def extract_text_from_pdf(file):
    text = ""
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_text_from_docx(file):
    doc = Document(file)
    return "\n".join([para.text for para in doc.paragraphs])

def sentiment_analysis():
    st.markdown("<h1 style='text-align:center;'>Sentiment Analysis</h1>", unsafe_allow_html=True)
    st.markdown("""
    <div style='background-color:#1E1E1E; padding:15px; margin-bottom:20px; border-radius:10px; border-left:4px solid #4CAF50;'>
    <h3 style='color:#4CAF50; margin-top:0;'>📋 Use Case Description</h3>
    <p style='color:#CCCCCC; margin-bottom:10px;'>A client has large number of help desk data that they want to analyse and understand what is the general sentiment of the users. The sentiments can also be shown for different feedback categories. And % of the sentiments will be appreciated by the client.</p>
    </div>
    """, unsafe_allow_html=True)
    

    st.subheader("Step 1: Upload or Enter Text")
    uploaded_file = st.file_uploader("Upload a document (.pdf, .docx, .txt)", type=["pdf", "docx", "txt"], key="sentiment_analysis_file_uploader")
    text_input = st.text_area("Or enter text manually")

    combined_text = ""
    payload = {}

    # Refined logic to ensure only one field is included in the payload
    if uploaded_file:
        ext = uploaded_file.name.split(".")[-1].lower()
        if ext == "pdf":
            combined_text = extract_text_from_pdf(uploaded_file)
        elif ext == "docx":
            combined_text = extract_text_from_docx(uploaded_file)
        elif ext == "txt":
            combined_text = uploaded_file.read().decode("utf-8")
        else:
            st.error("Unsupported file type. Please upload a .pdf, .docx, or .txt file.")
            return
        if not combined_text.strip():
            st.warning("No text could be extracted from the uploaded file. Please upload a file with selectable text.")
            return
        payload = {"file": uploaded_file}
    elif text_input:
        combined_text = text_input
        payload = {"text_input": combined_text}
    else:
        st.error("Please provide valid input.")
        return

    st.subheader("Step 2: Analyze")

    if st.button("Analyze Mixed Sentiment"):
        if not combined_text.strip():
            st.warning("Please enter valid text or upload a file with selectable text.")
            return

        token = st.session_state.get("access_token")
        if not token:
            st.error("Please login first.")
            return

        headers = {"Authorization": f"Bearer {token}"}
        payload = {"text_input": combined_text}

        response = requests.post(f"{BACKEND_URL}/usecase/sentiment-analysis", data=payload, headers=headers)

        if response.status_code == 403:
            st.error("You do not have permission to access this service. Please check your license or role.")
        elif response.status_code == 200:
            results = response.json()
            st.subheader("Sentiment Analysis Results")
            if isinstance(results, list):
                for idx, result in enumerate(results):
                    summary = result.get("summary", "Unknown")
                    percentages = result.get("percentage", {})
                    st.success(f"Entry {idx + 1}: {summary}")
                    st.write(f"Percentages: {percentages}")
            else:
                summary = results.get("summary", "Unknown")
                percentages = results.get("percentage", {})
                st.success(f"Summary: {summary}")
                st.write(f"Percentages: {percentages}")
        else:
            st.error(f"Sentiment analysis failed: {response.text}")

def app():
    sentiment_analysis()

