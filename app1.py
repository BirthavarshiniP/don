# app1.py

import streamlit as st
import auth_functions
from txtai.pipeline import Summary
from PyPDF2 import PdfReader

# Function to summarize text using txtai
@st.cache_resource
def summary_text(text):
    summary = Summary()
    result = summary(text)
    return result

# Function to extract text from a PDF
def extract_text_from_pdf(file_path):
    with open(file_path, 'rb') as f:
        reader = PdfReader(f)
        page = reader.pages[0]
        text = page.extract_text()
        return text

# Main application logic
def main_app():
    st.set_page_config(layout="wide")

    choice = st.sidebar.selectbox("Select your choice", ["Summarize Text", "Summarize Document"])

    if choice == "Summarize Text":
        st.subheader("Summarize Text using txtai")
        input_text = st.text_area("Enter your text here")
        if input_text is not None:
            if st.button("Summarize Text"):
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.markdown("**Your Input Text**")
                    st.info(input_text)
                with col2:
                    result = summary_text(input_text)
                    st.markdown("**Summarize Text**")
                    st.success(result)

    elif choice == "Summarize Document":
        st.subheader("Summarize Document using txtai")
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
                    result = extract_text_from_pdf("doc_file.pdf")
                    st.markdown("**Summarize Document**")
                    summary_result = summary_text(result)
                    st.success(summary_result)

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
    st.empty()
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
