import os,sys,json
import requests
from collections import Counter
from datetime import datetime
import xml.etree.ElementTree as ET

data_path = "../nsf_grant"
nsf_api_prefix = "https://api.nsf.gov/services/v1/awards/"

grant_div_name = {
"010": "Office of the Director",
"020": "Office of Information &amp; Resource Mgmt",
"030": "Directorate for Mathematical &amp; Physical Scien",
"040": "Directorate for Social, Behav &amp; Economic Scie",
"050": "Directorate for Computer &amp; Info Scie &amp; Enginr",
"060": "Directorate for Geosciences",
"070": "Directorate for Engineering",
"080": "Directorate for Biological Sciences",
"100": "Office of Budget, Finance, &amp; Award Management",
"110": "Directorate for Education and Human Resource",
"120": "National Coordination Office"
}

def count_numgrant_year(years):
    yamt = {y:{} for y in years}
    ymap = {y:[] for y in years}
    for year in years:
        path = os.path.join(data_path, str(year))
        for filename in sorted(os.listdir(path)):
            award_id, file_format = filename.split(".")
            if file_format == "json":
                continue
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

def count_numgrant_division_year(years):
    yamt = {y:{} for y in years}
    ymap = {y:[] for y in years}
    for year in years:
        path = os.path.join(data_path, str(year))
        for filename in sorted(os.listdir(path)):
            award_id, file_format = filename.split(".")
            if file_format == "json":
                continue
            try:
                root = ET.parse(os.path.join(data_path, str(year), filename)).getroot()
            except:
                # print("[ET parse error]", os.path.join(data_path, str(year), filename))
                pass
            grant_type = root.find("Award").find("AwardInstrument").find("Value").text
            # if grant_type != "Continuing grant":
            if grant_type != "Standard Grant":
                continue
            code = root.find("Award").find("Organization").find("Code").text[:3]
            grant_div_type = grant_div_name[code] if code in grant_div_name else "Other"
            grant_amount = int(root.find("Award").find("AwardAmount").text)
            ymap[year].append(grant_div_type)
            if grant_div_type in yamt[year]:
                yamt[year][grant_div_type] += grant_amount
            else:
                yamt[year][grant_div_type] = 0

    with open(os.path.join(data_path, "summary_stnd_div.json"), 'w') as outfile:
        data = {y:{"count":Counter(values), "amount":yamt[y]} for y, values in ymap.items()}
        json.dump(data, outfile)


def load_grant_data(filename):
    data = json.load(open(os.path.join(data_path, filename), 'r'))
    return data

def download_num_pub(years):
    for year in years:
        path = os.path.join(data_path, str(year))
        for filename in sorted(os.listdir(path)):
            award_id, file_format = filename.split(".")
            if file_format == "json" or os.path.isfile(os.path.join(path, "{}.json".format(award_id))):
                continue
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


def count_pub_amount(year):
    awards = dict()
    path = os.path.join(data_path, str(year))
    for filename in sorted(os.listdir(path)):
        award_id, file_format = filename.split(".")
        if file_format == "json":
            continue
        try:
            root = ET.parse(os.path.join(data_path, str(year), filename)).getroot()
        except:
            # print("[ET parse error]", os.path.join(data_path, str(year), filename))
            continue
        grant_type = root.find("Award").find("AwardInstrument").find("Value").text
        grant_amount = int(root.find("Award").find("AwardAmount").text)
        grant_start = datetime.strptime(root.find("Award").find("AwardEffectiveDate").text, "%m/%d/%Y")
        grant_end = datetime.strptime(root.find("Award").find("AwardExpirationDate").text, "%m/%d/%Y")
        code = root.find("Award").find("Organization").find("Code").text[:3]
        grant_div_type = grant_div_name[code] if code in grant_div_name else "Other"

        num_pubs = 0
        pubs = json.load(open(os.path.join(path, "{}.json".format(award_id)), 'r'))
        if "award" not in pubs["response"]:
            print("[No award error]", award_id)
            continue
        if len(pubs["response"]["award"]) > 0:
            num_pubs = len(pubs["response"]["award"][0]["publicationResearch"])
        awards[award_id] = {
            "type": grant_type,
            "amount": grant_amount,
            "div": grant_div_type,
            "num_pubs": num_pubs,
            "duration": (grant_end-grant_start).days
        }
    outfile = open(os.path.join(path, "numpub.json"), 'w')
    json.dump(awards, outfile)


def load_numpub_data(year):
    data = json.load(open(os.path.join(data_path, str(year), "numpub.json"), 'r'))
    return data

if __name__ == '__main__':
    years = range(2000, 2020, 1)
    # count_numgrant_division_year(years)
    # count_numgrant_year(years)
    # download_num_pub(years)
    count_pub_amount(2010)
    count_pub_amount(2011)
    count_pub_amount(2000)
