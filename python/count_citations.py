import os, sys, json, requests
import csv, time
import itertools
from datetime import datetime
from collections import Counter
from operator import itemgetter
from academic_search import *

if __name__ == "__main__":
    # field_name = "deep learning"
    # field_name = "compiler"
    # field_name = "assembly language"
    field_name = "flash memory"
    # field_name = "computer graphics"
    print("field yearmap", field_name)

    maxrange = 1000
    rangebin = 50
    result = {}
    citeranges = range(rangebin, maxrange, rangebin)
    for c in citeranges:
        citation = [c, c+rangebin]
        if c + rangebin == maxrange:
            citation = [c, 1000000]
        data = get_papers_from_field_of_study(field_name, citation)
        numpaper = 0
        numcite = 0
        if "entities" in data:
            numpaper = len(data["entities"])
            numcite = sum([p["CC"] for p in data["entities"]])
        print(citation, numpaper, numcite)
        result[c] = {
            "numpaper": numpaper,
            "numcite": numcite,
            "avgcite": numcite/numpaper if numcite > 0 else 0
        }
        time.sleep(1)

    with open('{}_stat.txt'.format(field_name), 'w') as outfile:
        json.dump(result, outfile)
