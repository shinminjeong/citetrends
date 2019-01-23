from django.shortcuts import render, render_to_response
from django.http import HttpResponse, JsonResponse
from django.template import Context
from django.template.context_processors import csrf
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.conf import settings

import os, json
from collections import Counter
from ent2Vec.utils import get_conf_name, get_fos_name

input_file = ""

def main(request):
    return render(request, "main.html")

def fos(request):
    return render(request, "fos.html")

def menu(request):
    file_type = request.GET.get("type")
    data_path = os.path.join(os.getcwd(), "app/data", file_type)
    avail_data = sorted(os.listdir(data_path))
    return render(request, "menu.html", {"type": file_type, "list": avail_data})

def plot(request):
    global input_file
    input_file = request.GET.get("input")
    file_type = request.GET.get("type")
    verbose = request.GET.get("verbose")
    grid_test = request.GET.get("grid_test")
    contour = request.GET.get("contour")
    data_path = os.path.join(os.getcwd(), "app/data/", file_type, input_file)
    data = json.loads(open(data_path).read())
    print(input_file, len(data), verbose)
    return render(request, "plot.html", {
        "plottype": "avg" if file_type == "conf" else "indv",
        "input_data": data, "verbose": verbose,
        "grid_test": grid_test, "contour": contour,
    })

@csrf_exempt
def search(request):
    global input_file
    plottype = request.POST.get("plottype")
    summary = request.POST.get("summary") == "true"
    print_threshold = 0.1
    text = ""
    rawinfo = {}
    refcounter = []
    paper_arr = []
    emb_type = input_file.split("_")[0]
    print("inputfile", input_file, emb_type)

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
            if emb_type == "BoV":
                refcounter.extend(rawinfo[name][pid]["References"])
            if emb_type == "BoF":
                refcounter.extend([f[0] for f in rawinfo[name][pid]["Fos"]])
            print(name, year, title)
            text += "{} {} {}<br>".format(name, year, title)

    else: # year average
        print_threshold = 0.0
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
                    if emb_type == "BoV":
                        refcounter.extend(paper["References"])
                    if emb_type == "BoF":
                        refcounter.extend([f[0] for f in paper["Fos"]])
                    y_papers.append(pid)
            paper_arr.extend(y_papers)
            print(name, year, len(y_papers))
            text += "{} {} - # of paper: {}<br>".format(name, year, len(y_papers))

    print("-------------------------------")
    print("Total {} paper selected".format(len(paper_arr)))
    print("-------------------------------")
    text += "<br>Total {} paper selected<br><br>".format(len(paper_arr))
    for conf_id, num in Counter(refcounter).most_common(10):
        if emb_type == "BoV":
            print(get_conf_name(conf_id), num)
            text += "%s %d (%.2f)<br>"%(get_conf_name(conf_id), num, num/len(paper_arr))
        if emb_type == "BoF":
            print(get_fos_name(conf_id), num)
            text += "%s %d (%.2f)<br>"%(get_fos_name(conf_id), num, num/len(paper_arr))
    print("-------------------------------")
    text += "<br>"

    ## only return summary
    if summary:
        text = ""
        for conf_id, num in Counter(refcounter).most_common(5):
            if num/len(paper_arr) < print_threshold: continue
            if emb_type == "BoV":
                text += "%s %d (%.2f)<br>"%(get_conf_name(conf_id), num, num/len(paper_arr))
            if emb_type == "BoF":
                text += "%s %d (%.2f)<br>"%(get_fos_name(conf_id), num, num/len(paper_arr))

    return JsonResponse({"text": text})

@csrf_exempt
def search_by_name(request):
    global input_file
    plottype = request.POST.get("plottype")
    search_name = request.POST.get("name")
    rawinfo = {}
    refcounter = []
    paper_arr = []
    emb_type = input_file.split("_")[0]
    print("search_by_name", input_file, emb_type, search_name)

    if plottype == "indv":
        selected_papers = request.POST.get("nodes")
        paper_arr = json.loads(selected_papers)
        for p in sorted(paper_arr):
            name, year, pid = p.split("_")
            if pid == "average": continue
            if name not in rawinfo: # load data from raw json file
                raw_data_path = os.path.join(os.getcwd(), "../data/{}.json".format(name))
                rawinfo[name] = json.loads(open(raw_data_path).read())
            if emb_type == "BoV":
                refcounter.extend(rawinfo[name][pid]["References"])
            if emb_type == "BoF":
                refcounter.extend([f[0] for f in rawinfo[name][pid]["Fos"]])

    else: # year average
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
                    if emb_type == "BoV":
                        refcounter.extend(paper["References"])
                    if emb_type == "BoF":
                        refcounter.extend([f[0] for f in paper["Fos"]])
                    y_papers.append(pid)
            paper_arr.extend(y_papers)

    search_id = int(search_name)
    c = Counter(refcounter);
    if len(paper_arr) == 0:
        value = 0
    else:
        value = c[search_id]/len(paper_arr)
    print(search_id, value)

    return JsonResponse({"value": value})
