import os, sys, json
import numpy as np
from operator import itemgetter

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYTHON_DIR = os.path.join(os.path.dirname(BASE_DIR), 'python')
sys.path.insert(0, PYTHON_DIR)

def normalise_data(nodes):
    return nodes


def processdata(gtype, center, outer_nodes):
    center_node = center
    outer_nodes = normalise_data(outer_nodes)

    # Radius of circle
    radius = 1.2

    # Get basic node information from ego graph
    flower_size = len(outer_nodes)
    anglelist = np.linspace(np.pi, 0., num=flower_size)
    x_pos = [0]; x_pos.extend(list(radius * np.cos(anglelist)))
    y_pos = [0]; y_pos.extend(list(radius * np.sin(anglelist)))

    # Outer nodes data
    nodedata = { key:{
            "name": key,
            "weight": outer_nodes[key]["ratiow"],
            "id": i,
            "gtype": gtype,
            "size": outer_nodes[key]["sumw"],
            "xpos": x_pos[i],
            "ypos": y_pos[i],
            "coauthor": str(False)
            # "coauthor": str(egoG.nodes[key]['coauthor'])
        } for i, key in zip(range(1, flower_size+1), outer_nodes)}
    # Center node data
    nodedata[center_node] = {
        "name": center_node,
        "weight": 1,
        "id": 0,
        "gtype": gtype,
        "size": 1,
        "xpos": x_pos[0],
        "ypos": y_pos[0],
        "coauthor": str(False)
    }
    # print(nodedata)
    nodekeys = [v["name"] for v in sorted(nodedata.values(), key=itemgetter("id"))]

    linkin = [{
            "source": nodekeys.index(s),
            "target": nodekeys.index(center_node),
            "name": s,
            "padding": nodedata[s]["size"],
            "id": nodedata[s]["id"],
            "gtype": gtype,
            "type": "in",
            "weight": outer_nodes[s]["in_nweight"],
            "count": outer_nodes[s]["influenced"]
        } for s in outer_nodes.keys()]

    linkout = [{
            "source": nodekeys.index(center_node),
            "target": nodekeys.index(s),
            "name": s,
            "padding": nodedata[s]["size"],
            "id": nodedata[s]["id"],
            "gtype": gtype,
            "type": "out",
            "weight": outer_nodes[s]["out_nweight"],
            "count": outer_nodes[s]["influencing"]
        } for s in outer_nodes.keys()]

    linkdata = list()
    for i, (lin, lout) in enumerate(zip(linkin, linkout)):
        linkdata.append(lin)
        linkdata.append(lout)

    chartdata = [{
            "id": l["id"],
            "name": l["name"],
            "type": l["type"],
            "gtype": gtype,
            # "weight": l["weight"],
            "weight": l["count"]
        } for l in linkdata]
    chartdata = sorted(chartdata, key=itemgetter("id"))
    # print(chartdata)
    return { "nodes": list(nodedata.values()), "links": linkdata, "bars": chartdata }
