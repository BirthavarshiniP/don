import streamlit as st
from txtai.pipeline import Summary
from PyPDF2 import PdfReader

st.set_page_config(layout="wide")

@st.cache_resource
def summary_text(text):
    summary = Summary()
    text = (text)
    result = summary(text)
    return result

def extract_text_from_pdf(file_path):
   with open(file_path, 'rb') as f:
      reader = PdfReader(f)
      page = reader.pages[0]
      text = page.extract_text()
      return text 
    

choice = st.sidebar.selectbox("Select your choice", ["Summarize Text", "Summarize Document"])

if choice == "Summarize Text":
    st.subheader("Summarize Text using txtai")
    input_text = st.text_area("Enter your text here")
    if input_text is not None:
     if st.button("Summarize Text"):
         col1, col2 = st.columns([1,1])
         with col1:
            st.markdown("**Your Input Text**")
            st.info(input_text)
         with col2:
            result = summary_text(input_text)
            st.markdown("**Summarize Text**")
            st.success(result)


elif choice == "Summarize Document":
    st.subheader("Summarize Document using txtai")
    input_file = st.file_uploader("Upload uou doucment", type = ["pdf"])
    if input_file is not None:
        if st.button("Summarize Document"):  
            with open("doc_file.pdf", "wb") as f:
              f.write(input_file.getbuffer())
            col1, col2 = st.columns([1,1])
            with col1:
                 st.markdown("**Extracted Text from Document**")
                 extracted_text = extract_text_from_pdf("doc_file.pdf")
                 st.info(extracted_text)

            with col2:
                result = extract_text_from_pdf("doc_file.pdf")
                st.markdown("**Summarize Document**")
                summary_result = summary_text(result)
                st.success(summary_result)