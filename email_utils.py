import csv
import os
import re
import markdown
from dotenv import load_dotenv

load_dotenv()

def load_template(file_path: str) -> str:
    """Load email template content."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def read_csv_data(csv_file_path: str):
    """Read recipient data from CSV and return list of dicts."""
    with open(csv_file_path, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def is_valid_email(email: str) -> bool:
    """Simple regex validation for email format."""
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return bool(re.match(pattern, email))

def get_attachments(folder: str = "ATTACH"):
    """Return confirmed attachments if the folder exists."""
    attachments = {'names': [], 'contents': []}
    if not os.path.exists(folder):
        return attachments

    for filename in os.listdir(folder):
        confirmed = input(f"Attach '{filename}'? (Y/n): ").strip().lower()
        if confirmed in ("y", "yes", ""):
            with open(os.path.join(folder, filename), "rb") as f:
                attachments['names'].append(filename)
                attachments['contents'].append(f.read())
    return attachments

def markdown_to_html(text: str) -> str:
    """Convert markdown text to HTML."""
    return markdown.markdown(text)
