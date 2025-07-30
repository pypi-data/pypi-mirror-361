from pathlib import Path


class ConlluMerger:
    """
    A utility class to merge .conllu files from multiple sources
    (e.g., 'adolphe' and 'autogramm') into a single combined dataset.
    """

    def __init__(self, base_dir="../data/ud", sources=None, output_subdir="combined"):
        """
        Initialize the merger.

        Args:
            base_dir (str): Base directory where individual corpus folders are stored.
            sources (list): List of subdirectories to merge (default: ["adolphe", "autogramm"]).
            output_subdir (str): Directory name where the combined files will be saved.
        """
        self.base_dir = Path(base_dir)
        self.sources = sources if sources else ["adolphe", "autogramm"]
        self.output_dir = self.base_dir / output_subdir
        self.splits = ["train", "dev", "test"]

    def merge(self):
        """
        Merge .conllu files from each source into single files per split
        and write them into the combined output directory.
        """
        self.output_dir.mkdir(parents=True, exist_ok=True)

        for split in self.splits:
            combined_path = self.output_dir / f"{split}.conllu"

            with combined_path.open("w", encoding="utf-8") as outfile:
                for source in self.sources:
                    source_file = self.base_dir / source / f"{split}.conllu"

                    if source_file.exists():
                        text = source_file.read_text(encoding="utf-8")
                        # Add a newline for safe separation
                        outfile.write(text + "\n")

        print(f"[✓] Merged .conllu files to {self.output_dir}")


if __name__ == "__main__":
    merger = ConlluMerger()
    merger.merge()
