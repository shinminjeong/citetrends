import os, json, itertools
import numpy as np
from collections import Counter
from datetime import datetime
from elasticsearch import Elasticsearch
from multiprocessing import Pool
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

ES_HOSTS = "130.56.249.107:9200"
query_matchall = {
    "query": {
        "match_all": {}
    }
}

def query_es(index, query=query_matchall):
    es_conn = Elasticsearch(ES_HOSTS)
    res = es_conn.search(index = index, body=query, request_timeout=300)
    return res["hits"]

def search_paper_author(id):
    result = []
    count = 0
    total = size = 1000
    while count < total:
        query = {
            "from": count,
            "size": size,
            "_source": ["PaperId"],
            "query": {
                "match": {
                    "AuthorId": id
                }
            }
        }
        resauthors = query_es("paperauthoraffiliations", query)
        total = resauthors["total"]
        pids = [r["_source"]["PaperId"] for r in resauthors["hits"]]
        query = {
            "size": 10000,
            "_source": ["_id", "Year", "OriginalTitle"],
            "query": {
                "terms": {
                    "PaperId": pids
                }
            }
        }
        count += size
        result.extend(query_es("papers", query)["hits"])
    return result

def search_paper_conf(id):
    result = []
    count = 0
    total = size = 1000
    while count < total:
        query = {
            "from": count,
            "size": size,
            "_source": ["_id", "Year", "OriginalTitle"],
            "query": {
                "match": {
                    "ConferenceSeriesId": id
                }
            }
        }
        resconf = query_es("papers", query)
        total = resconf["total"]
        result.extend(resconf["hits"])
        count += size
    print(len(result))
    return result


def search_papers(id, type):
    if type == "author":
        return search_paper_author(id)
    if type == "conf":
        return search_paper_conf(id)


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
    return query_es("papers", query)["hits"]


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
    reflist = query_es("paperreferences", query)["hits"]
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
    reflist = query_es("paperreferences", query)["hits"]
    for ref in reflist:
        refdict[ref["_source"]["PaperId"]].append(ref["_source"]["PaperReferenceId"])
    return refdict

