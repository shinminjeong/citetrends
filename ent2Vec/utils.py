import os, json, itertools
import numpy as np
from collections import Counter
from datetime import datetime
from elasticsearch import Elasticsearch
from multiprocessing import Pool
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

from ent2Vec.names import name_id_pairs

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

def get_fos_name(id):
    es_conn = Elasticsearch(ES_HOSTS)
    res = es_conn.get(index = "fieldsofstudy", doc_type="doc", id=id)
    return "{} ({})".format(res["_source"]["DisplayName"], res["_source"]["Level"])


def get_conf_name(id):
    es_conn = Elasticsearch(ES_HOSTS)
    exits = es_conn.exists(index = "conferenceseries", doc_type="doc", id=id)
    if exits:
        res = es_conn.get(index = "conferenceseries", doc_type="doc", id=id)
    else:
        res = es_conn.get(index = "journals", doc_type="doc", id=id)
    return res["_source"]["NormalizedName"]

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

def search_paper_journal(id):
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
                    "JournalId": id
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
    if type == "journal":
        return search_paper_journal(id)


def get_conf_from_pids(plist):
    # print("get_conf_from_pids", len(plist))
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
    # print("search_pref input paper", len(plist))
    refdict = {p:[] for p in plist}
    query = {
        "size": 10000,
        "query": {
            "terms": {
                "PaperId": plist
            }
        }
    }
    # cnt = []
    reflist = query_es("paperreferences", query)["hits"]
    for ref in reflist:
        # cnt.append(ref["_source"]["PaperId"])
        refdict[ref["_source"]["PaperId"]].append(ref["_source"]["PaperReferenceId"])
    # print("search_pref result", len(set(cnt)))
    return refdict

def search_pfos(plist):
    # print("search_pfos input paper", len(plist))
    refdict = {p:[] for p in plist}
    query = {
        "size": 10000,
        "query": {
            "terms": {
                "PaperId": plist
            }
        }
    }
    reflist = query_es("paperfieldsofstudy", query)["hits"]
    for ref in reflist:
        refdict[ref["_source"]["PaperId"]].append((ref["_source"]["FieldOfStudyId"], ref["_source"]["Similarity"]))
    return refdict


def get_paper_info(id, type):
    yearMap = {}
    titleMap = {}
    if isinstance(id, list):
        for n_id in id:
            res = search_papers(n_id, type)
            for r in res:
                yearMap[int(r["_id"])] = int(r["_source"]["Year"])
                titleMap[int(r["_id"])] = r["_source"]["OriginalTitle"]
    else:
        res = search_papers(id, type)
        yearMap = {int(r["_id"]):int(r["_source"]["Year"]) for r in res}
        titleMap = {int(r["_id"]):r["_source"]["OriginalTitle"] for r in res}
    paperids = list(yearMap.keys())
    div_pids = [paperids[i:i+1000] for i in range(0, len(paperids), 1000)]

    num_threads = 8
    p = Pool(num_threads)
    ref_result = dict()
    ref_result_temp = p.map(search_pref, div_pids)
    for ref_d in ref_result_temp:
        ref_result.update(ref_d)

    confMap = dict()
    conf_result = p.map(get_conf_from_pids, ref_result.values())
    for group in conf_result:
        for r in group:
            if "ConferenceSeriesId" in r["_source"]:
                confMap[int(r["_id"])] = int(r["_source"]["ConferenceSeriesId"])
            if "JournalId" in r["_source"]:
                confMap[int(r["_id"])] = int(r["_source"]["JournalId"])

    fosMap = dict()
    fos_result_temp = p.map(search_pfos, div_pids)
    for fos_d in fos_result_temp:
        fosMap.update(fos_d)

    """
    return dictionary
    {paperid: {
        "Year": year,
        "Title": title,
        "References": [list of venue ids]
        "FoS": [list of (fos_id, score)]
        }
    }
    """
    paper_info_dict = dict()
    for p in paperids:
        paper_info_dict[p] = {
            "Year": yearMap[p], "Title": titleMap[p],
            "References":[], "Fos":fosMap[p]}
        for ref in ref_result[p]:
            if ref in confMap:
                paper_info_dict[p]["References"].append(confMap[ref])
    return paper_info_dict


def save_as_file(filename, dictdata):
    with open("../data/{}.json".format(filename), "w") as outfile:
        json.dump(dictdata, outfile)

def save_plot_result(filename, dictdata):
    with open("../app/app/data/{}.json".format(filename), "w") as outfile:
        json.dump(dictdata, outfile)


