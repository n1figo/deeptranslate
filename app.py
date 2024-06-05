import os
from PyPDF2 import PdfReader
import streamlit as st
from docx import Document
from io import BytesIO
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from langchain.callbacks import get_openai_callback

# OpenAI API key 설정
os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]

def process_text(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    embeddings = HuggingFaceEmbeddings(model_name='sentence-transformers/all-MiniLM-L6-v2')
    documents = FAISS.from_texts(chunks, embeddings)
    return documents

def translate_text(text, target_language="Korean"):
    try:
        llm = ChatOpenAI(model="gpt-4", temperature=0.0)
        trans_template = PromptTemplate(
            input_variables=['trans'],
            template=f'Your task is to translate this text to {target_language}: {{trans}}'
        )
        memory = ConversationBufferMemory(input_key='trans', memory_key='chat_history')
        trans_chain = LLMChain(llm=llm, prompt=trans_template, verbose=True, output_key='translate', memory=memory)
        response = trans_chain({'trans': text})
        return response['translate']
    except Exception as e:
        st.error(f"Translation error: {e}")
        return None

def pdf_to_text(file):
    try:
        pdf_reader = PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {e}")
        return None

def text_to_docx(text):
    doc = Document()
    doc.add_paragraph(text)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# Streamlit 앱 설정
st.title("📄PDF Translator")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
target_language = st.selectbox("Select target language:", ["Korean", "Japanese", "Chinese", "English"])

if uploaded_file is not None:
    text = pdf_to_text(uploaded_file)
    if text:
        st.write("Translating...")
        translated_text = translate_text(text, target_language)
        
        if translated_text:
            st.write("Translation complete!")
            docx_file = text_to_docx(translated_text)
            
            st.download_button(
                label="Download Translated DOCX",
                data=docx_file,
                file_name="translated.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

# if __name__ == '__main__':
#     main()
