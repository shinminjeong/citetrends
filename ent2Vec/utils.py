import os, json
from elasticsearch import Elasticsearch

ES_HOSTS = "130.56.248.7:9200"
query_matchall = {
    "query": {
        "match_all": {}
    }
}

def query_es(index, query=query_matchall):
    es_conn = Elasticsearch(ES_HOSTS)
    res = es_conn.search(index = index, body=query)
    return res["hits"]["hits"]

# def get_all_conf_ids():
#     res = query_es("conferenceseries")
#     return [r["_source"]["ConferenceSeriesId"] for r in res]
#
# def get_all_journal_ids():
#     res = query_es("journals")
#     return [r["_source"]["JournalId"] for r in res]

def query_author_id(id):
    query = {
        "size": 1000,
        "_source": ["References.JournalId", "References.ConferenceSeriesId", "Year"],
        "query": {
            "match": {
                "Authors.AuthorId": id
            }
        }
    }
    return query_es("paper_info", query)