def get_set_of_fos_by_year(cname, res):
    fields = []
    for p, r in res.items():
        if "Fos" in r and "Year" in r:
            fields.append((r["Year"], r["Fos"]))
    setfos = {}
    for y, ref in fields:
        # count numpaper each year
        if y in name_id_pairs[cname]["numpaper"]:
            name_id_pairs[cname]["numpaper"][y] += 1
        else:
            name_id_pairs[cname]["numpaper"][y] = 1

        if y not in setfos:
            setfos[y] = []
        setfos[y].extend(ref)
    return setfos

def get_set_of_venues_by_year(cname, res):
    references = []
    for p, r in res.items():
        if "References" in r and "Year" in r:
            references.append((r["Year"], r["References"]))
    venues = {}
    for y, ref in references:
        # count numpaper each year
        if y in name_id_pairs[cname]["numpaper"]:
            name_id_pairs[cname]["numpaper"][y] += 1
        else:
            name_id_pairs[cname]["numpaper"][y] = 1

        if y not in venues:
            venues[y] = []
        venues[y].extend(ref)
    return venues

def aggr_venues(emb_type, data):
    venues = []
    for y, ref in data.items():
        if emb_type == "BoV":
            venues.extend(ref)
        elif emb_type == "BoF":
            venues.extend([r[0] for r in ref])
        else:
            print("(aggr_venues) ERROR: wrong embedding type", emb_type)
    return venues

def get_vector(emb_type, cname, bov, author_venue, year=0, norm_ref=True):
    if emb_type == "BoV":
        return get_vector_cnt(cname, bov, author_venue, year=year, norm_ref=norm_ref)
    elif emb_type == "BoF":
        return get_vector_score(cname, bov, author_venue, year=year, norm_ref=norm_ref)
    else:
        print("(get_vector) ERROR: wrong embedding type", emb_type)

def get_vector_cnt(cname, bov, author_venue, year=0, norm_ref=True):
    c = Counter(author_venue)
    author_arr = [float(c[b]) for b in bov]
    res_arr = np.array(author_arr)
    if year != 0:
        res_arr /= name_id_pairs[cname]["numpaper"][year]
    if norm_ref and len(author_venue) > 0:
        res_arr /= len(author_venue)
    return res_arr

def get_vector_score(cname, bov, author_fos, year=0, norm_ref=True):
    c = {fos:0 for fos in bov}
    for fos, score in author_fos:
        c[fos] += score
    author_arr = [float(c[b]) for b in bov]
    res_arr = np.array(author_arr)
    if year != 0:
        res_arr /= name_id_pairs[cname]["numpaper"][year]
    if norm_ref and len(author_fos) > 0:
        res_arr /= len(author_fos)
    return res_arr


def generate_data():
    for cname, value in name_id_pairs.items():
        print("generate_data", cname)
        data = get_paper_info(value["id"], value["type"])
        save_as_file(cname, data)


def generate_emb_year(emb_type):
    conf_vectors = {}
    for cname in name_id_pairs.keys():
        with open("../data/{}.json".format(cname), "r") as infile:
            data = json.load(infile)
            name_id_pairs[cname]["totalpaper"] = len(data)
            if emb_type == "BoV":
                conf_vectors[cname] = get_set_of_venues_by_year(cname, data)
            elif emb_type == "BoF":
                conf_vectors[cname] = get_set_of_fos_by_year(cname, data)
            else:
                print("(generate_emb_year) ERROR: wrong embedding type", emb_type)
    return conf_vectors

def print_cos_similarity(vec):
    for x,y in itertools.combinations(name_id_pairs.keys(), 2):
        print(x, y, cosine_similarity(vec[x], vec[y]))


def reduce_vec_pca(vec, number_of_venues):
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

def reduce_vec_tsne(vec, p, number_of_venues):
    # first reduce to 50D with PCA
    # print(len(vec), number_of_venues)
    pca = PCA(n_components=50)
    X = np.zeros((len(vec),number_of_venues))
    for i, v in enumerate(vec.values()):
        X[i] = v
    pca.fit(X)
    X_pca = pca.transform(X)

    tsne = TSNE(n_components=2, perplexity=p)
    X_tsne = tsne.fit_transform(X_pca)
    # print("original shape:   ", X.shape)
    # print("transformed shape:", X_tsne.shape)
    result = {}
    for i, k in enumerate(vec.keys()):
        result[k] = X_tsne[i].tolist()
    return result


