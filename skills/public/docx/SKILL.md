# DOCX Skill - Word Document Expert

## Purpose
Expert guide for creating and editing Microsoft Word documents programmatically using Python.

## Capabilities
- Create new documents with proper structure
- Add headings, paragraphs, tables, and lists
- Insert images and charts
- Apply styles and formatting
- Create headers/footers and page numbers
- Generate table of contents
- Work with sections and page breaks

## Best Practices

### Document Structure
1. Always start with a title (Heading 1)
2. Use proper heading hierarchy (H1 > H2 > H3)
3. Include page numbers for documents > 3 pages
4. Add a table of contents for documents > 10 pages
5. Use consistent spacing between sections

### Formatting Guidelines
- **Fonts**: Use consistent fonts (recommended: Calibri, Arial, Times New Roman)
- **Body text**: 11-12pt font size
- **Headings**: 14-18pt depending on level
- **Line spacing**: 1.15 or 1.5 for readability
- **Margins**: 1 inch on all sides (standard)
- **Paragraph spacing**: 6pt before, 6pt after

### Tables
- Include header row with bold text
- Use alternating row colors for readability
- Keep tables on single page when possible
- Add table captions for reference

### Images
- Use appropriate resolution (150-300 DPI for print)
- Compress images to reduce file size
- Add alt text for accessibility
- Use consistent sizing

## Code Examples

### Python (python-docx)

```python
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE

# Create a new document
doc = Document()

# Add title
title = doc.add_heading('Document Title', 0)
title.alignment = WD_ALIGN_PARAGRAPH.CENTER

# Add paragraph with formatting
para = doc.add_paragraph()
run = para.add_run('This is bold and ')
run.bold = True
run = para.add_run('this is italic.')
run.italic = True

# Add a table
table = doc.add_table(rows=3, cols=3)
table.style = 'Table Grid'

# Add header row
hdr_cells = table.rows[0].cells
hdr_cells[0].text = 'Column 1'
hdr_cells[1].text = 'Column 2'
hdr_cells[2].text = 'Column 3'

# Add an image
doc.add_picture('image.png', width=Inches(4))

# Add page break
doc.add_page_break()

# Save the document
doc.save('output.docx')
```

### Creating Headers and Footers

```python
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

section = doc.sections[0]
header = section.header
header_para = header.paragraphs[0]
header_para.text = "Document Header"
header_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

footer = section.footer
footer_para = footer.paragraphs[0]
footer_para.text = "Page "
# Add page number field
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
run = footer_para.add_run()
fldChar1 = OxmlElement('w:fldChar')
fldChar1.set(qn('w:fldCharType'), 'begin')
run._r.append(fldChar1)
```

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Large file size | Compress images before insertion |
| Font not displaying | Use standard fonts or embed custom fonts |
| Table spanning pages | Use `table.allow_autofit = False` |
| Inconsistent formatting | Use document styles instead of direct formatting |

## Dependencies

```bash
pip install python-docx Pillow
```

## References
- [python-docx documentation](https://python-docx.readthedocs.io/)
- [Microsoft Word file format](https://docs.microsoft.com/en-us/openspecs/office_standards/ms-docx/)
