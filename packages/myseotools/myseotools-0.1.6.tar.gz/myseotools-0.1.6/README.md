
# 📦 My SEO Tools

**My SEO Tools** is a simple yet powerful Python SEO toolkit that helps developers and analysts quickly audit websites using Python.

It includes checks for meta tags, images, keyword density, named entities, canonical tags, broken links, and internal links. All results can be exported to JSON or CSV.

---

## 🚀 Features

- ✅ Meta tag extractor (`title`, `description`)
- 🔗 Broken link checker (internal & external)
- 🧠 Keyword density analyzer
- 🏷️ Named entity extractor (via spaCy)
- 📎 Canonical & Open Graph tag validator
- 🖼️ Image audit (missing alt, large files, preload recommendations)
- 📤 Export results to CSV or JSON

---

## 📦 Installation

```bash
pip install myseotools
```

---

## 🧪 Example Usage

```python
from myseotools.meta_checker import check_meta
from myseotools.image_audit import audit_images
from myseotools.keyword_analyzer import analyze_keyword_density
from myseotools.entity_extractor import extract_entities

url = "https://example.com"

print("🔍 Meta Info:", check_meta(url))
print("🖼️ Image Issues:", audit_images(url))
print("📊 Keyword Density:", analyze_keyword_density(url))
print("🧠 Entities:", extract_entities(url))
```

---

## 📄 Sample Output

```python
{'title': 'Busting CIBIL Score Myths: Get the CIBIL Score Facts Right',
 'description': 'Discover the truth behind common CIBIL score myths. Learn how to maintain a healthy credit score and make informed financial decisions with Airtel Finance.'}
```

---

## 📁 Exporting to CSV or JSON

To save results:

```python
from myseotools.meta_checker import check_meta
import json

data = check_meta("https://example.com")

with open("results.json", "w") as f:
    json.dump(data, f, indent=2)
```

Or to CSV using the `csv` module.

---

## 🧠 Dependencies

- Python 3.7+
- `requests`
- `beautifulsoup4`
- `spacy`
- `lxml`

---

## 🛠️ Notes

- CLI support was available in earlier versions but may not be included in v0.1.4 depending on build.
- You can mix and match modules depending on your audit needs.

---

## 💬 License

MIT

---

## 🙌 Author

Built by **Amal Alexander**  
Feel free to contribute or fork for your own SEO workflows!
