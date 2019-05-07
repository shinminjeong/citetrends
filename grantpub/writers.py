import os
from datetime import datetime
from collections import Counter
import pandas as pd
import xml.etree.ElementTree as ET

data_path = "../nsf_grant"
outf_path = "../nsf_sum"
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

def read_xml_files(years):
    df_cols = ["year", "id", "title", "type", "amount", "code", "start", "end", "firstname", "lastname", "email", "role", "institution"]

    for year in years:
        out_df = pd.DataFrame(columns = df_cols)
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
            award = grant_type = root.find("Award")
            title = award.find("AwardTitle").text
            grant_type = award.find("AwardInstrument").find("Value").text
            grant_amount = int(award.find("AwardAmount").text)
            code = award.find("Organization").find("Code").text
            grant_start = award.find("AwardEffectiveDate").text
            grant_end = award.find("AwardExpirationDate").text

            inst = award.find("Institution")
            if inst:
                inst_name = inst.find("Name").text
            else:
                inst_name = ""
                print("No institution name", award_id)


            investigators = award.findall("Investigator")
            if not investigators:
                print("No investigator", award_id)
                continue
            for investigator in investigators:
                inv_fname = inv_lname = inv_eaddr = inv_role = ""
                inv_fname = investigator.find("FirstName").text
                inv_lname = investigator.find("LastName").text
                inv_eaddr = investigator.find("EmailAddress").text
                inv_role = investigator.find("RoleCode").text

                # df_cols = ["year", "id", "title", "type", "amount", "code", "start", "end", "firstname", "lastname", "email", "role", "institution"]
                data = [year, award_id, title, grant_type, grant_amount, code, grant_start, grant_end, inv_fname, inv_lname, inv_eaddr, inv_role, inst_name]
                out_df = out_df.append(pd.Series(data, index = df_cols), ignore_index = True)

        out_df.to_csv(os.path.join(outf_path, "summary_{}.csv".format(year)), sep=',', index=None, header=True)


def num_grants_each_year(years):
    # data = []
    for year in years:
        data = []
        path = os.path.join(outf_path, "summary_{}.csv".format(year))
        data.append(pd.read_csv(path, header=0))
        concat_df = pd.concat(data, ignore_index = True)

        groups = concat_df.groupby(["firstname", "lastname", "email"])
        num_grants = []
        for name, value in groups:
            num_grants.append(value.shape[0])
            # if value.shape[0] > 1:
            #     print(name)
            #     print(value.loc[:, ["year", "type", "amount", "code"]])
        cnt = Counter(num_grants)
        print(year, end =",")
        for i in range(1, 10, 1):
            print(cnt[i], end =",")
        print()


def num_people_num_grants(years):
    data = []
    for year in years:
        path = os.path.join(outf_path, "summary_{}.csv".format(year))
        data.append(pd.read_csv(path, header=0))
    concat_df = pd.concat(data, ignore_index = True)

    print("total number of grants", concat_df["id"].count())
    groups = concat_df.groupby(["firstname", "lastname", "email"])
    print("total number of people", groups["firstname", "lastname", "email"].count())

    num_grants = []
    for name, value in groups:
        num_grants.append(value.shape[0])
        # if value.shape[0] > 1:
        #     print(name)
        #     print(value.loc[:, ["year", "type", "amount", "code"]])
    print(len(num_grants))
    cnt = Counter(num_grants)
    for i in range(1, 31, 1):
        print(i, ", ", cnt[i])


def num_pi_each_year(years):
    for year in years:
        data = []
        path = os.path.join(outf_path, "summary_{}.csv".format(year))
        data.append(pd.read_csv(path, header=0))
        concat_df = pd.concat(data, ignore_index = True)

        groups = concat_df.groupby(["year", "id", "title", "amount"])
        # print("total number of award", groups["year", "id", "title", "amount"].count())

        num_grants = []
        amount_single_stnd = []
        amount_single_cont = []
        amount_single_other = []
        amount_multiple_same_stnd = []
        amount_multiple_same_cont = []
        amount_multiple_same_other = []
        amount_multiple_diff_stnd = []
        amount_multiple_diff_cont = []
        amount_multiple_diff_other = []
        for name, value in groups:
            num_grants.append(value.shape[0])
            grant_amount = value.amount.values[0]
            if value.shape[0] == 1:
                if value.type.values[0] == "Standard Grant":
                    amount_single_stnd.append(grant_amount)
                elif value.type.values[0] == "Continuing grant":
                    amount_single_cont.append(grant_amount)
                else:
                    amount_single_other.append(grant_amount)
            else:
                emails = [str(e).split("@")[-1] for e in value.email.values]
                # print(emails)
                if len(set(emails)) == 1:
                    if value.type.values[0] == "Standard Grant":
                        amount_multiple_same_stnd.append(grant_amount)
                    elif value.type.values[0] == "Continuing grant":
                        amount_multiple_same_cont.append(grant_amount)
                    else:
                        amount_multiple_same_other.append(grant_amount)
                else:
                    if value.type.values[0] == "Standard Grant":
                        amount_multiple_diff_stnd.append(grant_amount)
                    elif value.type.values[0] == "Continuing grant":
                        amount_multiple_diff_cont.append(grant_amount)
                    else:
                        amount_multiple_diff_other.append(grant_amount)

        # print(len(num_grants))
        # print(len(amount_single_stnd), len(amount_single_cont), len(amount_single_other))
        print(year, ",", len(amount_single_stnd), ",", len(amount_single_cont), ",",
            len(amount_multiple_same_stnd), ",", len(amount_multiple_same_cont), ",",
            len(amount_multiple_diff_stnd), ",", len(amount_multiple_diff_cont),
            ",", sum(amount_single_stnd)/len(amount_single_stnd), ",", sum(amount_single_cont)/len(amount_single_cont),
            ",", sum(amount_multiple_same_stnd)/len(amount_multiple_same_stnd), ",", sum(amount_multiple_same_cont)/len(amount_multiple_same_cont),
            ",", sum(amount_multiple_diff_stnd)/len(amount_multiple_diff_stnd), ",", sum(amount_multiple_diff_cont)/len(amount_multiple_diff_cont))

def num_pi_each_year_2(years):
    for year in years:
        data = []
        path = os.path.join(outf_path, "summary_{}.csv".format(year))
        data.append(pd.read_csv(path, header=0))
        concat_df = pd.concat(data, ignore_index = True)

        groups = concat_df.groupby(["year", "id", "title", "amount"])
        # print("total number of award", groups["year", "id", "title", "amount"].count())

        num_grants = []
        amount_single = []
        amount_multiple_same = []
        amount_multiple_diff = []
        for name, value in groups:
            num_grants.append(value.shape[0])
            grant_amount = value.amount.values[0]
            if value.shape[0] == 1:
                amount_single.append(value.shape[0])
            else:
                emails = [str(e).split("@")[-1] for e in value.email.values]
                # print(emails)
                if len(set(emails)) == 1:
                    amount_multiple_same.append(value.shape[0])
                else:
                    amount_multiple_diff.append(value.shape[0])

        # print(len(num_grants))
        # print(len(amount_single_stnd), len(amount_single_cont), len(amount_single_other))
        print(year,
            ",", sum(amount_single)/len(amount_single),
            ",", sum(amount_multiple_same)/len(amount_multiple_same),
            ",", sum(amount_multiple_diff)/len(amount_multiple_diff))


if __name__ == '__main__':
    years = range(2000, 2020, 1)
    # read_xml_files(years)
    num_pi_each_year_2(years)
    # num_grants_each_year(years)
    # num_people_num_grants(years)