def download_data_save_as_json():
    return generate_data()


def generate_one_hot_vec(sorted_list_bov, ref_id):
    vec = [1 if b==ref_id else 0 for b in sorted_list_bov]
    return vec


def generate_year_trends_plots(emb_type, name_flag):
    data = generate_emb_year(emb_type)

    ## calculate total bag of venue
    bag_of_venues = set()
    for name, y_venues in data.items():
        venues = aggr_venues(emb_type, y_venues)
        print("{}: len(papers)={}, len(venues)={}, len(set(venues))={}".format(name, name_id_pairs[name]["totalpaper"], len(venues), len(set(venues))))
        print(name_id_pairs[name]["numpaper"])
        [bag_of_venues.add(v) for v in venues]
    print("Total # of venues = ", len(bag_of_venues))
    sorted_list_bov = list(bag_of_venues)
    number_of_venues = len(sorted_list_bov)

    ## generate year_bov for each entity
    vec = {}
    for name, y_venues in data.items():
        for y, ref in y_venues.items():
            vec["{}_{}".format(name, y)] = get_vector(emb_type, name, sorted_list_bov, ref, year=y)

    # generate anchor points
    # for name in ["POPL","PLDI","OOPSLA","ISCA","MICRO","ASPLOS","ICFP","OSDI","ICML","NIPS","WSDM","CIKM","ICWSM","WWW","AAAI"]:
    # for name in ["ICML","NIPS","WSDM","CIKM","ICWSM","WWW","AAAI"]:
    # for name in ["ICML","NIPS"]:
        # vec["{}_Anchor".format(name)] = generate_one_hot_vec(sorted_list_bov, name_id_pairs[name]["id"])
    # print_cos_similarity(vec)
    reduce_and_save(vec, number_of_venues, "{}_{}".format(emb_type, name_flag))


def reduce_and_save(vec, number_of_venues, tag):
    reduce_vec = reduce_vec_pca(vec, number_of_venues)
    # print(reduce_vec)
    save_plot_result("{}_pca".format(tag), reduce_vec)

    for p in [10, 20, 40, 80, 160]:
        reduce_t_vec = reduce_vec_tsne(vec, p, number_of_venues)
        save_plot_result("{}_tsne_{}".format(tag, p), reduce_t_vec)


def generate_emb_paper(emb_type):
    paper_vectors = {}
    for cname in name_id_pairs.keys():
        with open("../data/{}.json".format(cname), "r") as infile:
            data = json.load(infile)
            name_id_pairs[cname]["totalpaper"] = len(data)
            for p, value in data.items():
                if emb_type == "BoV":
                    paper_vectors["{}_{}_{}".format(cname, value["Year"], p)] = value["References"]
                elif emb_type == "BoF":
                    paper_vectors["{}_{}_{}".format(cname, value["Year"], p)] = value["Fos"]
                else:
                    print("(generate_emb_paper) ERROR: wrong embedding type", emb_type)
    return paper_vectors

def generate_indv_paper_plots(emb_type, name_flag):
    data = generate_emb_paper(emb_type)

    bag_of_venues = set()
    sorted_list_bov = list()
    venues = aggr_venues(emb_type, data)
    print("len(papers)={}, len(venues)={}, len(set(venues))={}".format(len(data), len(venues), len(set(venues))))
    [bag_of_venues.add(v) for v in venues]
    print("Total # of venues = ", len(bag_of_venues))
    sorted_list_bov = list(bag_of_venues)
    number_of_venues = len(sorted_list_bov)

    ## generate year_bov for each paper
    vec = {}
    for paper, ref_venuew in data.items():
        if len(ref_venuew) == 0:
            continue
        cname, y, pid = paper.split("_")
        # print(cname, y, pid, len(ref_venuew))
        vec[paper] = get_vector(emb_type, cname, sorted_list_bov, ref_venuew)

    ## generate average vectors by years
    year_data = generate_emb_year(emb_type)
    for cname, y_venues in year_data.items():
        for y, ref in y_venues.items():
            vec["{}_{}_average".format(cname, y)] = get_vector(emb_type, cname, sorted_list_bov, ref, year=y)

    # print(vec)
    reduce_and_save(vec, number_of_venues, "{}_{}".format(emb_type, name_flag))


if __name__ == '__main__':
    # download_data_save_as_json()
    # generate_year_trends_plots("BoF", "nref_Cheng")
    generate_indv_paper_plots("BoF", "nref_conf_pl")
