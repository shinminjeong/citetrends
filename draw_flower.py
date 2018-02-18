import os, json, requests
from datetime import datetime
from collections import Counter
from operator import itemgetter
from academic_search import *

def extract_author_ids(paper_ids):
    authors = get_authors_from_papers(paper_ids)
    authors_score = {}
    for ath in authors["Results"]:
        try:
            if ego_id not in ath[0]["AuthorIDs"]:   # remove self citation
                for author in ath[0]["AuthorIDs"]:
                    score = 1.0/len(ath[0]["AuthorIDs"])
                    if author in authors_score:
                        authors_score[author] += score
                    else:
                        authors_score[author] = score
        except Exception as e:
            pass
    mostcommon = sorted(authors_score.items(), key=itemgetter(1), reverse=True)[:30]
    author_info = get_author_information([a[0] for a in mostcommon])
    author_name = {a[0]["CellID"]:a[0]["Name"] for a in author_info["Results"]}
    print("Top 10 authors")
    print([(author_name[key], authors_score[key]) for key in author_name.keys()])


####################################################
ego_name = "lexing xie"
print("------------ getting papers from",ego_name, datetime.now())
papers = get_papers_from_author(ego_name)
ego_id = [a["AuId"] for a in papers["entities"][0]["AA"] if a["AuN"] == ego_name][0]

print("------------ getting citation from paper list", datetime.now())
paper_ids = [e["Id"] for e in papers["entities"]]
print("author: {}, id: {}".format(ego_name, ego_id))
print("number of papers:",  len(paper_ids))
citations = get_citations_from_papers(paper_ids)
references = [e["RId"] if "RId" in e else [] for e in papers["entities"]]

print("------------ getting authors from citations", datetime.now())
cite_paper_ids = []
for res in citations["Results"]:
    cite_paper_ids.extend(res[0]["CitationIDs"])
extract_author_ids(cite_paper_ids)

print("------------ getting authors from references", datetime.now())
ref_paper_ids = []
for res in references:
    ref_paper_ids.extend(res)
extract_author_ids(ref_paper_ids)

print("------------ finish!!!", datetime.now())
####################################################
