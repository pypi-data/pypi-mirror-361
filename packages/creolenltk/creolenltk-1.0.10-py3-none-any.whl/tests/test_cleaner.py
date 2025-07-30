import unittest
from creolenltk import TextCleaner


class TestCleaner(unittest.TestCase):

    def setUp(self):
        # Create an instance of the Cleaner class for testing
        self.cleaner = TextCleaner()

    def test_normalize_whitespace(self):
        input_text = "  Sa  a   se    yon  tès. "
        expected_output = "Sa a se yon tès."
        self.assertEqual(self.cleaner.normalize_whitespace(input_text), expected_output)

    def test_remove_html_tags(self):
        input_text = "<p>Sa se yon <b>tès</b>.</p>"
        expected_output = "Sa se yon tès."
        self.assertEqual(self.cleaner.remove_html_tags(input_text), expected_output)



if __name__ == '__main__':
    unittest.main()
