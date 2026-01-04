# XLSX Skill - Excel Spreadsheet Expert

## Purpose
Expert guide for creating and editing Microsoft Excel spreadsheets programmatically using Python.

## Capabilities
- Create workbooks with multiple sheets
- Read and write cell values
- Apply formatting and styles
- Create formulas and functions
- Generate charts and graphs
- Handle large datasets efficiently
- Create pivot tables
- Data validation and conditional formatting

## Best Practices

### Spreadsheet Structure
1. **Headers in row 1** - Clear, descriptive column names
2. **One data type per column** - Don't mix numbers and text
3. **No merged cells in data ranges** - Breaks sorting/filtering
4. **No blank rows/columns** - Interrupts data ranges
5. **Use named ranges** - For formulas and references

### Data Formatting
- Format numbers consistently (decimals, thousands separator)
- Use ISO date format (YYYY-MM-DD) for dates
- Right-align numbers, left-align text
- Use consistent currency symbols
- Apply number formats, don't type symbols

### Performance
- Avoid volatile functions (INDIRECT, OFFSET, NOW)
- Use tables for structured data
- Limit conditional formatting ranges
- Consider data model for large datasets

## Code Examples

### Python (openpyxl)

```python
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils import get_column_letter

# Create workbook
wb = Workbook()
ws = wb.active
ws.title = "Data"

# Add headers
headers = ['Name', 'Age', 'City', 'Salary']
for col, header in enumerate(headers, 1):
    cell = ws.cell(row=1, column=col, value=header)
    cell.font = Font(bold=True)
    cell.fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
    cell.font = Font(bold=True, color="FFFFFF")

# Add data
data = [
    ['Alice', 30, 'New York', 75000],
    ['Bob', 25, 'Los Angeles', 65000],
    ['Charlie', 35, 'Chicago', 85000],
]

for row_idx, row_data in enumerate(data, 2):
    for col_idx, value in enumerate(row_data, 1):
        ws.cell(row=row_idx, column=col_idx, value=value)

# Auto-adjust column widths
for column in ws.columns:
    max_length = 0
    column_letter = get_column_letter(column[0].column)
    for cell in column:
        try:
            if len(str(cell.value)) > max_length:
                max_length = len(str(cell.value))
        except:
            pass
    ws.column_dimensions[column_letter].width = max_length + 2

# Save
wb.save('output.xlsx')
```

### Adding Formulas

```python
# Sum formula
ws['E2'] = '=SUM(D2:D4)'

# Average formula
ws['E3'] = '=AVERAGE(D2:D4)'

# VLOOKUP
ws['F2'] = '=VLOOKUP(A2,A:D,4,FALSE)'

# Conditional formula
ws['G2'] = '=IF(D2>70000,"High","Low")'
```

### Creating Charts

```python
from openpyxl.chart import BarChart, Reference

# Create chart
chart = BarChart()
chart.type = "col"
chart.style = 10
chart.title = "Salary by Employee"
chart.y_axis.title = "Salary"
chart.x_axis.title = "Employee"

# Add data
data = Reference(ws, min_col=4, min_row=1, max_row=4, max_col=4)
categories = Reference(ws, min_col=1, min_row=2, max_row=4)
chart.add_data(data, titles_from_data=True)
chart.set_categories(categories)
chart.shape = 4

# Add to worksheet
ws.add_chart(chart, "F2")
```

### Conditional Formatting

```python
from openpyxl.formatting.rule import ColorScaleRule, CellIsRule
from openpyxl.styles import PatternFill

# Color scale (heat map)
color_scale = ColorScaleRule(
    start_type='min', start_color='FF0000',
    mid_type='percentile', mid_value=50, mid_color='FFFF00',
    end_type='max', end_color='00FF00'
)
ws.conditional_formatting.add('D2:D100', color_scale)

# Cell value rule
red_fill = PatternFill(start_color='FFC7CE', end_color='FFC7CE', fill_type='solid')
ws.conditional_formatting.add('D2:D100',
    CellIsRule(operator='lessThan', formula=['70000'], fill=red_fill))
```

### Data Validation

```python
from openpyxl.worksheet.datavalidation import DataValidation

# Dropdown list
dv = DataValidation(type="list", formula1='"Option1,Option2,Option3"', allow_blank=True)
dv.error = "Please select from the list"
dv.errorTitle = "Invalid Input"
ws.add_data_validation(dv)
dv.add('B2:B100')
```

### Reading Excel Files

```python
from openpyxl import load_workbook

wb = load_workbook('input.xlsx')
ws = wb.active

# Read all data
for row in ws.iter_rows(min_row=2, values_only=True):
    print(row)

# Read specific cell
value = ws['A1'].value

# Read range
for row in ws['A1:D10']:
    for cell in row:
        print(cell.value)
```

## Common Functions Reference

| Function | Example | Description |
|----------|---------|-------------|
| SUM | `=SUM(A1:A10)` | Sum of range |
| AVERAGE | `=AVERAGE(A1:A10)` | Average of range |
| VLOOKUP | `=VLOOKUP(A1,B:C,2,FALSE)` | Vertical lookup |
| IF | `=IF(A1>10,"Yes","No")` | Conditional |
| COUNTIF | `=COUNTIF(A:A,"value")` | Count matching |
| SUMIF | `=SUMIF(A:A,">10",B:B)` | Conditional sum |

## Dependencies

```bash
pip install openpyxl pandas xlsxwriter
```

## For Large Files (pandas)

```python
import pandas as pd

# Read large Excel file
df = pd.read_excel('large_file.xlsx', engine='openpyxl')

# Write with xlsxwriter for better performance
df.to_excel('output.xlsx', engine='xlsxwriter', index=False)
```

## References
- [openpyxl documentation](https://openpyxl.readthedocs.io/)
- [pandas Excel documentation](https://pandas.pydata.org/docs/reference/api/pandas.read_excel.html)
