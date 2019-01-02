from django.shortcuts import render, render_to_response
from django.http import HttpResponse, JsonResponse
from django.template import Context
from django.template.context_processors import csrf
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.conf import settings

import os, json

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
    data_path = os.path.join(os.getcwd(), "app/data/", file_type, input_file)
    data = json.loads(open(data_path).read())
    # print("input_file", data)
    if file_type == "conf":
        return render(request, "plot_avg.html", {"input_data": data})
    if file_type == "indv":
        return render(request, "plot_indv.html", {"input_data": data})
