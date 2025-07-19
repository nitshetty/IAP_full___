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
    </div>    """, unsafe_allow_html=True)
    
    st.subheader("Step 1: Upload or Enter Text")
    st.info("Please provide either text input OR upload a file, not both.")
    uploaded_file = st.file_uploader("Upload a document (.pdf, .docx, .txt)", type=["pdf", "docx", "txt"], key="sentiment_analysis_file_uploader")
    text_input = st.text_area("Or enter text manually")

    st.subheader("Step 2: Analyze")

    if st.button("Analyze Mixed Sentiment"):
        # Validate that user provides either text OR file, not both
        if uploaded_file and text_input.strip():
            st.error("Please provide either text input OR upload a file, not both.")
            return
        
        if not uploaded_file and not text_input.strip():
            st.error("Please provide either text input OR upload a file.")
            return

        combined_text = ""

        # Process uploaded file
        if uploaded_file:
            ext = uploaded_file.name.split(".")[-1].lower()
            if ext == "pdf":
                try:
                    combined_text = extract_text_from_pdf(uploaded_file)
                except Exception as e:
                    st.error(f"Error reading PDF file: {e}")
                    return
            elif ext == "docx":
                try:
                    combined_text = extract_text_from_docx(uploaded_file)
                except Exception as e:
                    st.error(f"Error reading DOCX file: {e}")
                    return
            elif ext == "txt":
                try:
                    combined_text = uploaded_file.read().decode("utf-8")
                except Exception as e:
                    st.error(f"Error reading TXT file: {e}")
                    return
            else:
                st.error("Unsupported file type. Please upload a .pdf, .docx, or .txt file.")
                return
            
            if not combined_text.strip():
                st.error("No text could be extracted from the uploaded file. Please upload a file with readable text.")
                return
        else:
            # Use text input
            combined_text = text_input.strip()

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

