import os, sys, json, requests
import itertools
from datetime import datetime
from collections import Counter
from operator import itemgetter
from academic_search import *

if __name__ == "__main__":
    field_name = "deep learning"
    # field_name = "compiler"
    citation = [200, 10000]
    data = get_papers_from_field_of_study(field_name, citation)
    papers = {p["Id"]:p for p in data["entities"]}
    authors = {}
    for pid in papers:
        for a in papers[pid]["AA"]:
            authors[a["AuId"]] = a["AuN"]
    print("field: {}, citation: {}~{}, #papers: {} #authors: {}"
        .format(field_name, citation[0], citation[1], len(papers), len(authors)))

    paper_ids = list(papers.keys())
    citations = get_citations_from_papers(paper_ids)
