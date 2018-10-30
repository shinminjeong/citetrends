var width = $(window).width(), height = $(window).height();
var legend_margin = 200;
var draw = SVG('drawing').size(width, height);
var bbox = [0, 0, 0, 0] // (x_min, x_max, y_min, y_max)
var nsize = 6, nsizeb = 10;

var colors = ["#065143", "#129490",
  "#70B77E", "#E0A890", "#CE1483", "#fe4a49",
  "#A2DDE1", "#FCAB10", "#ff9234", "#fd0054",
  "#0b409c", "#5e227f"]
var glist = [];
var every_nodes = {};
var every_nodes_t = {};

var filename = GetURLParameter("input");
console.log(filename)

$.getJSON("http://127.0.0.1:8080/data/"+filename, function( data ) {
    var groups = new Set();
    for (var key in data) {
      // calculating boundary box
      bbox[0] = Math.min(bbox[0], data[key][0])
      bbox[1] = Math.max(bbox[1], data[key][0])
      bbox[2] = Math.min(bbox[2], data[key][1])
      bbox[3] = Math.max(bbox[3], data[key][1])
      // save names of nodes
      var name = key.split("_");
      groups.add(name[0]);
      every_nodes[name[0]] = [];
      every_nodes_t[name[0]] = [];
    }

    glist = Array.from(groups); // list of names
    var xd = bbox[1]-bbox[0]+10,
        yd = bbox[3]-bbox[2]+10;
    var xs = 1+(width-legend_margin)/xd, ys = 1+height/yd;

    // draw circle for each point
    for (var key in data) {
      var name = key.split("_");
      var gname = name[0], year = name[1];
      var circle = draw.circle(nsize*2).id(key)
          .center(data[key][0]*xs+(width-legend_margin)/2, data[key][1]*ys+height/2+30)
          .fill(colors[glist.indexOf(gname)]);
      circle.mouseover(function() { highlight_node(this.node.id) });
      circle.mouseout(function() { reset_highlight() });
      every_nodes[gname].push(circle);
    }

    // draw year for each point
    for (var key in data) {
      var name = key.split("_");
      var gname = name[0], year = name[1];
      var c_text = draw.text(year).id(key).fill("#000")
          .move(data[key][0]*xs+(width-legend_margin)/2+10, data[key][1]*ys+height/2+30)
          .attr("visibility", "hidden");
      every_nodes_t[gname].push(c_text);
    }

    // draw legends
    for (var gid in glist) {
      var legend_rect = draw.rect(20,20).id(gid)
          .fill(colors[gid]).move(width-legend_margin, gid*25+20);
      var legend_text = draw.text(glist[gid]).id(gid)
          .move(width-legend_margin+30, gid*25+20)
          .fill("#000");

      legend_rect.mouseover(function() { highlight_group(glist[this.node.id]) });
      legend_text.mouseover(function() { highlight_group(glist[this.node.id]) });

      legend_rect.mouseout(function() { reset_highlight() });
      legend_text.mouseout(function() { reset_highlight() });
    }

});

function highlight_node(nid) {
  // console.log("highlight_node", nid);
  dim_every_nodes();
  var members = SVG.select("#"+nid).members;
  for (var n in members) {
    if (members[n].type == "circle") { members[n].attr("r", nsizeb).attr("opacity", 1); }
    if (members[n].type == "text") { members[n].text(nid).attr("visibility", "visible"); }
  }
}

function highlight_group(gname) {
  // console.log("highlight_group", gname);
  dim_every_nodes();
  for (var e in every_nodes[gname]) {
    every_nodes[gname][e].attr("r", nsizeb).attr("opacity", 1)
        .fill(colors[glist.indexOf(gname)]);
    every_nodes_t[gname][e].attr("visibility", "visible");
  }
}

function dim_every_nodes() {
  for (var gname in every_nodes) {
    for (var e in every_nodes[gname]) {
      every_nodes[gname][e].attr("opacity", 0.6);
    }
  }
}

function reset_highlight() {
  for (var gname in every_nodes) {
    for (var e in every_nodes[gname]) {
      every_nodes[gname][e].attr("r", nsize)
          .attr("opacity", 1)
          .fill(colors[glist.indexOf(gname)]);
    }
    for (var e in every_nodes_t[gname]) {
      var y = every_nodes_t[gname][e].id();
      every_nodes_t[gname][e].text(y.split("_")[1]).attr("visibility", "hidden");
    }
  }
}

function GetURLParameter(sParam) {
  var sPageURL = window.location.search.substring(1);
  var sURLVariables = sPageURL.split('&');
  for (var i = 0; i < sURLVariables.length; i++) {
    var sParameterName = sURLVariables[i].split('=');
    if (sParameterName[0] == sParam) {
      return sParameterName[1];
    }
  }
}
