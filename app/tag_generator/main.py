#!/usr/bin/env python3

from tokenizer import Tokenizer

from .document import Document


def main():
    tokenizer = Tokenizer()

    doc = Document(1)
    #doc.add_text("hello i am paradox")
    doc.load_from_file("documents/test.txt")
    doc.extract_terms(tokenizer)
    doc.generate_frequency_map()
    doc.display()

if __name__ == "__main__":
    main()

