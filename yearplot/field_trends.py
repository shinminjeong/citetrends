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
    pub_year_map = {papers[key]["Y"]:[] for key in paper_ids}
    cite_year_map = {papers[key]["Y"]:[] for key in paper_ids}

    citations = get_citations_from_papers(paper_ids)
    for res in citations["Results"]:
        pid = res[0]["CellID"]
        pyear = papers[pid]["Y"]
        pub_year_map[pyear].append(pid)
        cite_year_map[pyear].extend(res[0]["CitationIDs"])
        cite_paper_ids.extend(res[0]["CitationIDs"])
    print("# or papers = {}, # of citation = {}"
        .format(len(citations["Results"]), len(set(cite_paper_ids))))
    yeardata = get_years_from_papers(list(set(cite_paper_ids)))
    yearmap = {d[0]["CellID"]:d[0]["PublishYear"] for d in yeardata["Results"]}

    bins = range(1940, 2019)
    result = {year:{y:0 for y in bins} for year in bins}
    for pubyear in bins:
        if pubyear in cite_year_map:
            t_counter = Counter([yearmap[pid] for pid in cite_year_map[pubyear]])
            for citeyear in bins:
                result[pubyear][citeyear] = t_counter[citeyear]
    return result, pub_year_map

if __name__ == "__main__":
    # field_name = "deep learning"
    # field_name = "compiler"
    # field_name = "assembly language"
    # field_name = "flash memory"
    # field_name = "computer graphics"
    # citation = [300, 1000]
    # data = get_papers_from_field_of_study(field_name, citation)
    # papers = {p["Id"]:p for p in data["entities"]}

    # print("field yearmap", field_name)
    result = {}
    # citeyear, pubyear = create_papers_yearmap(papers)
    # arthor_name = "brian p schmidt"
    # arthor_name = "frank wilczek"
    # arthor_name = "george f smoot"
    # arthor_name = "yoichiro nambu"
    arthor_name = "peter w higgs"
    citeyear, pubyear = create_author_yearmap(arthor_name)

    for k in citeyear.keys():
        result[k] = {
            "pub": len(pubyear[k]) if k in pubyear else 0,
            "cite": citeyear[k]
        }
    print(result)
    # with open('computer_graphics/{}_{}.txt'.format(citation[0], citation[1]), 'w') as outfile:
    #     json.dump(result, outfile)
    with open('{}.txt'.format(arthor_name), 'w') as outfile:
        json.dump(result, outfile)
