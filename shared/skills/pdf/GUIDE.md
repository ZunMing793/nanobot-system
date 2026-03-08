# PDF è¯¦ç»æå

æ¬ææ¡£åå?PDF æä»¶å¤ççå®æ´æä½æµç¨åé«çº§åè½ã?
---

## 1. Python åº?
### pypdf - åºæ¬æä½

#### åå¹¶ PDF

```python
from pypdf import PdfWriter, PdfReader

writer = PdfWriter()
for pdf_file in ["doc1.pdf", "doc2.pdf", "doc3.pdf"]:
    reader = PdfReader(pdf_file)
    for page in reader.pages:
        writer.add_page(page)

with open("merged.pdf", "wb") as output:
    writer.write(output)
```

#### æå PDF

```python
reader = PdfReader("input.pdf")
for i, page in enumerate(reader.pages):
    writer = PdfWriter()
    writer.add_page(page)
    with open(f"page_{i+1}.pdf", "wb") as output:
        writer.write(output)
```

#### æååæ°æ?
```python
reader = PdfReader("document.pdf")
meta = reader.metadata
print(f"Title: {meta.title}")
print(f"Author: {meta.author}")
print(f"Subject: {meta.subject}")
print(f"Creator: {meta.creator}")
```

#### æè½¬é¡µé¢

```python
reader = PdfReader("input.pdf")
writer = PdfWriter()

page = reader.pages[0]
page.rotate(90)  # é¡ºæ¶éæè½?90 åº?writer.add_page(page)

with open("rotated.pdf", "wb") as output:
    writer.write(output)
```

### pdfplumber - ææ¬åè¡¨æ ¼æå?
#### å¸¦å¸å±æåææ¬

```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        print(text)
```

#### æåè¡¨æ ¼

```python
with pdfplumber.open("document.pdf") as pdf:
    for i, page in enumerate(pdf.pages):
        tables = page.extract_tables()
        for j, table in enumerate(tables):
            print(f"Table {j+1} on page {i+1}:")
            for row in table:
                print(row)
```

#### é«çº§è¡¨æ ¼æå

```python
import pandas as pd

with pdfplumber.open("document.pdf") as pdf:
    all_tables = []
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            if table:  # æ£æ¥è¡¨æ ¼æ¯å¦ä¸ºç©?                df = pd.DataFrame(table[1:], columns=table[0])
                all_tables.append(df)

# åå¹¶ææè¡¨æ ?if all_tables:
    combined_df = pd.concat(all_tables, ignore_index=True)
    combined_df.to_excel("extracted_tables.xlsx", index=False)
```

### reportlab - åå»º PDF

#### åºæ¬ PDF åå»º

```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

c = canvas.Canvas("hello.pdf", pagesize=letter)
width, height = letter

# æ·»å ææ¬
c.drawString(100, height - 100, "Hello World!")
c.drawString(100, height - 120, "This is a PDF created with reportlab")

# æ·»å çº¿æ¡
c.line(100, height - 140, 400, height - 140)

# ä¿å­
c.save()
```

#### åå»ºå¤é¡µ PDF

```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

doc = SimpleDocTemplate("report.pdf", pagesize=letter)
styles = getSampleStyleSheet()
story = []

# æ·»å åå®¹
title = Paragraph("Report Title", styles['Title'])
story.append(title)
story.append(Spacer(1, 12))

body = Paragraph("This is the body of the report. " * 20, styles['Normal'])
story.append(body)
story.append(PageBreak())

# ç¬?2 é¡?story.append(Paragraph("Page 2", styles['Heading1']))
story.append(Paragraph("Content for page 2", styles['Normal']))

# æå»º PDF
doc.build(story)
```

#### ä¸æ åä¸æ ?
**éè¦**ï¼æ°¸è¿ä¸è¦å¨ ReportLab PDF ä¸­ä½¿ç?Unicode ä¸æ /ä¸æ å­ç¬¦ï¼ââââââââââ? â°Â¹Â²Â³â´âµâ¶â·â¸â¹ï¼ãåç½®å­ä½ä¸åå«è¿äºå­å½¢ï¼ä¼å¯¼è´å®ä»¬æ¸²æä¸ºå®å¿é»æ¡ã?
ç¸åï¼å¨ Paragraph å¯¹è±¡ä¸­ä½¿ç?ReportLab ç?XML æ è®°æ ç­¾ï¼?
```python
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet

styles = getSampleStyleSheet()

# ä¸æ ï¼ä½¿ç?<sub> æ ç­¾
chemical = Paragraph("H<sub>2</sub>O", styles['Normal'])

# ä¸æ ï¼ä½¿ç?<super> æ ç­¾
squared = Paragraph("x<super>2</super> + y<super>2</super>", styles['Normal'])
```

