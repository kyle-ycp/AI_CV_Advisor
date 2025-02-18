import pdfplumber
import docx2txt
from io import BytesIO
import pdfkit
import markdown
import os
from docx import Document
from pdf2image import convert_from_bytes

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
                            line-height: 1.5;
                        }
                        h1, h2, h3 {
                            color: #4CAF50;
                            margin-bottom: 10px;
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
                    <link href="https://fonts.googleapis.com/css2?family=Times+New+Roman:wght@400&display=swap" rel="stylesheet">
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