import os, json, itertools
from utils import query_es

ID_CS = 41008148
NAME_CS = "Computer Science"

def get_children_fos(fos_id):
    query = {
        "size": 10000,
        "_source": ["ChildFieldOfStudyId"],
        "query": {
            "match": {
                "FieldOfStudyId": fos_id
            }
        }
    }
    res = query_es("fieldofstudychildren", query)["hits"]
    children = [r["_source"]["ChildFieldOfStudyId"] for r in res]
    return children

def get_fos_info(fos_id):
    query = {
        "_source": ["DisplayName", "PaperCount", "Level"],
        "size": 20,
        "query": {
            "match" : {
                "FieldOfStudyId": fos_id
            }
        }
    }
    res = query_es("fieldsofstudy", query)["hits"][0]["_source"]
    return res["DisplayName"], res["PaperCount"], res["Level"]


if __name__ == '__main__':
    data_1 = get_children_fos(ID_CS) # level 0
    print("0_{}".format(NAME_CS))
    for fid_1 in data_1:
        name_1, num, level = get_fos_info(fid_1) # level 1
        print("0_{}.{}_{},{}".format(NAME_CS, level, name_1.replace(".", "_"), num))
        data_2 = get_children_fos(fid_1)
        for fid_2 in data_2:
            name_2, num, level = get_fos_info(fid_2) # level 1
            print("0_{}.1_{}.{}_{},{}".format(NAME_CS, name_1.replace(".", "_"), level, name_2.replace(".", "_"), num))