å¯¹äºç»å¸ç»å¶çææ¬ï¼é?Paragraph å¯¹è±¡ï¼ï¼æå¨è°æ´å­ä½å¤§å°åä½ç½®ï¼èä¸æ¯ä½¿ç?Unicode ä¸æ /ä¸æ ã?
---

## 2. å½ä»¤è¡å·¥å?
### pdftotext (poppler-utils)

```bash
# æåææ¬
pdftotext input.pdf output.txt

# ä¿çå¸å±æåææ¬
pdftotext -layout input.pdf output.txt

# æåç¹å®é¡µé¢
pdftotext -f 1 -l 5 input.pdf output.txt  # ç¬?1-5 é¡?```

### qpdf

```bash
# åå¹¶ PDF
qpdf --empty --pages file1.pdf file2.pdf -- merged.pdf

# æåé¡µé¢
qpdf input.pdf --pages . 1-5 -- pages1-5.pdf
qpdf input.pdf --pages . 6-10 -- pages6-10.pdf

# æè½¬é¡µé¢
qpdf input.pdf output.pdf --rotate=+90:1  # å°ç¬¬ 1 é¡µæè½?90 åº?
# ç§»é¤å¯ç 
qpdf --password=mypassword --decrypt encrypted.pdf decrypted.pdf
```

### pdftkï¼å¦æå¯ç¨ï¼

```bash
# åå¹¶
pdftk file1.pdf file2.pdf cat output merged.pdf

# æå
pdftk input.pdf burst

# æè½¬
pdftk input.pdf rotate 1east output rotated.pdf
```

---

## 3. å¸¸ç¨ä»»å¡

### ä»æ«æ?PDF æåææ¬

```python
# éè¦ï¼pip install pytesseract pdf2image
import pytesseract
from pdf2image import convert_from_path

# å°?PDF è½¬æ¢ä¸ºå¾å?images = convert_from_path('scanned.pdf')

# å¯¹æ¯é¡µè¿è¡?OCR
text = ""
for i, image in enumerate(images):
    text += f"Page {i+1}:\n"
    text += pytesseract.image_to_string(image)
    text += "\n\n"

print(text)
```

### æ·»å æ°´å°

```python
from pypdf import PdfReader, PdfWriter

# åå»ºæ°´å°ï¼æå è½½ç°æçï¼
watermark = PdfReader("watermark.pdf").pages[0]

# åºç¨äºææé¡µé?reader = PdfReader("document.pdf")
writer = PdfWriter()

for page in reader.pages:
    page.merge_page(watermark)
    writer.add_page(page)

with open("watermarked.pdf", "wb") as output:
    writer.write(output)
```

### æåå¾å

```bash
# ä½¿ç¨ pdfimages (poppler-utils)
pdfimages -j input.pdf output_prefix

# è¿ä¼æåææå¾åä¸º output_prefix-000.jpg, output_prefix-001.jpg ç­?```

### å¯ç ä¿æ¤

```python
from pypdf import PdfReader, PdfWriter

reader = PdfReader("input.pdf")
writer = PdfWriter()

for page in reader.pages:
    writer.add_page(page)

# æ·»å å¯ç 
writer.encrypt("userpassword", "ownerpassword")

with open("encrypted.pdf", "wb") as output:
    writer.write(output)
```

---

## 4. å¿«éåè?
| ä»»å¡ | æä½³å·¥å?| å½ä»¤/ä»£ç  |
|------|----------|-----------|
| åå¹¶ PDF | pypdf | `writer.add_page(page)` |
| æå PDF | pypdf | æ¯æä»¶ä¸é¡?|
| æåææ¬ | pdfplumber | `page.extract_text()` |
| æåè¡¨æ ¼ | pdfplumber | `page.extract_tables()` |
| åå»º PDF | reportlab | Canvas æ?Platypus |
| å½ä»¤è¡åå¹?| qpdf | `qpdf --empty --pages ...` |
| OCR æ«æ PDF | pytesseract | åè½¬æ¢ä¸ºå¾å |
| å¡«å PDF è¡¨å | pdf-lib æ?pypdfï¼è§ FORMS.mdï¼?| è§?FORMS.md |

---

## 5. åç»­æ­¥éª¤

- æå³é«çº§ pypdfium2 ç¨æ³ï¼è§ REFERENCE.md
- æå³ JavaScript åºï¼pdf-libï¼ï¼è§?REFERENCE.md
- å¦éå¡«å PDF è¡¨åï¼æç?FORMS.md ä¸­çè¯´ææä½
- æå³æéæé¤æåï¼è§ REFERENCE.md
