# empire chain
from empire_chain.tools.docling import Docling
import unittest

class TestDocling(unittest.TestCase):
    def test_docling(self):
        docling = Docling()
        converted_doc = docling.convert("Manas-Resume.pdf")
        docling.save_markdown(converted_doc, "Manas-Resume.md")

if __name__ == "__main__":
    unittest.main()