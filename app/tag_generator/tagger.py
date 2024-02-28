#!/usr/bin/env python3

import operator
import sys
from pprint import pprint

from .datautils import get_test_document, get_train_documents
from .document import Document
from .textprocessor import TokenProcessor
from .tfidf import TFIDF


class Tagger:
    def __init__(self):
        self.documents = {}
        self.tfidf = TFIDF()

    def add_document(self, document):
        self.documents[document.id] = document

    def display(self):
        for id in self.documents:
            self.documents[id].display()

    def get_terms_weighted_by_tfidf(self, document):
        documents = [self.documents[key] for key in self.documents]
        tfidf_list = self.tfidf.calculate_tfidf_document(documents, document)
        weighted_terms = {}
        for d in tfidf_list:
            term = d["term"]
            tf = d["tf"]
            idf = d["idf"]
            weighted_terms[term] = tf * idf
        return weighted_terms

    def get_tags_using_weighted_terms(self, weighted_terms, size=5):
        sorted_terms = sorted(weighted_terms.items(), key=operator.itemgetter(1), reverse=True)
        length = len(weighted_terms)
        size = length if size > length else size
        tags = []
        for i in range(size):
            tags.append(sorted_terms[i][0])
        return tags

    def __str__(self):
        return str(pprint(vars(self)))


def get_tag_from_text(input_str=None):
    n = 5
    token_processor = TokenProcessor()
    testfile = "data/test.txt"

    documents = get_train_documents("data/documents/*", token_processor)

    try:
        doc = get_test_document(input_str, token_processor)
    except FileNotFoundError:
        print("The file '{}' is out of existence. :D".format(testfile))
        return

    tagger = Tagger()
    for document in documents:
        tagger.add_document(document)

    weighted_terms = tagger.get_terms_weighted_by_tfidf(doc)
    tags = tagger.get_tags_using_weighted_terms(weighted_terms, size=n)
    print("The likeky tags for the document are:\n{}".format(tags))
    str_tags = ''
    for tag in tags:
        str_tags += tag + ', '
    return str_tags


def main():
    input_str = "Alcremie - SWSH09: Brilliant Stars Trainer Gallery (SWSH09:TG)"
    get_tag_from_text(input_str)


if __name__ == "__main__":
    main()
