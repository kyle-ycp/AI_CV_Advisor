import streamlit as st
import pdfplumber
import docx2txt
from io import BytesIO
import pdfkit
import markdown
from chatbot import generate_chat_completion
import os
import subprocess

os.environ['PATH'] += ':/usr/bin'

# Set app icon and title
st.set_page_config(page_title="AI-Powered CV Analyzer", page_icon="📄")

def extract_text_from_file(uploaded_file):
    if uploaded_file.type == "application/pdf":
        with pdfplumber.open(uploaded_file) as pdf:
            text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])
    elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        text = docx2txt.process(uploaded_file)
    else:
        text = "Unsupported file format. Please upload a PDF or DOCX."
    return text

def generate_pdf(markdown_text):
    # Convert Markdown to HTML
    options = {
    'page-size': 'A4',
    'margin-top': '10mm',
    'margin-right': '10mm',
    'margin-bottom': '10mm',
    'margin-left': '10mm',
    }

    html_text = markdown.markdown(markdown_text)
    config = pdfkit.configuration(wkhtmltopdf="/wkhtmltopdf/bin/wkhtmltopdf.exe")  # Adjust path as necessary
    pdf_data = pdfkit.from_string(html_text, False,options=options, configuration=config)

    return pdf_data


# Streamlit UI
st.title("AI-Powered CV Analyzer")
st.write(os.environ['PATH'])

try:
    result = subprocess.run(['wkhtmltopdf', '--version'], capture_output=True, text=True)
    st.write("wkhtmltopdf is accessible:", result.stdout)
except FileNotFoundError:
    st.write("wkhtmltopdf not found in the environment.")

uploaded_file = st.file_uploader("Upload your CV (PDF or DOCX)", type=["pdf", "docx"])

# # Job Details Section
# st.subheader("Job Details (If applicable)")
# job_url = st.text_input("Enter the job listing URL (LinkedIn, company website, etc.):")
# if job_url:
#     st.write(f"You entered: {job_url}")

if uploaded_file:
    st.subheader("Extracted Text:")
    cv_text = extract_text_from_file(uploaded_file)
    st.text_area("CV Content", cv_text, height=300)

    # Initialize session state for advice and new CV text
    if 'advice_text' not in st.session_state:
        st.session_state.advice_text = ""
    if 'new_cv_text' not in st.session_state:
        st.session_state.new_cv_text = ""
    
    if st.button("Analyze CV") or st.session_state.advice_text != "":
        # st.write("**AI Analysis & Recommendations Coming Soon...**")
        prompt = f"""Imgine you are a professional career advisor, please comment on the below CV content.
                    Please ignore format issue at this moment as it is just the content.
                    Please summarise the advice and reponse within 200 words. 
                    CV: {cv_text} """
        st.session_state.advice_text = generate_chat_completion(prompt).content

        st.subheader("AI Analysis & Recommendations")
        st.write(st.session_state.advice_text)

        if st.button("Generate Revised CV") or st.session_state.new_cv_text != "":
            prompt = f"""
                        Imagine you are a professional career advisor. 
                        Please help to revise the given CV, paying attention to the format. 
                        Generate the revised CV only, without any additional comments.
                        CV: {cv_text}
                    """
            st.session_state.new_cv_text = generate_chat_completion(prompt).content

            # editable_cv = st.text_area("Edit CV", st.session_state.new_cv_text, height=600)
            editable_cv = st.session_state.new_cv_text
            st.subheader("Preview")
            st.markdown(editable_cv)

            # st.write("**AI-Generated CV Coming Soon...**")
            pdf_data = generate_pdf(editable_cv)
            st.download_button(label="Download", data=pdf_data, file_name="Revised_CV.pdf", mime="application/pdf")
        
        if st.button("Generate Cover Letter"):
            st.write("**AI-Generated Cover Letter Coming Soon...**")
