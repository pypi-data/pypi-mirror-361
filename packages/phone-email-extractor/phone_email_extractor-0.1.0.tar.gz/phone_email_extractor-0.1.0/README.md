# Contact Extractify

**Contact Extractify** is a lightweight Python package to extract email addresses, phone numbers, and URLs from raw text. It's built with simplicity and accuracy in mind, making it ideal for quick data extraction tasks or preprocessing text from websites, documents, or logs.

---

## ✨ Features

- 📧 Extract email addresses using robust regex
- 📱 Extract international and local phone numbers
- 🔗 Extract URLs (HTTP, HTTPS, and `www.` formats)
- 🧼 Deduplicated and normalized results

---

## 🚀 Installation

You can install the package using:

```bash
pip install contact-extractify



## 🧑‍💻 Usage

```python
from contact_extractor.core import extract_emails, extract_phones, extract_urls

text = """
Contact us at hello@example.com or visit https://example.com.
You can also call us at +1 (555) 123-4567.
"""

emails = extract_emails(text)
phones = extract_phones(text)
urls = extract_urls(text)

print("Emails:", emails)
print("Phones:", phones)
print("URLs:", urls)
```

---

## 📦 Functions

| Function           | Description                           |
|--------------------|---------------------------------------|
| `extract_emails()` | Extracts all valid email addresses    |
| `extract_phones()` | Extracts phone numbers (normalized)   |
| `extract_urls()`   | Extracts valid URLs from the text     |

---

## 📝 License

This project is licensed under the [MIT License](LICENSE).

---


## 📫 Contact

Maintained by **Gaurav Rawal** – [gauravrawal2001@gmail.com](mailto:gauravrawal2001@gmail.com)