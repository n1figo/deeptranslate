import streamlit as st
from pdfminer.high_level import extract_text
from docx import Document
import openai
import io


# API 키를 api_keys.json 파일에서 불러오기
with open('api_keys.json', 'r') as f:
    api_keys = json.load(f)
    openai.api_key = api_keys['api_key']
    

def translate_text(text, target_language="ko"):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"Translate the following text to {target_language}:\n\n{text}",
        max_tokens=2048
    )
    return response.choices[0].text.strip()

def pdf_to_text(file):
    return extract_text(file)

def text_to_docx(text):
    doc = Document()
    doc.add_paragraph(text)
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

st.title("PDF Translator")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file is not None:
    text = pdf_to_text(uploaded_file)
    st.write("Translating...")
    translated_text = translate_text(text)
    
    st.write("Translation complete!")
    docx_file = text_to_docx(translated_text)
    
    st.download_button(
        label="Download Translated DOCX",
        data=docx_file,
        file_name="translated.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
