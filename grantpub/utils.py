import os,sys,json
import requests
from collections import Counter
import xml.etree.ElementTree as ET

data_path = "../nsf_grant"
nsf_api_prefix = "https://api.nsf.gov/services/v1/awards/"

def count_numgrant_year(years):
    yamt = {y:{} for y in years}
    ymap = {y:[] for y in years}
    for year in years:
        path = os.path.join(data_path, str(year))
        for filename in sorted(os.listdir(path)):
            try:
                root = ET.parse(os.path.join(data_path, str(year), filename)).getroot()
            except:
                # print("[ET parse error]", os.path.join(data_path, str(year), filename))
                pass
            grant_type = root.find("Award").find("AwardInstrument").find("Value").text
            grant_amount = int(root.find("Award").find("AwardAmount").text)
            ymap[year].append(grant_type)
            if grant_type in yamt[year]:
                yamt[year][grant_type] += grant_amount
            else:
                yamt[year][grant_type] = 0

    with open(os.path.join(data_path, "summary.json"), 'w') as outfile:
        data = {y:{"count":Counter(values), "amount":yamt[y]} for y, values in ymap.items()}
        json.dump(data, outfile)

    # return {y:Counter(values) for y, values in ymap.items()}, yamt

def load_grant_data(years):
    data = json.load(open(os.path.join(data_path, "summary.json"), 'r'))
    return data

def download_num_pub(years):
    for year in years:
        path = os.path.join(data_path, str(year))
        for filename in sorted(os.listdir(path)):
            award_id = filename.split(".")[0]
            print(award_id)
            rsp = query_nsf(award_id)
            outfile = open(os.path.join(path, "{}.json".format(award_id)), 'w')
            json.dump(rsp, outfile)

def query_nsf(award_id):
    payload = {"printFields": "publicationResearch"}
    response = requests.get("{}{}.json".format(nsf_api_prefix, award_id), params=payload)
    # print('curl: ' + response.url)
    # print('return statue: ' + str(response.status_code))
    if response.status_code != 200:
        print("return statue: " + str(response.status_code))
        print("ERROR: problem with the request.")
        exit()
    return json.loads((response.content).decode("utf-8"))


if __name__ == '__main__':
    years = range(2009, 2010, 1)
    # count_numgrant_year(years)
    download_num_pub(years)
