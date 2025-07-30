import spacy
from pathlib import Path
from typing import List, Tuple


class PosTagger:
    """
    A wrapper class for loading and using a spaCy POS tagging model,
    specifically designed for Haitian Creole trained models.
    """

    def __init__(self, model_path: str = None):
        """
        Initialize the POS tagger.

        Args:
            model_path (str, optional): Path to the trained spaCy model directory.
                                        If not provided, defaults to ./model-best/model-best relative to this file.
        """
        if model_path is None:
            model_path = Path(__file__).parent / "model-best" / "model-best"
        self.nlp = spacy.load(str(model_path))
        print(str(model_path))

    def tag(self, text: str) -> List[Tuple[str, str]]:
        """
        Tag the input text with part-of-speech labels.

        Args:
            text (str): The input sentence or paragraph.

        Returns:
            List[Tuple[str, str]]: A list of (word, POS tag) tuples.
        """
        doc = self.nlp(text)
        return [(token.text, token.tag_) for token in doc]

