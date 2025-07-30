import re
from bs4 import BeautifulSoup


class TextCleaner:
    """
    A class for performing various text cleaning operations,
    preserving Haitian Creole accented characters and important punctuation.

    Methods:
    - normalize_whitespace(text): Normalize whitespace.
    - remove_html_tags(text): Remove HTML tags.
    - clean_special_characters(text, keep_numbers=True): Clean text with regex allowing important chars.
    - clean_text(text, lowercase=True, keep_numbers=True): Comprehensive text cleaning pipeline.
    """

    @staticmethod
    def normalize_whitespace(text):
        """Normalize whitespace by replacing consecutive spaces with a single space."""
        return ' '.join(text.split())

    @staticmethod
    def remove_html_tags(text):
        """Remove HTML tags from the input text."""
        soup = BeautifulSoup(text, 'html.parser')
        return soup.get_text()

    @staticmethod
    def clean_special_characters(text, keep_numbers=True):
        """
        Remove unwanted characters while keeping important Haitian Creole letters and punctuation.

        Parameters:
        - text (str): Input text.
        - keep_numbers (bool): Whether to keep numerical digits.

        Returns:
        - str: Cleaned text.
        """
        if keep_numbers:
            pattern = r"[^A-Za-zÀ-ÿ0-9 !,.\-'\?%\(\)]"
        else:
            pattern = r"[^A-Za-zÀ-ÿ !,.\-'\?%\(\)]"

        cleaned = re.sub(pattern, ' ', text)
        return TextCleaner.normalize_whitespace(cleaned)

    @staticmethod
    def clean_text(text, lowercase=True, keep_numbers=True):
        """
        Perform comprehensive text cleaning.

        Parameters:
        - text (str): Input text.
        - lowercase (bool): Convert to lowercase.
        - keep_numbers (bool): Retain numerical digits.

        Returns:
        - str: Cleaned text.
        """
        if not isinstance(text, str):
            return ""

        cleaned_html = TextCleaner.remove_html_tags(text)
        cleaned_text = TextCleaner.clean_special_characters(
            cleaned_html, keep_numbers=keep_numbers)

        if lowercase:
            cleaned_text = cleaned_text.lower()

        return cleaned_text
