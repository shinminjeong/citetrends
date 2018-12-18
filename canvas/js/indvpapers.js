var width = $(window).width(), height = $(window).height();
var margin = 5, legend_margin = 200, text_margin = 15;
var draw = SVG('papers').size(width, height);
    draw.rect(width, height).fill("#fff").dblclick(function() { zoom_out() });
    draw.viewbox(0,0,width,height);
// this decides layer order
var draw_edge = draw.group();
var draw_node = draw.group();
var draw_text = draw.group();
var draw_legend = draw.group();

var nsize = 6, nsizeb = 10;
var bbox = [width,-width,height,-height,0,0]; // (x_min, x_max, y_min, y_max, x_center, y_center)
var colors = ["#065143", "#129490",
  "#70B77E", "#E0A890", "#CE1483", "#fe4a49",
  "#A2DDE1", "#FCAB10", "#ff9234", "#fd0054",
  "#0b409c", "#5e227f"]
var glist = [];
var yearSet = new Set();
var every_nodes = {};
var every_nodes_t = {};
var every_edges = {};
var zoomed = false;

var filename = GetURLParameter("input");
console.log(filename)

$.getJSON("http://127.0.0.1:8080/data/indv/"+filename, function( data ) {
    var groups = new Set();
    for (var key in data) {
      // calculating boundary box
      bbox[0] = Math.min(bbox[0], data[key][0]-margin)
      bbox[1] = Math.max(bbox[1], data[key][0]+margin)
      bbox[2] = Math.min(bbox[2], data[key][1]-margin)
      bbox[3] = Math.max(bbox[3], data[key][1]+margin)
      // save names of nodes
      var name = key.split("_");
      // var gname = name[0]+"-"+name[1];
      var gname = name[0];
      var year = name[1];
      var paperid = name[2];
      groups.add(gname);
      yearSet.add(year);
      every_nodes[gname] = [];
      every_nodes_t[gname] = [];
      every_edges[gname] = [];
    }
    bbox[4] = (bbox[0]+bbox[1])/2;
    bbox[5] = (bbox[2]+bbox[3])/2;

    glist = Array.from(groups); // list of names
    var xd = bbox[1]-bbox[0],
        yd = bbox[3]-bbox[2];
    var xs = (width-legend_margin)/xd, ys = height/yd;
    console.log("original", xd, yd, xs, ys);
    // draw circle for each point
    for (var key in data) {
      var name = key.split("_");
      // var gname = name[0]+"-"+name[1];
      var gname = name[0];
      var year = name[1];
      var paperid = name[2];
      var newx = (data[key][0]-bbox[4])*xs+(width-legend_margin)/2,
          newy = (data[key][1]-bbox[5])*ys+height/2;
      // console.log(data[key][0], data[key][1], newx, newy);
      var circle = draw_node.circle(nsize*2).id(key)
          .attr("ox", data[key][0]).attr("oy", data[key][1])
          .attr("px", newx).attr("py", newy)
          .center(newx, newy)
          .fill(colors[glist.indexOf(gname)%colors.length]);
      circle.mouseover(function() { highlight_node(this.node.id) });
      circle.mouseout(function() { reset_highlight() });
      circle.click(function() { zoom_in_node(this.node.id) });
      every_nodes[gname].push(circle);
    }

    // draw year for each point
    for (var key in data) {
      var name = key.split("_");
      // var gname = name[0]+"-"+name[1];
      var gname = name[0];
      var year = name[1];
      var paperid = name[2];
      var newx = (data[key][0]-bbox[4])*xs+(width-legend_margin)/2,
          newy = (data[key][1]-bbox[5])*ys+height/2;
      var label = "";
      if (paperid == "average") label = year;
      var c_text = draw_text.text(label).id(key).fill("#000")
          .attr("x", newx+text_margin).attr("y", newy)
          .attr("stroke", 1)
          .attr("stroke-color", "white")
          .attr("visibility", "hidden");
      every_nodes_t[gname].push(c_text);
    }

    // draw legends
    for (var gid in glist) {
      var legend_rect = draw_legend.rect(20,20).id(gid)
          .fill(colors[gid%colors.length]).move(width-legend_margin, gid*25+20);
      var legend_text = draw_legend.text(glist[gid]).id(gid)
          .move(width-legend_margin+30, gid*25+20)
          .fill("#000");

      legend_rect.mouseover(function() { highlight_group(glist[this.node.id]) });
      legend_text.mouseover(function() { highlight_group(glist[this.node.id]) });

      legend_rect.mouseout(function() { reset_highlight() });
      legend_text.mouseout(function() { reset_highlight() });
    }

});

function zoom_out() {
  if (!zoomed) return;
  zoomed = false;
  reset_highlight();
  remove_edges();
  draw.animate(100).viewbox(0, 0, width, height);
}

