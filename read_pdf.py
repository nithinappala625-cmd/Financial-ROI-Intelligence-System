import sys

try:
    import pypdf

    with open("Project_Status_Report.pdf", "rb") as f:
        reader = pypdf.PdfReader(f)
        for page in reader.pages:
            print(page.extract_text())
except Exception as e:
    print(f"Error reading PDF: {e}")
