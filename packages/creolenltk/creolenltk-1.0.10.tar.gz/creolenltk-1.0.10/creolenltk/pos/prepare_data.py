import os
import random
from pathlib import Path
from conllu import parse_incr


class ConlluSplitter:
    """
    A class for loading, shuffling, and splitting .conllu sentences
    into training and development sets.
    """

    def __init__(self, data_dir="../data/ud/autogramm", dev_split=0.1):
        """
        Initialize the splitter.

        Args:
            data_dir (str): Path to the base data directory.
            dev_split (float): Fraction of data to reserve for the dev set.
        """
        self.data_dir = Path(data_dir)
        self.source_dir = self.data_dir / "not-to-release"
        self.output_dir = self.data_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.train_file = self.output_dir / "train.conllu"
        self.dev_file = self.output_dir / "dev.conllu"
        self.dev_split = dev_split

    def load_sentences(self):
        """
        Load all parsed sentences from .conllu files in the source directory.
        """
        sentences = []
        for file in sorted(self.source_dir.glob("*.conllu")):
            with file.open("r", encoding="utf-8") as f:
                sentences.extend(parse_incr(f))
        return sentences

    def save_sentences(self, sentences, out_path):
        """
        Serialize a list of TokenLists to a .conllu output file.
        """
        with out_path.open("w", encoding="utf-8") as f:
            for sentence in sentences:
                f.write(sentence.serialize())
        print(f"✓ Saved {len(sentences)} sentences to {out_path}")

    def split_and_save(self):
        """
        Shuffle, split into train/dev, and save the sentences.
        """
        print(f"Loading data from: {self.source_dir}")
        all_sentences = self.load_sentences()
        print(f"Total sentences loaded: {len(all_sentences)}")

        # Shuffle the dataset for a randomized split
        random.seed(42)
        random.shuffle(all_sentences)

        split_idx = int(len(all_sentences) * (1 - self.dev_split))
        train_sents = all_sentences[:split_idx]
        dev_sents = all_sentences[split_idx:]

        # Save split data
        self.save_sentences(train_sents, self.train_file)
        self.save_sentences(dev_sents, self.dev_file)


if __name__ == "__main__":
    splitter = ConlluSplitter()
    splitter.split_and_save()
