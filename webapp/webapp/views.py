import os, sys, json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from .graph import processdata

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYTHON_DIR = os.path.join(os.path.dirname(BASE_DIR), 'python')
sys.path.insert(0, PYTHON_DIR)

from draw_flower import draw_flower

def main(request):
    ego_name = request.GET.get('keyword')
    data1 = None
    print("ego_name", ego_name)
    if ego_name:
        # ego_name = "lexing xie"
        flower = draw_flower(ego_name)
        # print(flower)
        data1 = processdata("author", ego_name, flower)
    return render(request, "flower.html", {"author": data1});
