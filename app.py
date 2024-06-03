import streamlit as st
from pdfminer.high_level import extract_text
from docx import Document
from openai import OpenAI
import io, os


# OpenAI 클라이언트 설정
client = OpenAI()

def translate_text(text, target_language="ko"):
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that translates text."},
                {"role": "user", "content": f"Translate the following text to {target_language}: {text}"}
            ],
            temperature=1,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        st.error(f"Translation error: {e}")
        return None

def pdf_to_text(file):
    try:
        return extract_text(file)
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return None

def text_to_docx(text):
    doc = Document()
    doc.add_paragraph(text)
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# Streamlit 앱 설정
st.title("PDF Translator")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    text = pdf_to_text(uploaded_file)
    if text:
        st.write("Translating...")
        # API 키 가져오기
        openai_api_key = st.secrets["OPENAI_API_KEY"]
        client.api_key = openai_api_key
        
        translated_text = translate_text(text)
        
        if translated_text:
            st.write("Translation complete!")
            docx_file = text_to_docx(translated_text)
            
            st.download_button(
                label="Download Translated DOCX",
                data=docx_file,
                file_name="translated.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )