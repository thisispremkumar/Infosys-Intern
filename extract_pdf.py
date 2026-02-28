import pdfplumber

with pdfplumber.open('Small Business Sales & Profit Analyzer.pdf') as pdf:
    text = ''
    for page in pdf.pages:
        text += page.extract_text() + '\n'
    
    with open('pdf_content.txt', 'w', encoding='utf-8') as f:
        f.write(text)
    
    print(text)
