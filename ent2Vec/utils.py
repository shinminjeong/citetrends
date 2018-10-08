import os, json
from datetime import datetime
from elasticsearch import Elasticsearch
from multiprocessing import Pool

ES_HOSTS = "130.56.249.107:9200"
query_matchall = {
    "query": {
        "match_all": {}
    }
}

def query_es(index, query=query_matchall):
    es_conn = Elasticsearch(ES_HOSTS)
    res = es_conn.search(index = index, body=query, request_timeout=300)
    return res["hits"]["hits"]

# def get_all_conf_ids():
#     res = query_es("conferenceseries")
#     return [r["_source"]["ConferenceSeriesId"] for r in res]
#
# def get_all_journal_ids():
#     res = query_es("journals")
#     return [r["_source"]["JournalId"] for r in res]

def search_papers(id, type):
    if type == "author":
        query = {
            "size": 10000,
            "_source": ["PaperId"],
            "query": {
                "match": {
                    "AuthorId": id
                }
            }
        }
        pids = [r["_source"]["PaperId"] for r in query_es("paperauthoraffiliations", query)]
        query = {
            "size": 10000,
            "_source": ["_id", "Year"],
            "query": {
                "terms": {
                    "PaperId": pids
                }
            }
        }
        return query_es("papers", query)
    if type == "conf":
        query = {
            "size": 10000,
            "_source": ["_id", "Year"],
            "query": {
                "match": {
                    "ConferenceSeriesId": id
                }
            }
        }
        return query_es("papers", query)


def get_conf_from_pids(plist):
    query = {
        "size": 10000,
        "_source": ["ConferenceSeriesId", "JournalId"],
        "query": {
            "terms": {
                "_id": plist
            }
        }
    }
    return query_es("papers", query)

def search_pref_indv(paper):
    refdict = {paper:[]}
    query = {
        "size": 10000,
        "query": {
            "match": {
                "PaperId": paper
            }
        }
    }
    reflist = query_es("paperreferences", query)
    for ref in reflist:
        refdict[ref["_source"]["PaperId"]].append(ref["_source"]["PaperReferenceId"])
    return refdict

def search_pref(plist):
    refdict = {p:[] for p in plist}
    query = {
        "size": 10000,
        "query": {
            "terms": {
                "PaperId": plist
            }
        }
    }
    reflist = query_es("paperreferences", query)
    for ref in reflist:
        refdict[ref["_source"]["PaperId"]].append(ref["_source"]["PaperReferenceId"])
    return refdict

def get_paper_ref(id, type):
    res = search_papers(id, type)
    yearMap = {int(r["_id"]):int(r["_source"]["Year"]) for r in res}
    paperids = list(yearMap.keys())

    num_threads = 8
    p = Pool(num_threads)
    ref_result = p.apply_async(search_pref, [paperids]).get()

    confMap = dict()
    conf_result = p.map(get_conf_from_pids, ref_result.values())
    for group in conf_result:
        for r in group:
            if "ConferenceSeriesId" in r["_source"]:
                confMap[int(r["_id"])] = int(r["_source"]["ConferenceSeriesId"])
            if "JournalId" in r["_source"]:
                confMap[int(r["_id"])] = int(r["_source"]["JournalId"])
    """
    return dictionary
    {paperid: {"Year": year, "References": [list of venue ids]}}
    """
    paper_ref_dict = dict()
    for p in paperids:
        paper_ref_dict[p] = {"Year": yearMap[p], "References":[]}
        for ref in ref_result[p]:
            if ref in confMap:
                paper_ref_dict[p]["References"].append(confMap[ref])
    return paper_ref_dict

# DEBUG = False
# def get_paper_ref(id, type):
#     t1 = datetime.now()
#     res = search_papers(id, type)
#     t2 = datetime.now()
#     if DEBUG:
#         print((t2-t1).total_seconds(),
#         "Get paper ids from a venue (search papers) or from an author (search paa and papers)")
#
#     yearMap = {int(r["_id"]):int(r["_source"]["Year"]) for r in res}
#     paperids = list(yearMap.keys())
#
#     num_threads = 1
#     p = Pool(num_threads)
#
#     t1 = datetime.now()
#     # ref_result = p.map_async(search_pref_indv, paperids).get()
#     ref_result = p.map_async(search_pref, [paperids]).get()
#     t2 = datetime.now()
#     if DEBUG:
#         print((t2-t1).total_seconds(),
#         "Get paper references from paper ids (search pref). # of threads = {}".format(num_threads))
#
#     confMap = dict()
#     aggr_list = []
#     for refs in ref_result:
#         for l in refs.values():
#             aggr_list.extend(l)
#     t1 = datetime.now()
#     conf_result = p.map_async(get_conf_from_pids, [list(set(aggr_list))]).get()
#     t2 = datetime.now()
#     if DEBUG:
#         print((t2-t1).total_seconds(),
#         "Get venue of {} paper references (search papers). # of threads = {}".format(len(aggr_list), num_threads))
#
#     for group in conf_result:
#         for r in group:
#             if "ConferenceSeriesId" in r["_source"]:
#                 confMap[int(r["_id"])] = int(r["_source"]["ConferenceSeriesId"])
#             if "JournalId" in r["_source"]:
#                 confMap[int(r["_id"])] = int(r["_source"]["JournalId"])
#
#     """
#     return dictionary
#     {paperid: {"Year": year, "References": [list of venue ids]}}
#     """
#     paper_ref_dict = dict()
#     for p in paperids:
#         paper_ref_dict[p] = {"Year": yearMap[p], "References":[]}
#         for ref in ref_result[p]:
#             if ref in confMap:
#                 paper_ref_dict[p]["References"].append(confMap[ref])
#     return paper_ref_dict


if __name__ == '__main__':
    get_paper_ref(1120384002, "conf")
    # get_paper_ref(1127352206, "conf")
