import subprocess
import sys
from spacy.cli.train import train
from pathlib import Path
import shutil
import spacy
from spacy.tokens import DocBin
from spacy.training import Example


class POSTrainer:
    """
    Trains a spaCy POS tagger for Haitian Creole using UD .conllu files.
    """

    def __init__(self, data_dir="../data/ud/combined", output_dir="./model-best"):
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)

    def convert_ud_to_spacy(self):
        """
        Use spaCy CLI to convert .conllu files into .spacy format.
        """
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        for split in ["train", "dev", "test"]:
            input_file = self.data_dir / f"{split}.conllu"
            subprocess.run([
                sys.executable, "-m", "spacy", "convert",
                str(input_file),
                str(self.output_dir),
                "--converter", "conllu",
                "--file-type", "spacy",
                "--n-sents", "10"
            ], check=True)

            print(f"Converted {input_file} to .spacy format.")

    def train(self):
        """
        Convert data and train the POS tagger.
        """
        self.convert_ud_to_spacy()
        train("config/config.cfg", output_path=self.output_dir)

    def evaluate_spacy_model(self, model_path, test_data_path):
        """
        Evaluate the trained spaCy model on the given .spacy test data.
        """
        nlp = spacy.load(str(model_path))
        doc_bin = DocBin().from_disk(str(test_data_path))
        docs = list(doc_bin.get_docs(nlp.vocab))

        examples = [Example(predicted=nlp(doc.text), reference=doc)
                    for doc in docs]
        scores = nlp.evaluate(examples)
        print("\nEvaluation on test set:")
        for k, v in scores.items():
            print(f"{k:20s} {v}")


if __name__ == "__main__":
    trainer = POSTrainer()
    trainer.train()

    trainer.evaluate_spacy_model(
        trainer.output_dir / "model-best", trainer.output_dir / "test.spacy")
