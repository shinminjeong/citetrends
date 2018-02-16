import os, json, requests
import http.client, urllib.request, urllib.parse, urllib.error, base64
from datetime import datetime
from collections import Counter

MAS_URL_PREFIX = "http://westus.api.cognitive.microsoft.com"
headers = {
    # Request headers
    'Ocp-Apim-Subscription-Key': 'a27d17cc1a6044f5bb6accf68e10eefa',
}

def query_academic_search(type, url, query):
    if type == "get":
        response = requests.get(url, params=urllib.parse.urlencode(query), headers=headers)
    elif type == "post":
        response = requests.post(url, json=query, headers=headers)
    if response.status_code != 200:
        print("return statue: " + str(response.status_code))
        print("ERROR: problem with the request.")
        print(response.content)
        exit()
    return json.loads((response.content).decode("utf-8"))

def get_papers_from_author(author):
    url = os.path.join(MAS_URL_PREFIX, "academic/v1.0/evaluate")
    query = {
      "expr": "Composite(AA.AuN=='{}')".format(author),
      "count": 20,
      "offset": 0,
      "attributes": "prob,Id,Ti,Y,CC,AA.AuN,AA.AuId,RId"
    }
    data = query_academic_search("get", url, query)
    return data

def get_citations_from_papers(paper_ids):
    url = os.path.join(MAS_URL_PREFIX, "academic/v1.0/graph/search?mode=json")
    query = {
      "path": "/paper",
      "paper": {
        "type": "Paper",
        "id": paper_ids,
        "select": [ "OriginalTitle", "CitationCount", "CitationIDs" ]
      }
    }
    data = query_academic_search("post", url, query)
    return data

def get_authors_from_papers(paper_ids):
    url = os.path.join(MAS_URL_PREFIX, "academic/v1.0/graph/search?mode=json")
    query = {
      "path": "/paper",
      "paper": {
        "type": "Paper",
        "id": paper_ids,
        "select": [ "AuthorIDs" ]
      }
    }
    data = query_academic_search("post", url, query)
    return data

def get_author_information(author_ids):
    url = os.path.join(MAS_URL_PREFIX, "academic/v1.0/graph/search?mode=json")
    query = {
      "path": "/author",
      "author": {
        "type": "Author",
        "id": author_ids,
        "select": [ "Name" ]
      }
    }
    data = query_academic_search("post", url, query)
    return data

####################################################
author_name = "lexing xie"
print("------------ getting papers from", author_name, datetime.now())
papers = get_papers_from_author(author_name)
# print(json.dumps(papers, indent=2))
print("------------ getting citation from paper list", datetime.now())
paper_ids = [e["Id"] for e in papers["entities"]]
print("author:", author_name)
print("number of papers:",  len(paper_ids))
# print(paper_ids[:5])
citations = get_citations_from_papers(paper_ids)
references = [e["RId"] if "RId" in e else [] for e in papers["entities"]]
# print(json.dumps(citations, indent=2))

print("------------ getting authors from citations", datetime.now())
cite_counter = Counter()
for res in citations["Results"]:
    # print(res[0])
    cite_paper_ids = res[0]["CitationIDs"]
    authors = get_authors_from_papers(cite_paper_ids)
    authors_ids = []
    for ath in authors["Results"]:
        authors_ids.extend(ath[0]["AuthorIDs"])
    cite_counter += Counter(authors_ids)
mostcommon = cite_counter.most_common(10)
author_info = get_author_information([a[0] for a in mostcommon])
author_name = {a[0]["CellID"]:a[0]["Name"] for a in author_info["Results"]}
print("Top 10 authors in citation papers")
print([(author_name[key], cite_counter[key]) for key in author_name.keys()])

print("------------ getting authors from references", datetime.now())
ref_counter = Counter()
for res in references:
    # print(res)
    ref_paper_ids = res
    authors = get_authors_from_papers(ref_paper_ids)
    authors_ids = []
    for ath in authors["Results"]:
        authors_ids.extend(ath[0]["AuthorIDs"])
    ref_counter += Counter(authors_ids)
mostcommon = ref_counter.most_common(10)
author_info = get_author_information([a[0] for a in mostcommon])
author_name = {a[0]["CellID"]:a[0]["Name"] for a in author_info["Results"]}
print("Top 10 authors in reference papers")
print([(author_name[key], ref_counter[key]) for key in author_name.keys()])


print("------------ finish!!!", datetime.now())
####################################################
