import re


def clean_text(text):
    # Replace multiple spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Replace excessive blank lines
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    # Remove leading/trailing whitespace
    text = text.strip()

    return text