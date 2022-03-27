import re


def clean_html(raw_html):
    """
    Strips all HTML tags from HTML code leaving only plain text with no formatting.
    :param raw_html: HTML string
    :return: plain text string
    """
    clean = re.compile('<.*?>')
    clean_text = re.sub(clean, '', raw_html)
    return clean_text