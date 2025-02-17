import streamlit as st
import pdfplumber
import docx2txt
from pdf2image import convert_from_bytes
from io import BytesIO
import pdfkit
import markdown
from chatbot import generate_chat_completion
import os
from docx import Document

# Set app icon and title
st.set_page_config(page_title="AI-Powered CV Advisor", page_icon="📄", layout="wide", 
                   menu_items=
                   {
                        'Get Help': 'https://www.extremelycoolapp.com/help',
                        'Report a bug': "https://www.extremelycoolapp.com/bug",
                        'About': "# This is a header. This is an *extremely* cool app!"
                    }
)

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
    
    # Ensure the text is properly encoded
    html_text = markdown.markdown(markdown_text, extensions=['extra', 'smarty'])

    custom_css = """
                    <style>
                        body {
                            font-family: 'Times New Roman', serif;
                            font-size: 12pt;
                            color: #333;
                            line-height: 1.5; /* Improve readability */
                        }
                        h1, h2, h3 {
                            color: #4CAF50; /* Change as needed */
                            margin-bottom: 10px; /* Add spacing below headings */
                        }
                        p {
                            margin: 10px 0;
                        }
                        .highlight {
                            background-color: #f0f0f0;
                            padding: 5px;
                            border-left: 5px solid #4CAF50;
                        }
                    </style>
                """
    
    # Combine HTML with custom CSS
    full_html = f"""
    <html>
    <head>
        <meta charset="utf-8">
        <title>CV Document</title>
        {custom_css}
    </head>
    <body>
        {html_text}
    </body>
    </html>
    """

    # Use pdfkit to generate the PDF
    config = pdfkit.configuration()  # Adjust path as necessary
    pdf_data = pdfkit.from_string(full_html, False, options=options, configuration=config)

    return pdf_data
def convert_pdf_to_image(pdf_data):
    # Convert PDF bytes to images
    images = convert_from_bytes(pdf_data)
    return images

def create_docx(document):
    # Create a new Document
    doc = Document()
    doc.add_paragraph(document)
    
    # Save the document to a BytesIO object
    doc_io = BytesIO()
    doc.save(doc_io)
    doc_io.seek(0)  # Move to the beginning of the BytesIO buffer
    return doc_io

# Streamlit UI
st.title("AI-Powered CV Advisor")

# Create two columns
col1, col2 = st.columns([1, 1])  # Adjust ratios as needed

# Upper section in the first column
with col1:
    st.header("Upload your CV")
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
            st.session_state.new_cv_text = generate_chat_completion(prompt).content
            # st.session_state.new_cv_text = "New CV"

            # editable_cv = st.text_area("Edit CV", st.session_state.new_cv_text, height=600)
            editable_cv = st.session_state.new_cv_text
            pdf_data = generate_pdf(editable_cv)
            docx_io = create_docx(editable_cv)

            st.subheader("Preview")
            # st.markdown(editable_cv)
            st.image(convert_pdf_to_image(pdf_data), caption="Generated by CV Advisor")        
            
            col3, col4 = st.columns(2)
            
            with col3:
                st.download_button(label="Download PDF", data=pdf_data, file_name="Revised_CV.pdf", mime="application/pdf")
            with col4:
                st.download_button(label="Download Docx", data=docx_io, file_name="Revised_CV.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

        if st.button("Generate Cover Letter"):
            # Create a prompt for generating the cover letter
            cover_letter_prompt = f"""
                Write a cover letter for a job application based on the following details:
                Job Listing URL: {job_url}
                Key Skills: {skills}
                CV Content: {cv_text}

                Please make it professional and targeted for the job position.
            """
            cover_letter = generate_chat_completion(cover_letter_prompt).content
            pdf_data = generate_pdf(cover_letter)
            docx_io = create_docx(cover_letter)

            st.subheader("Preview")
            # st.markdown(editable_cv)
            st.image(convert_pdf_to_image(pdf_data), caption="Generated by CV Advisor")        
            st.download_button(label="Download Template", data=docx_io, file_name="Cover_Letter.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    else:
        st.error("Please upload a CV before clicking Analyze.")
    

# Lower section in the second column
with col2:
    st.header("Chat Bot")
    messages_placeholder = st.container(height=550)
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({"role": "assistant", "content": "Hello! I'm your AI assistant here to help you. Let's get started!"})

    # Display chat messages from history on app rerun
    with messages_placeholder:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # React to user input
    if user_message := st.chat_input("What is up?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": user_message})

        # Display user message in Chat Display
        with messages_placeholder:
            with st.chat_message("user"):
                st.markdown(user_message)

        # Generate AI response
            conversation_history_list = st.session_state.messages
        
        # Create a comprehensive prompt for the chatbot
        if uploaded_file:
            # Include additional information in the prompt
            additional_context = f"""
            Job Listing URL: {job_url}
            Key Skills: {skills}
            Relevant Experience: {experience}
            CV Content: {cv_text}
            User Query: {prompt}
            """
            prompt = f"""
            Imagine you are a professional career advisor. 
            Please provide advice based on the following details:
            {additional_context}
            """

        else:
            prompt = f"""Imgine you are a professional career advisor, please comment on the below CV content.
                            CV: {cv_text} """

        response = f"{generate_chat_completion(prompt + user_message).content}"

        # Append "assistant" message to chat history
        st.session_state.messages.append({"role": "assistant", "content": response})
        # Display assistant response in chat message container
        with messages_placeholder:
            with st.chat_message("assistant"):
                st.markdown(response)
        

# Additional UI Elements
st.markdown("---")
st.write("Created by [Kyle Yeung](https://github.com/kyle-ycp)")