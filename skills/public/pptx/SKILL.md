# PPTX Skill - PowerPoint Presentation Expert

## Purpose
Expert guide for creating and editing Microsoft PowerPoint presentations programmatically using Python.

## Capabilities
- Create new presentations with professional layouts
- Add slides with various layouts
- Insert text, images, charts, and shapes
- Apply themes and master slides
- Add animations and transitions (limited)
- Create speaker notes
- Export to PDF

## Best Practices

### Slide Design
1. **One idea per slide** - Keep content focused
2. **6x6 Rule** - Maximum 6 bullet points, 6 words each
3. **Consistent layout** - Use master slides for consistency
4. **Visual hierarchy** - Use size and color to guide attention
5. **White space** - Don't overcrowd slides

### Typography
- **Title text**: 36-44pt
- **Body text**: 24-32pt
- **Minimum readable**: 18pt
- **Fonts**: Sans-serif for presentations (Arial, Calibri, Helvetica)
- **Contrast**: Dark text on light background or vice versa

### Colors
- Use 3-5 colors maximum
- Maintain brand consistency
- Ensure sufficient contrast (WCAG AA minimum)
- Use color to highlight, not decorate

### Images
- High resolution (1920x1080 minimum for full-slide)
- Consistent style across presentation
- Use as backgrounds sparingly
- Ensure text readability over images

## Code Examples

### Python (python-pptx)

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

# Create presentation
prs = Presentation()

# Set slide dimensions (16:9)
prs.slide_width = Inches(13.333)
prs.slide_height = Inches(7.5)

# Add title slide
title_slide_layout = prs.slide_layouts[0]
slide = prs.slides.add_slide(title_slide_layout)

title = slide.shapes.title
subtitle = slide.placeholders[1]

title.text = "Presentation Title"
subtitle.text = "Subtitle or Author Name"

# Add content slide
bullet_slide_layout = prs.slide_layouts[1]
slide = prs.slides.add_slide(bullet_slide_layout)

shapes = slide.shapes
title_shape = shapes.title
body_shape = shapes.placeholders[1]

title_shape.text = "Slide Title"

tf = body_shape.text_frame
tf.text = "First bullet point"

p = tf.add_paragraph()
p.text = "Second bullet point"
p.level = 0

p = tf.add_paragraph()
p.text = "Sub-bullet point"
p.level = 1

# Save presentation
prs.save('presentation.pptx')
```

### Adding Images

```python
from pptx.util import Inches

# Add blank slide
blank_slide_layout = prs.slide_layouts[6]
slide = prs.slides.add_slide(blank_slide_layout)

# Add image
left = Inches(1)
top = Inches(1)
width = Inches(5)
slide.shapes.add_picture('image.png', left, top, width=width)
```

### Adding Charts

```python
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE

# Create chart data
chart_data = CategoryChartData()
chart_data.categories = ['Q1', 'Q2', 'Q3', 'Q4']
chart_data.add_series('Series 1', (19.2, 21.4, 16.7, 22.3))

# Add chart to slide
x, y, cx, cy = Inches(2), Inches(2), Inches(6), Inches(4.5)
chart = slide.shapes.add_chart(
    XL_CHART_TYPE.COLUMN_CLUSTERED, x, y, cx, cy, chart_data
).chart
```

### Adding Tables

```python
rows, cols = 3, 4
left, top = Inches(1), Inches(2)
width, height = Inches(8), Inches(2)

table = slide.shapes.add_table(rows, cols, left, top, width, height).table

# Set column widths
table.columns[0].width = Inches(2)

# Add content
table.cell(0, 0).text = "Header 1"
table.cell(0, 1).text = "Header 2"
```

## Slide Layouts Reference

| Index | Layout Name | Use Case |
|-------|-------------|----------|
| 0 | Title Slide | Opening slide |
| 1 | Title and Content | Standard content |
| 2 | Section Header | Section dividers |
| 3 | Two Content | Comparison slides |
| 4 | Comparison | Side-by-side with titles |
| 5 | Title Only | Custom content slides |
| 6 | Blank | Full custom layouts |

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Text overflow | Reduce font size or split content |
| Image quality loss | Use high-res source images |
| Inconsistent styling | Use master slides |
| Large file size | Compress images, limit embedded fonts |

## Dependencies

```bash
pip install python-pptx Pillow
```

## References
- [python-pptx documentation](https://python-pptx.readthedocs.io/)
