# Convert Large Excel File to CSV/TSV

## Installation

```bash
python3 -m pip install -U large_excel_convert
```

## Usage

### Use in CMD

```bash

large_excel_convert -h
large_excel_convert -i input.xlsx
large_excel_convert -i input.xlsx -o output.csv
large_excel_convert -i input.xlsx -o output.csv -enc gb18030
large_excel_convert -i input.xlsx -o output.tsv -f tsv
large_excel_convert -i input.xlsx -o sheet2.csv -s 2
```

### Use in Python

```python
from large_excel_convert.core import ExcelParser

# excel = ExcelParser('input.xlsx', sheet=1, tag='row')
excel = ExcelParser('input.xlsx')
rows = excel.rows()

for row in rows:
    print(row)
    # ...
````
