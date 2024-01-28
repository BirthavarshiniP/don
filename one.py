# app1.py

import streamlit as st
import auth_functions
from PyPDF2 import PdfReader
from transformers import T5ForConditionalGeneration, T5Tokenizer

# Load the T5 model and tokenizer
model = T5ForConditionalGeneration.from_pretrained('t5-small')
tokenizer = T5Tokenizer.from_pretrained('t5-small', legacy=False)

# Function to summarize text using T5 model
def summary_text(text, target_length=1000):
    # Target length of the summary in tokens
    target_length_tokens = target_length // 5  # Assuming an average token length of 5 characters

    inputs = tokenizer.encode("summarize: " + text, return_tensors="pt")

    # Generate the summary with constraints on length
    summary = model.generate(
        inputs,
        max_length=target_length_tokens + len(inputs[0]),
        min_length=target_length_tokens + len(inputs[0]) - 100,  # Allow some flexibility
        num_beams=5,
        length_penalty=2.0,
        early_stopping=True,
        no_repeat_ngram_size=2,  # Avoid repeating phrases
        top_k=50,  # Consider the top 50 words for each token during generation
        top_p=0.95,  # Consider the top 95% of the probability mass for each token during generation
    )

    summary_text = tokenizer.decode(summary[0], skip_special_tokens=True)
    return summary_text

# Function to extract text from a PDF
def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as f:
        reader = PdfReader(f)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    return text

# Main application logic
def main_app():
    st.set_page_config(layout="wide")

    choice = st.sidebar.selectbox("Select your choice", ["Summarize Text", "Summarize Document"])

    if choice == "Summarize Text":
        st.subheader("Summarize Text using T5 model")
        input_text = st.text_area("Enter your text here")
        if input_text is not None:
            if st.button("Summarize Text"):
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.markdown("**Your Input Text**")
                    st.info(input_text)
                with col2:
                    result = summary_text(input_text, target_length=1000)
                    st.markdown("**Summarize Text**")
                    st.success(result)

    elif choice == "Summarize Document":
        st.subheader("Summarize Document using T5 model")
        input_file = st.file_uploader("Upload your document", type=["pdf"])
        if input_file is not None:
            if st.button("Summarize Document"):
                with open("doc_file.pdf", "wb") as f:
                    f.write(input_file.getbuffer())
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.markdown("**Extracted Text from Document**")
                    extracted_text = extract_text_from_pdf("doc_file.pdf")
                    st.info(extracted_text)

                with col2:
                    # Split the text into chunks of 1000 words
                    chunk_size = 500
                    chunks = [extracted_text[i:i + chunk_size] for i in range(0, len(extracted_text), chunk_size)]

                    # Tokenize and summarize each chunk
                    summaries = []
                    for chunk in chunks:
                        chunk_summary = summary_text(chunk, target_length=100)
                        summaries.append(chunk_summary)

                    # Combine the summaries from each chunk
                    combined_summary = " ".join(summaries)
                    st.subheader("Summary")
                    st.success(combined_summary)

# Login page
def login_page():
    col1,col2,col3 = st.columns([1,2,1])

    # Authentication form layout
    do_you_have_an_account = col2.selectbox(label='Do you have an account?',options=('Yes','No','I forgot my password'))
    auth_form = col2.form(key='Authentication form',clear_on_submit=False)
    email = auth_form.text_input(label='Email')
    password = auth_form.text_input(label='Password',type='password') if do_you_have_an_account in {'Yes','No'} else auth_form.empty()
    auth_notification = col2.empty()

    # Sign In
    if do_you_have_an_account == 'Yes' and auth_form.form_submit_button(label='Sign In',use_container_width=True,type='primary'):
        with auth_notification, st.spinner('Signing in'):
            auth_functions.sign_in(email,password)

    # Create Account
    elif do_you_have_an_account == 'No' and auth_form.form_submit_button(label='Create Account',use_container_width=True,type='primary'):
        with auth_notification, st.spinner('Creating account'):
            auth_functions.create_account(email,password)

    # Password Reset
    elif do_you_have_an_account == 'I forgot my password' and auth_form.form_submit_button(label='Send Password Reset Email',use_container_width=True,type='primary'):
        with auth_notification, st.spinner('Sending password reset link'):
            auth_functions.reset_password(email)

    # Authentication success and warning messages
    if 'auth_success' in st.session_state:
        auth_notification.success(st.session_state.auth_success)
        del st.session_state.auth_success
    elif 'auth_warning' in st.session_state:
        auth_notification.warning(st.session_state.auth_warning)
        del st.session_state.auth_warning

# Main Streamlit app
def main():
    if 'user_info' not in st.session_state:
        login_page()
    else:

        # text summarizer page
        main_app()

        # Sign out
        st.header('Sign out:')
        st.button(label='Sign Out',on_click=auth_functions.sign_out,type='primary')

        # Delete Account
        st.header('Delete account:')
        password = st.text_input(label='Confirm your password',type='password')
        st.button(label='Delete Account',on_click=auth_functions.delete_account,args=[password],type='primary')

if __name__ == "__main__":
    main()
