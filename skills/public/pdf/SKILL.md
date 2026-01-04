# PDF Skill - PDF Document Expert

## Purpose
Expert guide for creating, editing, and manipulating PDF documents programmatically using Python.

## Capabilities
- Create PDFs from scratch
- Merge and split PDFs
- Extract text and images
- Add watermarks and annotations
- Fill PDF forms
- Encrypt and decrypt PDFs
- Convert HTML/images to PDF
- OCR for scanned documents

## Best Practices

### PDF Creation
1. **Use vector graphics** when possible for scalability
2. **Embed fonts** to ensure consistent rendering
3. **Optimize images** before embedding (150-300 DPI)
4. **Use PDF/A** for archival purposes
5. **Add metadata** (title, author, keywords)

### Accessibility
- Add proper document structure (headings, lists)
- Include alt text for images
- Use readable fonts (minimum 12pt)
- Ensure sufficient color contrast
- Tag content for screen readers

### Security
- Use strong encryption (AES-256)
- Set appropriate permissions
- Don't rely solely on password protection
- Consider digital signatures for authenticity

## Code Examples

### Creating PDFs (ReportLab)

```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor

# Create PDF
c = canvas.Canvas("output.pdf", pagesize=letter)
width, height = letter

# Add title
c.setFont("Helvetica-Bold", 24)
c.drawString(1*inch, height - 1*inch, "Document Title")

# Add paragraph
c.setFont("Helvetica", 12)
text = "This is a sample paragraph in the PDF document."
c.drawString(1*inch, height - 2*inch, text)

# Add rectangle
c.setStrokeColor(HexColor("#336699"))
c.setFillColor(HexColor("#e6f0ff"))
c.rect(1*inch, height - 4*inch, 3*inch, 1*inch, fill=True)

# Add image
c.drawImage("image.png", 1*inch, height - 6*inch, width=2*inch, height=2*inch)

# Save
c.save()
```

### Multi-page Documents (ReportLab)

```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

doc = SimpleDocTemplate("output.pdf", pagesize=letter)
styles = getSampleStyleSheet()
story = []

# Title
story.append(Paragraph("Report Title", styles['Heading1']))
story.append(Spacer(1, 12))

# Paragraphs
story.append(Paragraph("This is the introduction paragraph.", styles['Normal']))
story.append(Spacer(1, 12))

# Table
data = [
    ['Header 1', 'Header 2', 'Header 3'],
    ['Row 1', 'Data', 'Data'],
    ['Row 2', 'Data', 'Data'],
]
table = Table(data)
story.append(table)

# Build PDF
doc.build(story)
```

### Merging PDFs (PyPDF2)

```python
from PyPDF2 import PdfMerger

merger = PdfMerger()

# Add PDFs to merge
merger.append("document1.pdf")
merger.append("document2.pdf")
merger.append("document3.pdf", pages=(0, 3))  # Only pages 1-3

# Write merged PDF
merger.write("merged.pdf")
merger.close()
```

### Splitting PDFs (PyPDF2)

```python
from PyPDF2 import PdfReader, PdfWriter

reader = PdfReader("input.pdf")

# Extract specific pages
writer = PdfWriter()
writer.add_page(reader.pages[0])  # First page
writer.add_page(reader.pages[2])  # Third page

with open("extracted.pdf", "wb") as output:
    writer.write(output)

# Split into individual pages
for i, page in enumerate(reader.pages):
    writer = PdfWriter()
    writer.add_page(page)
    with open(f"page_{i+1}.pdf", "wb") as output:
        writer.write(output)
```

### Extracting Text (PyPDF2)

```python
from PyPDF2 import PdfReader

reader = PdfReader("document.pdf")

# Extract from all pages
full_text = ""
for page in reader.pages:
    full_text += page.extract_text()

print(full_text)

# Extract from specific page
text = reader.pages[0].extract_text()
```

### Adding Watermark

```python
from PyPDF2 import PdfReader, PdfWriter

# Read watermark
watermark_reader = PdfReader("watermark.pdf")
watermark_page = watermark_reader.pages[0]

# Read source document
reader = PdfReader("document.pdf")
writer = PdfWriter()

# Apply watermark to each page
for page in reader.pages:
    page.merge_page(watermark_page)
    writer.add_page(page)

with open("watermarked.pdf", "wb") as output:
    writer.write(output)
```

### Encrypting PDFs

```python
from PyPDF2 import PdfReader, PdfWriter

reader = PdfReader("document.pdf")
writer = PdfWriter()

for page in reader.pages:
    writer.add_page(page)

# Encrypt with password
writer.encrypt(
    user_password="user_pass",
    owner_password="owner_pass",
    use_128bit=True
)

with open("encrypted.pdf", "wb") as output:
    writer.write(output)
```

### HTML to PDF (weasyprint)

```python
from weasyprint import HTML, CSS

# From URL
HTML('https://example.com').write_pdf('from_url.pdf')

# From HTML string
html_content = """
<html>
<head><style>body { font-family: Arial; }</style></head>
<body><h1>Hello World</h1><p>This is a PDF from HTML.</p></body>
</html>
"""
HTML(string=html_content).write_pdf('from_string.pdf')

# With custom CSS
css = CSS(string='@page { size: A4; margin: 1cm }')
HTML(string=html_content).write_pdf('styled.pdf', stylesheets=[css])
```

## Library Comparison

| Library | Best For | Limitations |
|---------|----------|-------------|
| ReportLab | Creating PDFs from scratch | Complex API |
| PyPDF2 | Merging, splitting, basic editing | Limited text extraction |
| pdfplumber | Text extraction, tables | Read-only |
| weasyprint | HTML to PDF | Requires system dependencies |
| PyMuPDF (fitz) | Fast operations, rendering | Large binary size |

## Dependencies

```bash
pip install reportlab PyPDF2 pdfplumber weasyprint pymupdf
```

## OCR for Scanned PDFs

```python
import pytesseract
from pdf2image import convert_from_path

# Convert PDF to images
images = convert_from_path('scanned.pdf')

# OCR each page
full_text = ""
for image in images:
    text = pytesseract.image_to_string(image)
    full_text += text + "\n"

print(full_text)
```

## References
- [ReportLab documentation](https://www.reportlab.com/docs/reportlab-userguide.pdf)
- [PyPDF2 documentation](https://pypdf2.readthedocs.io/)
- [WeasyPrint documentation](https://weasyprint.org/)