def get_paper_ref(id, type):
    res = search_papers(id, type)
    yearMap = {int(r["_id"]):int(r["_source"]["Year"]) for r in res}
    titleMap = {int(r["_id"]):r["_source"]["OriginalTitle"] for r in res}
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
    {paperid: {"Year": year, "Title": title, "References": [list of venue ids]}}
    """
    paper_ref_dict = dict()
    for p in paperids:
        paper_ref_dict[p] = {"Year": yearMap[p], "Title": titleMap[p], "References":[]}
        for ref in ref_result[p]:
            if ref in confMap:
                paper_ref_dict[p]["References"].append(confMap[ref])
    return paper_ref_dict


def save_as_file(filename, dictdata):
    with open("../data/{}.json".format(filename), "w") as outfile:
        json.dump(dictdata, outfile)

def save_plot_result(filename, dictdata):
    with open("../canvas/data/{}.json".format(filename), "w") as outfile:
        json.dump(dictdata, outfile)


def get_set_of_venues_by_year(res):
    references = []
    for p, r in res.items():
        if "References" in r and "Year" in r:
            references.append((r["Year"], r["References"]))
    venues = {}
    for y, ref in references:
        if y not in venues:
            venues[y] = []
        venues[y].extend(ref)
    return venues

def aggr_venues(data):
    venues = []
    for y, ref in data.items():
        venues.extend(ref)
    return venues

def get_vector(name, bov, author_venue, norm=False):
    c = Counter(author_venue)
    author_arr = [[float(c[b]) for b in bov]]
    if norm:
        return np.array(author_arr)/name_id_pairs[name]["numpaper"]
    else:
        return np.array(author_arr)

name_id_pairs = {
    # "steve_blackburn": {"id": 2146610949, "type":"author"},
    # "kathryn_mckinley": {"id": 2115847858, "type":"author"},
    # "james_bornholt": {"id": 2026265091, "type":"author"},
    # "julian_dolby": {"id": 2780161863, "type":"author"},
    # "perry_cheng": {"id": 2140441920, "type":"author"},
    # "julian_mcauley": {"id": 2041520510, "type":"author"},
    "ICWSM": {"id": 1124713781, "type":"conf"},
    "POPL": {"id": 1160032607, "type":"conf"},
    "PLDI": {"id": 1127352206, "type":"conf"},
    "WSDM": {"id": 1120384002, "type":"conf"},
    "CIKM": {"id": 1194094125, "type":"conf"},
    "ISCA": {"id": 1131341566, "type":"conf"},
    "MICRO": {"id": 1150919317, "type":"conf"},
    "ASPLOS": {"id": 1174091362, "type":"conf"},
    "OSDI": {"id": 1185109434, "type":"conf"},
    "ICML": {"id": 1180662882, "type":"conf"},
    "NIPS": {"id": 1127325140, "type":"conf"},
    "OOPSLA": {"id": 1138732554, "type":"conf"},
    "WWW": {"id": 1135342153, "type":"conf"},
    "AAAI": {"id": 1184914352, "type":"conf"},
}

def generate_data():
    for cname, value in name_id_pairs.items():
        data = get_paper_ref(value["id"], value["type"])
        save_as_file(cname, data)


def generate_bov():
    conf_vectors = {}
    for cname in name_id_pairs.keys():
        with open("../data/{}.json".format(cname), "r") as infile:
            data = json.load(infile)
            name_id_pairs[cname]["numpaper"] = len(data)
            conf_vectors[cname] = get_set_of_venues_by_year(data)
    return conf_vectors

def print_cos_similarity(vec):
    for x,y in itertools.combinations(name_id_pairs.keys(), 2):
        print(x, y, cosine_similarity(vec[x], vec[y]))


def reduce_vec_pca(vec):
    pca = PCA(n_components=2)
    X = np.zeros((len(vec),number_of_venues))
    for i, v in enumerate(vec.values()):
        X[i] = v
    pca.fit(X)
    X_pca = pca.transform(X)
    # print("original shape:   ", X.shape)
    # print("transformed shape:", X_pca.shape)
    result = {}
    for i, k in enumerate(vec.keys()):
        result[k] = X_pca[i].tolist()
    return result

def reduce_vec_tsne(vec, p):
    tsne = TSNE(n_components=2, perplexity=p)
    X = np.zeros((len(vec),number_of_venues))
    for i, v in enumerate(vec.values()):
        X[i] = v
    X_tsne = tsne.fit_transform(X)
    # print("original shape:   ", X.shape)
    # print("transformed shape:", X_tsne.shape)
    result = {}
    for i, k in enumerate(vec.keys()):
        result[k] = X_tsne[i].tolist()
    return result


if __name__ == '__main__':
    # generate_data()

    data = generate_bov()

    bag_of_venues = set()
    sorted_list_bov = list()
    for name, y_venues in data.items():
        venues = aggr_venues(y_venues)
        print("{}: len(papers)={}, len(venues)={}, len(set(venues))={}".format(name, name_id_pairs[name]["numpaper"], len(venues), len(set(venues))))
        [bag_of_venues.add(v) for v in venues]
    print("Total # of venues = ", len(bag_of_venues))
    sorted_list_bov = list(bag_of_venues)
    number_of_venues = len(sorted_list_bov)

    ## generate bov for each entity
    vec = {}
    avg_vec = {}
    print(data.keys())
    for name, y_venues in data.items():
        vec[name] = get_vector(name, sorted_list_bov, aggr_venues(y_venues))
        avg_vec[name] = get_vector(name, sorted_list_bov, aggr_venues(y_venues), True)
    # print_cos_similarity(vec)
    # print(reduce_vec_dim(vec))

    ## generate year_bov for each entity
    vec = {}
    for name, y_venues in data.items():
        for y, ref in y_venues.items():
            vec["{}_{}".format(name, y)] = get_vector(name, sorted_list_bov, ref)
    # print_cos_similarity(vec)
    reduce_vec = reduce_vec_pca(vec)
    # print(reduce_vec)
    save_plot_result("pca_vec", reduce_vec)

    for i in [1,2,3]:
        for p in [5, 10, 20, 40, 80]:
            reduce_t_vec = reduce_vec_tsne(vec, p)
            # print(reduce_vec)
            save_plot_result("tsne_vec_{}_{}".format(i, p), reduce_t_vec)
