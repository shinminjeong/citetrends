from django.shortcuts import render, render_to_response
from django.http import HttpResponse, JsonResponse
from django.template import Context
from django.template.context_processors import csrf
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.conf import settings

import os, json
from collections import Counter
from ent2Vec.utils import get_conf_name

def main(request):
    return render(request, "main.html")

def menu(request):
    file_type = request.GET.get("type")
    data_path = os.path.join(os.getcwd(), "app/data", file_type)
    avail_data = sorted(os.listdir(data_path))
    return render(request, "menu.html", {"type": file_type, "list": avail_data})

def plot(request):
    input_file = request.GET.get("input")
    file_type = request.GET.get("type")
    verbose = request.GET.get("verbose")
    grid_test = request.GET.get("grid_test")
    data_path = os.path.join(os.getcwd(), "app/data/", file_type, input_file)
    data = json.loads(open(data_path).read())
    print("input_file", len(data), verbose)
    return render(request, "plot.html", {
        "plottype": "avg" if file_type == "conf" else "indv",
        "input_data": data, "verbose": verbose,
        "grid_test": grid_test
    })

@csrf_exempt
def search(request):
    plottype = request.POST.get("plottype")
    summary = request.POST.get("summary") == "true"
    print_threshold = 0.1
    text = ""
    rawinfo = {}
    refcounter = []
    paper_arr = []

    if plottype == "indv":
        print_threshold = 0.3
        selected_papers = request.POST.get("nodes")
        paper_arr = json.loads(selected_papers)
        for p in sorted(paper_arr):
            name, year, pid = p.split("_")
            if pid == "average": continue
            if name not in rawinfo: # load data from raw json file
                raw_data_path = os.path.join(os.getcwd(), "../data/{}.json".format(name))
                rawinfo[name] = json.loads(open(raw_data_path).read())
            title = rawinfo[name][pid]["Title"]
            refcounter.extend(rawinfo[name][pid]["References"])
            print(name, year, title)
            text += "{} {} {}<br>".format(name, year, title)

    else: # year average
        print_threshold = 0.1
        selected_years = request.POST.get("nodes")
        avg_year_arr = json.loads(selected_years)
        for p in sorted(avg_year_arr):
            name, year = p.split("_")
            if year == "Anchor": continue
            if name not in rawinfo: # load data from raw json file
                raw_data_path = os.path.join(os.getcwd(), "../data/{}.json".format(name))
                rawinfo[name] = json.loads(open(raw_data_path).read())
            y_papers = []
            for pid, paper in rawinfo[name].items():
                if paper["Year"] == int(year):
                    # print(paper)
                    refcounter.extend(paper["References"])
                    y_papers.append(pid)
            paper_arr.extend(y_papers)
            print(name, year, len(y_papers))
            text += "{} {} - # of paper: {}<br>".format(name, year, len(y_papers))

    print("-------------------------------")
    print("Total {} paper selected".format(len(paper_arr)))
    print("-------------------------------")
    text += "<br>Total {} paper selected<br><br>".format(len(paper_arr))
    for conf_id, num in Counter(refcounter).most_common(10):
        print(get_conf_name(conf_id), num)
        text += "%s %d (%.2f)<br>"%(get_conf_name(conf_id), num, num/len(paper_arr))
    print("-------------------------------")
    text += "<br>"

    ## only return summary
    if summary:
        text = ""
        for conf_id, num in Counter(refcounter).most_common(5):
            if num/len(paper_arr) < print_threshold: continue
            text += "%s %d (%.2f)<br>"%(get_conf_name(conf_id), num, num/len(paper_arr))

    return JsonResponse({"text": text})
