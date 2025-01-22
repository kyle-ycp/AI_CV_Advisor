import streamlit as st
import pdfplumber
import docx2txt
from pdf2image import convert_from_bytes
from io import BytesIO
import pdfkit
import markdown
from chatbot import generate_chat_completion
import os

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
    config = pdfkit.configuration()  # Adjust path as necessary
    pdf_data = pdfkit.from_string(html_text, False,options=options, configuration=config)

    return pdf_data

def convert_pdf_to_image(pdf_data):
    # Convert PDF bytes to images
    images = convert_from_bytes(pdf_data)
    return images

# Streamlit UI
st.title("AI-Powered CV Analyzer")

uploaded_file = st.file_uploader("You can upload your current CV (PDF or DOCX)", type=["pdf", "docx"])

# Display uploaded file information
if uploaded_file is not None:
    st.success(f"File '{uploaded_file.name}' uploaded successfully!")

# Additional Inputs
st.subheader("Additional Information")
with st.expander("Provide additional context (optional)"):
    job_url = st.text_input("Enter the job listing URL (LinkedIn, company website, etc.):")
    skills = st.text_input("List key skills relevant to the job (comma-separated):")
    experience = st.text_area("Describe your relevant experience:")    

if uploaded_file:
    # st.subheader("Extracted Text:")
    cv_text = extract_text_from_file(uploaded_file)
    # st.text_area("CV Content", cv_text, height=300)

    # Initialize session state for advice and new CV text
    if 'advice_text' not in st.session_state:
        st.session_state.advice_text = ""
    if 'new_cv_text' not in st.session_state:
        st.session_state.new_cv_text = ""
    
    # if st.button("Analyze CV") or st.session_state.advice_text != "":
    #     # st.write("**AI Analysis & Recommendations Coming Soon...**")
    #     prompt = f"""Imgine you are a professional career advisor, please comment on the below CV content.
    #                 Please ignore format issue at this moment as it is just the content.
    #                 Please summarise the advice and reponse within 200 words. 
    #                 CV: {cv_text} """
    #     # st.session_state.advice_text = generate_chat_completion(prompt).content
    #     st.session_state.advice_text = "####comment#####"

    #     st.subheader("AI Analysis & Recommendations")
    #     st.write(st.session_state.advice_text)

    if st.button("Generate Revised CV") or st.session_state.new_cv_text != "":
        prompt = f"""
                    Imagine you are a professional career advisor. 
                    Please help to revise the given CV, paying attention to the format. 
                    Generate the revised CV only, without any additional comments.
                    CV: {cv_text}
                """
        # st.session_state.new_cv_text = generate_chat_completion(prompt).content
        st.session_state.new_cv_text = "New CV"

        # editable_cv = st.text_area("Edit CV", st.session_state.new_cv_text, height=600)
        editable_cv = st.session_state.new_cv_text
        pdf_data = generate_pdf(editable_cv)

        st.subheader("Preview")
        # st.markdown(editable_cv)
        st.image(convert_pdf_to_image(pdf_data), caption="Sunrise by the mountains")        
        st.download_button(label="Download", data=pdf_data, file_name="Revised_CV.pdf", mime="application/pdf")
    
    if st.button("Generate Cover Letter"):
        st.write("**AI-Generated Cover Letter Coming Soon...**")

else:
    st.error("Please upload a CV before clicking Analyze.")

# Additional UI Elements
st.markdown("---")
st.write("Created by [Kyle Yeung](https://github.com/kyle-ycp)")