function calculate_bbox(data) {
  var box = [width,-width,height,-height,0,0];
  for (var key in data) {
    // calculating boundary box
    box[0] = Math.min(box[0], data[key].node.getAttribute("px"));
    box[1] = Math.max(box[1], data[key].node.getAttribute("px"));
    box[2] = Math.min(box[2], data[key].node.getAttribute("py"));
    box[3] = Math.max(box[3], data[key].node.getAttribute("py"));
  }
  // console.log("calculate_canvas", box);
  box[4] = (box[0]+box[1])/2;
  box[5] = (box[2]+box[3])/2;
  return box
}

function zoom_in_node(nid) {
  if (zoomed) return;
  zoomed = true;
  dim_every_nodes(0.2);
  var name = nid.split("_");
  // var gname = name[0]+"-"+name[1];
  var gname = name[0];

  // calculate bbox region to zome in
  var nbox = calculate_bbox(every_nodes[gname]);
  var xd = 50+nbox[1]-nbox[0], yd = 50+nbox[3]-nbox[2];
  var newwidth = 100, newheight = 100; // added margin
  if (xd > yd) {
    newwidth += xd, newheight += height*xd/width;
  } else {
    newwidth += width*yd/height, newheight += yd;
  }

  draw.animate(100).viewbox({
    x: nbox[4]-newwidth/2,
    y: nbox[5]-newheight/2,
    width: newwidth,
    height: newheight,
    zoom: Math.min(width/newwidth, height/newheight)
  });

  // chaneg node color and draw edges
  for (var e in every_nodes[gname]) {
    var name = every_nodes[gname][e].node.id.split("_");
    var year_n = name[1], pid = name[2];
    if (pid == "average") {
      every_nodes[gname][e].attr("r", nsize).attr("opacity", 1)
          .fill(colors[glist.indexOf(gname)%colors.length]);
    } else {
      every_nodes[gname][e].attr("r", nsize).attr("opacity", 1)
          .fill("white").attr("stroke", colors[glist.indexOf(gname)%colors.length]);
    }
    var year_t = every_nodes_t[gname][e].node.id.split("_")[1];
    // if (year_t%5 == 0) {
      every_nodes_t[gname][e].attr("visibility", "visible");
    // }
  }
  draw_edges_group(gname);
}

var mouseover_while_zoomed;
function highlight_node(nid) {
  // console.log("highlight_node", nid);
  if (!zoomed) dim_every_nodes(0.6);
  mouseover_while_zoomed = nid;
  var members = SVG.select("#"+nid).members;
  for (var n in members) {
    if (members[n].type == "circle") { members[n].attr("r", nsizeb).attr("opacity", 1); }
    if (members[n].type == "text") { members[n].text(nid).attr("visibility", "visible"); }
  }
}

function remove_edges() {
  for (var gname in every_nodes) {
    for (var e in every_edges[gname]) {
      every_edges[gname][e].remove();
    }
  }
}

function draw_edges_group(gname) {
  var yearlist = Array.from(yearSet).sort();
  var prv = null;
  for (var y in yearlist) {
    var cur = SVG.get("#"+gname+"_"+yearlist[y]+"_average");
    if (cur) {
      if (prv) {
        var path = draw_edge.line(prv.node.getAttribute("cx"), prv.node.getAttribute("cy"),
                          cur.node.getAttribute("cx"), cur.node.getAttribute("cy"))
                       .stroke(colors[glist.indexOf(gname)%colors.length]);
        every_edges[gname].push(path);
      }
      prv = cur;
    }
  }
}

function highlight_group(gname) {
  if (zoomed) return;
  // console.log("highlight_group", gname);
  dim_every_nodes(0.3);
  for (var e in every_nodes[gname]) {
    every_nodes[gname][e].attr("r", nsizeb).attr("opacity", 1)
        .fill(colors[glist.indexOf(gname)%colors.length]);
    every_nodes_t[gname][e].attr("visibility", "visible");
  }
}

function dim_every_nodes(opct) {
  for (var gname in every_nodes) {
    for (var e in every_nodes[gname]) {
      every_nodes[gname][e].attr("opacity", opct);
    }
    for (var e in every_edges[gname]) {
      every_edges[gname][e].attr("opacity", opct);
    }
  }
}

function reset_highlight() {
  if (zoomed) {
    // console.log("mouseover_while_zoomed", mouseover_while_zoomed)
    var members = SVG.select("#"+mouseover_while_zoomed).members;
    for (var n in members) {
      if (members[n].type == "circle") { members[n].attr("r", nsize).attr("opacity", 0.6); }
      if (members[n].type == "text") { members[n].text(mouseover_while_zoomed).attr("visibility", "hidden"); }
    }
    return;
  }
  for (var gname in every_nodes) {
    for (var e in every_nodes[gname]) {
      var tmp = every_nodes[gname][e].node;
      var newx = tmp.getAttribute("px"), newy = tmp.getAttribute("py");
      every_nodes[gname][e].attr("r", nsize)
          .attr("cx", newx).attr("cy", newy)
          .attr("opacity", 1)
          .fill(colors[glist.indexOf(gname)%colors.length]);
      var name = tmp.id.split("_");
      var label = "";
      if (name[2] == "average") label = name[1];
      every_nodes_t[gname][e].text(label).attr("visibility", "hidden")
          .attr("x", newx+text_margin).attr("y", newy)
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
