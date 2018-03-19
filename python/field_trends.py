import os, sys, json, requests
import itertools
from datetime import datetime
from collections import Counter
from operator import itemgetter
from academic_search import *

def create_author_yearmap(author_name):
    print("author yearmap", author_name)
    data = get_papers_from_author(author_name)
    papers = {p["Id"]:p for p in data["entities"]}
    return create_papers_yearmap(papers)


def create_papers_yearmap(papers):
    paper_ids = list(papers.keys())
    cite_paper_ids = []
    cite_year_map = {papers[key]["Y"]:[] for key in paper_ids}

    citations = get_citations_from_papers(paper_ids)
    for res in citations["Results"]:
        pid = res[0]["CellID"]
        pyear = papers[pid]["Y"]
        cite_year_map[pyear].extend(res[0]["CitationIDs"])
        cite_paper_ids.extend(res[0]["CitationIDs"])
    print("# or papers = {}, # of citation = {}"
        .format(len(citations["Results"]), len(set(cite_paper_ids))))
    yeardata = get_years_from_papers(list(set(cite_paper_ids)))
    yearmap = {d[0]["CellID"]:d[0]["PublishYear"] for d in yeardata["Results"]}

    bins = range(2000, 2016)
    result = {year:{y:0 for y in bins} for year in bins}
    for pubyear in bins:
        if pubyear in cite_year_map:
            t_counter = Counter([yearmap[pid] for pid in cite_year_map[pubyear]])
            for citeyear in bins:
                result[pubyear][citeyear] = t_counter[citeyear]
    return result

if __name__ == "__main__":
    # field_name = "deep learning"
    # field_name = "compiler"
    # field_name = "assembly language"
    # field_name = "flash memory"
    field_name = "computer graphics"
    citation = [300, 1000]
    data = get_papers_from_field_of_study(field_name, citation)
    papers = {p["Id"]:p for p in data["entities"]}

    print("field yearmap", field_name)
    result = create_papers_yearmap(papers)
    print(result)
    with open('{}.txt'.format(field_name), 'w') as outfile:
        json.dump(result, outfile)
