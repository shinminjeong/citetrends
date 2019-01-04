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
    data_path = os.path.join(os.getcwd(), "app/data/", file_type, input_file)
    data = json.loads(open(data_path).read())
    print("input_file", len(data), verbose)
    if file_type == "conf":
        return render(request, "plot.html", {"plottype": "avg", "input_data": data})
    if file_type == "indv":
        return render(request, "plot.html", {"plottype": "indv", "input_data": data, "verbose": verbose})

@csrf_exempt
def search(request):
    selected_papers = request.POST.get("papers")
    paper_arr = json.loads(selected_papers)

    text = ""
    rawinfo = {}
    refcounter = []
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
    print("-------------------------------")
    print("Total {} paper selected".format(len(paper_arr)))
    print("-------------------------------")
    text += "<br>Total {} paper selected<br><br>".format(len(paper_arr))
    for conf_id, num in Counter(refcounter).most_common(10):
        print(get_conf_name(conf_id), num)
        text += "{} {}<br>".format(get_conf_name(conf_id), num)
    print("-------------------------------")
    text += "<br>"

    return JsonResponse({"text": text})
