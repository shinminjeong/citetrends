import os, sys, json, requests
import csv, time
import itertools
from datetime import datetime
from collections import Counter
from operator import itemgetter
from academic_search import *

def read_data():
    datapath = "../data/0804-filtered.csv"
    reader = csv.reader(open(datapath), delimiter=',', skipinitialspace=True)
    next(reader) # skip the first line
    data = dict((r[0], {
        "Type": r[1],
        "Authors": r[2],
        "Title": r[3],
        "Year": r[4],
        "Outlet": r[5]
    }) for r in reader if len(r) > 6 and r[0] != "")
    return data

if __name__ == "__main__":
    data = read_data()
    for p,v in data.items():
        title = v["Title"]
        try:
            paper = get_paperinfo_from_title(title.strip())
            print(p, paper["entities"][0]["Id"])
        except Exception as e:
            print(p, "error", title)
            #print(e)
        time.sleep(1)
