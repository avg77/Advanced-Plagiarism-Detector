from flask import Flask, request, render_template
import PyPDF2
import docx
import requests
import json
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ''
    for page_num in range(len(reader.pages)):
        text += reader.pages[page_num].extract_text()
    return text


def extract_text_from_docx(file):
    doc = docx.Document(file)
    full_text = []
    for para in doc.paragraphs:
        full_text.append(para.text)
    return '\n'.join(full_text)

def extract_text_from_txt(file):
    return file.read().decode('utf-8')

def check_plagiarism(text_to_check):
    burp0_url = "https://papersowl.com:443/plagiarism-checker-send-data"
    burp0_headers = {"User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64; rv:100.0) Gecko/20100101 Firefox/100.0", "Accept": "*/*", "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3", "Accept-Encoding": "gzip, deflate", "Referer": "https://papersowl.com/free-plagiarism-checker", "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "X-Requested-With": "XMLHttpRequest", "Origin": "https://papersowl.com", "Dnt": "1", "Sec-Fetch-Dest": "empty", "Sec-Fetch-Mode": "no-cors", "Sec-Fetch-Site": "same-origin", "Pragma": "no-cache", "Cache-Control": "no-cache", "Te": "trailers", "Connection": "close"}
    burp0_data = {"is_free": "false", "plagchecker_locale": "en", "product_paper_type": "1", "title": '', "text": str(text_to_check)}
    try:
        r = requests.post(burp0_url, headers=burp0_headers, data=burp0_data)
        r.raise_for_status()
        result = json.loads(r.text)
        return result
    except requests.exceptions.RequestException as e:
        logger.error(f"Error occurred during plagiarism check: {str(e)}")
        return None

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' in request.files:
            file = request.files['file']
            if file.filename.endswith('.pdf'):
                text = extract_text_from_pdf(file)
            elif file.filename.endswith('.docx'):
                text = extract_text_from_docx(file)
            elif file.filename.endswith('.txt'):
                text = extract_text_from_txt(file)
            else:
                return "Unsupported file format. Please upload a PDF, DOCX, or TXT file."
            
            plagiarism_result = check_plagiarism(text)
            if plagiarism_result is not None:
                return render_template('result.html', result=plagiarism_result, uploaded_text=text)
            else:
                return "An error occurred during plagiarism check. Please try again later."
        else:
            return "No file was uploaded."
    
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)
