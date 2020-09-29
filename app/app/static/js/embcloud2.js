var margin = 0, legend_margin = 200, text_margin = 3;
var draw = SVG().addTo('#papers');
    // draw.rect(width, height).fill("#fff").dblclick(function() { zoom_out() });
    draw.rect(width, height).fill("transparent").dblclick(function() { zoom_out() });
    draw.viewbox(0,0,width,height);
// this decides layer order
var draw_node = draw.group();
var draw_hull = draw.group();
var draw_edge = draw.group();
var draw_text = draw.group();
var draw_legend = draw.group();

var nsize = 2, nsizeb = 4;
var bbox = [width,-width,height,-height,0,0]; // (x_min, x_max, y_min, y_max, x_center, y_center)
var colors = ["#065143", "#129490", "#70B77E", "#A2DDE1", "#4363d8",
  "#E0A890", "#fe4a49", "#FCAB10", "#ff9234", "#e6194B",
  "#0b409c", "#5e227f", "#caabd8", "#ff6bd6", ]
var glist = [];
var yearSet = new Set();
var group_flag = {};
var every_nodes = {};
var every_nodes_t = {};
var every_edges = {};
var legend_rect = {};
var legend_text = {};
var zoomed = false;
var plottype = "avg"; // avg or indv

function drawDensityBlobs( data, density_blob ) {
  var groups = new Set();
  for (var key in data) {
    // save names of nodes
    var name = key.split("_");
    // var gname = name[0]+"-"+name[1];
    var gname = name[0];
    var year = name[1];
    var paperid = name[2];
    groups.add(gname);
    yearSet.add(year);
    group_flag[gname] = true;
    every_nodes[gname] = [];
    every_nodes_t[gname] = [];
    every_edges[gname] = [];

    if (true) {
      // calculating boundary box
      bbox[0] = Math.min(bbox[0], data[key][0]-margin)
      bbox[1] = Math.max(bbox[1], data[key][0]+margin)
      bbox[2] = Math.min(bbox[2], data[key][1]-margin)
      bbox[3] = Math.max(bbox[3], data[key][1]+margin)
    }
  }
  bbox[4] = (bbox[0]+bbox[1])/2;
  bbox[5] = (bbox[2]+bbox[3])/2;

  glist = Array.from(groups); // list of names
  var xd = bbox[1]-bbox[0],
      yd = bbox[3]-bbox[2];
  var xs = (width-legend_margin)/xd, ys = height/yd;
  // console.log("original", xd, yd, xs, ys);

  // draw circle for each point
  for (var key in density_blob) {
    // var gname = name[0]+"-"+name[1];
    var gname = key;
    var newx = (density_blob[key]["mean"][0]-bbox[4])*xs+(width-legend_margin)/2,
        newy = (density_blob[key]["mean"][1]-bbox[5])*ys+height/2;
    var newrx = density_blob[key]["std"][0]*xs,
        newry = density_blob[key]["std"][1]*ys;
    console.log(gname, newx, newy, newrx, newry);
    var circle = draw_node.ellipse(newrx, newry).id(key)
        .attr("class", gname+"_"+year)
        .center(newx, newy)
        .fill(colors[glist.indexOf(gname)%colors.length]);
    every_nodes[gname].push(circle);
  }

  // draw legends
  drawLegends();
}

function drawCloud( data, type ) {
  plottype = type;
  var groups = new Set();
  for (var key in data) {
    // save names of nodes
    var name = key.split("_");
    // var gname = name[0]+"-"+name[1];
    var gname = name[0];
    var year = name[1];
    var paperid = name[2];
    groups.add(gname);
    yearSet.add(year);
    group_flag[gname] = true;
    every_nodes[gname] = [];
    every_nodes_t[gname] = [];
    every_edges[gname] = [];
    // if (paperid == "average") {
    if (true) {
      // calculating boundary box
      bbox[0] = Math.min(bbox[0], data[key][0]-margin)
      bbox[1] = Math.max(bbox[1], data[key][0]+margin)
      bbox[2] = Math.min(bbox[2], data[key][1]-margin)
      bbox[3] = Math.max(bbox[3], data[key][1]+margin)
    }
  }
  bbox[4] = (bbox[0]+bbox[1])/2;
  bbox[5] = (bbox[2]+bbox[3])/2;

  glist = Array.from(groups); // list of names
  var xd = bbox[1]-bbox[0],
      yd = bbox[3]-bbox[2];
  var xs = (width-legend_margin)/xd, ys = height/yd;
  // console.log("original", xd, yd, xs, ys);
  // draw circle for each point
  var paths = {};
  for (var g = 0; g < glist.length; g++) {
    paths[glist[g]] = {};
  }
  // console.log("groups", groups, paths)
  // console.log("yearSet", Array.from(yearSet).sort())
  for (var key in data) {
    var name = key.split("_");
    // var gname = name[0]+"-"+name[1];
    var gname = name[0];
    var year = name[1];
    var paperid = name[2];
    var newx = (data[key][0]-bbox[4])*xs+(width-legend_margin)/2,
        newy = (data[key][1]-bbox[5])*ys+height/2;
    // console.log(gname, year, paperid, data[key][0], data[key][1], newx, newy);
    paths[gname][year] = [newx, newy];

    var pre = every_nodes[gname][every_nodes[gname].length-1];
    var distance = pre?Math.hypot(pre.attr("px")-newx, pre.attr("py")-newy):0;
    // console.log(pre, distance);
    var circle = draw_node.circle(2).id(key)
        .attr("class", gname+"_"+year)
        .attr("ox", data[key][0]).attr("oy", data[key][1])
        .attr("px", newx).attr("py", newy)
        .center(newx, newy)
        // .stroke(colors[glist.indexOf(gname)%colors.length])
        .fill(colors[glist.indexOf(gname)%colors.length]);
    every_nodes[gname].push(circle);
  }

  // draw year for each point
  drawYears(xs, ys);

  // draw legends
  drawLegends();
  function drawCloud( data, type ) {
    plottype = type;
    var groups = new Set();
    for (var key in data) {
      // save names of nodes
      var name = key.split("_");
      // var gname = name[0]+"-"+name[1];
      var gname = name[0];
      var year = name[1];
      var paperid = name[2];
      groups.add(gname);
      yearSet.add(year);
      group_flag[gname] = true;
      every_nodes[gname] = [];
      every_nodes_t[gname] = [];
      every_edges[gname] = [];
      // if (paperid == "average") {
      if (true) {
        // calculating boundary box
        bbox[0] = Math.min(bbox[0], data[key][0]-margin)
        bbox[1] = Math.max(bbox[1], data[key][0]+margin)
        bbox[2] = Math.min(bbox[2], data[key][1]-margin)
        bbox[3] = Math.max(bbox[3], data[key][1]+margin)
      }
    }
    bbox[4] = (bbox[0]+bbox[1])/2;
    bbox[5] = (bbox[2]+bbox[3])/2;

    glist = Array.from(groups); // list of names
    var xd = bbox[1]-bbox[0],
        yd = bbox[3]-bbox[2];
    var xs = (width-legend_margin)/xd, ys = height/yd;
    // console.log("original", xd, yd, xs, ys);
    // draw circle for each point
    var paths = {};
    for (var g = 0; g < glist.length; g++) {
      paths[glist[g]] = {};
    }
    // console.log("groups", groups, paths)
    // console.log("yearSet", Array.from(yearSet).sort())
    for (var key in data) {
      var name = key.split("_");
      // var gname = name[0]+"-"+name[1];
      var gname = name[0];
      var year = name[1];
      var paperid = name[2];
      var newx = (data[key][0]-bbox[4])*xs+(width-legend_margin)/2,
          newy = (data[key][1]-bbox[5])*ys+height/2;
      // console.log(gname, year, paperid, data[key][0], data[key][1], newx, newy);
      paths[gname][year] = [newx, newy];

      var pre = every_nodes[gname][every_nodes[gname].length-1];
      var distance = pre?Math.hypot(pre.attr("px")-newx, pre.attr("py")-newy):0;
      // console.log(pre, distance);
      var circle = draw_node.circle(2).id(key)
          .attr("class", gname+"_"+year)
          .attr("ox", data[key][0]).attr("oy", data[key][1])
          .attr("px", newx).attr("py", newy)
          .center(newx, newy)
          // .stroke(colors[glist.indexOf(gname)%colors.length])
          .fill(colors[glist.indexOf(gname)%colors.length]);
      every_nodes[gname].push(circle);
    }

    // draw year for each point
    drawYears(xs, ys);

    // draw legends
    drawLegends();
  }}


function drawYears(xs, ys) {
  for (var key in data) {
    var name = key.split("_");
    var gname = name[0];
    var year = name[1];
    var paperid = name[2];
    var newx = (data[key][0]-bbox[4])*xs+(width-legend_margin)/2,
        newy = (data[key][1]-bbox[5])*ys+height/2;
    if (plottype == "avg" || (plottype == "indv" && paperid == "average")) {
      var label = year;
      // console.log(plottype, key, label)
      var c_text = draw_text.text(label).id(key).fill("#000")
          .attr("x", newx+text_margin).attr("y", newy)
          .attr("stroke", 1)
          .attr("stroke-color", "white")
          .attr("display", "none");
      every_nodes_t[gname].push(c_text);
    }
  }
}

function drawLegends() {
  for (var gid in glist) {
    gname = glist[gid];
    legend_rect[gname] = draw_legend.rect(20,20).id(gid)
        .stroke(colors[gid%colors.length])
        .fill(colors[gid%colors.length]).move(width-legend_margin, gid*25+20);
    legend_text[gname] = draw_legend.text(glist[gid]).id(gid)
        .move(width-legend_margin+30, gid*25+20)
        .fill("#000");

    // legend_rect[gname].click(function() { toggle_dimension(this.node.id) });
    legend_rect[gname].click(function() {
      console.log("click", gname, glist[this.node.id])
      var gname = glist[this.node.id];
      group_flag[gname] = !group_flag[gname];
      draw_labels(gname);
      draw_edges_group(gname);
      draw_cvxhulls(gname)
    });
  }
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function rotate_path_slice(gname, year) {
  var n_point = SVG("#"+gname+"_"+year+"_average");
  var n_pivot = SVG("#"+gname+"_"+(parseInt(year)+1)+"_average");
  var n_point_text = SVG("text#"+n_point.id());

  console.log("rotate", n_point.id());

  while(true) {
    var point = {'x':n_point.attr('px'), 'y':n_point.attr('py')}
    var pivot = {'x':n_pivot.attr('px'), 'y':n_pivot.attr('py')}
    var path = SVG("#"+gname+"_path")

    if (Math.abs(point.y-pivot.y) < 2 && point.x < pivot.x) {
      var newx = point.x, newy = pivot.y;
      move_pre_points(gname, year, 0, newy-point.y);
      n_point.center(newx, newy).attr('px', newx).attr('py', newy);
      n_point_text.attr('x', newx+text_margin).attr('y', newy);
      path.attr("d", calculate_edge(gname));
      break;
    } else {
      var new_pos = rotate_point(point, pivot, -0.01);
      move_pre_points(gname, year, new_pos.x-point.x, new_pos.y-point.y);
      move_year_group(gname, year, new_pos.x-point.x, new_pos.y-point.y);
      n_point.center(new_pos.x, new_pos.y).attr('px', new_pos.x).attr('py', new_pos.y);
      n_point_text.attr('x', new_pos.x+text_margin).attr('y', new_pos.y);
      path.attr("d", calculate_edge(gname));
      await sleep(5);
    }
  }
}

function move_year_group(gname, year, dx, dy) {
  var n_points = SVG.find("."+gname+"_"+year);
  for (var i = 0; i < n_points.length; i++) {
    var n_point = n_points[i];
    if (n_point.id().split("_")[2] == "average") continue;
    // console.log("move_year_group", n_point.id())
    var newx = n_point.attr('px')+dx;
    var newy = n_point.attr('py')+dy;
    n_point.center(newx, newy).attr('px', newx).attr('py', newy);
  }
  redraw_cvxhulls(gname);
}

function move_pre_points(gname, y_until, dx, dy) {
  var yearList = Array.from(yearSet).sort();
  for (var y = 0; y < yearList.length; y++) {
    var year = yearList[y];
    if (year == parseInt(y_until)) break;
    var n_points = SVG.find("circle."+gname+"_"+year);
    for (var i = 0; i < n_points.length; i++) {
      var n_point = n_points[i];
      var newx = n_point.attr('px')+dx;
      var newy = n_point.attr('py')+dy;
      n_point.center(newx, newy).attr('px', newx).attr('py', newy);
    }
    var n_point_text = SVG("text#"+gname+"_"+year+"_average");
    n_point_text.attr('x', newx+text_margin).attr('y', newy);
  }
}

function rotate_point(point, pivot, rad)
{
  var radians = rad;
  if (point.y > pivot.y) {
    radians = -rad;
  }
  var cosTheta = Math.cos(radians);
  var sinTheta = Math.sin(radians);
  var x = (cosTheta * (point.x - pivot.x) - sinTheta * (point.y - pivot.y) + pivot.x);
  var y = (sinTheta * (point.x - pivot.x) + cosTheta * (point.y - pivot.y) + pivot.y);
  return {'x':x, 'y':y};
}

function draw_labels(gname) {
  for (var e in every_nodes_t[gname]) {
    if (group_flag[gname]) {
      every_nodes_t[gname][e].attr('display', 'none');
    } else {
      every_nodes_t[gname][e].attr('display', 'block');
    }
  }
}

function redraw_cvxhulls(gname) {
  // console.log("draw_cvxhulls", gname)
  draw_hull.clear();
  var hulls = traceHulls(every_nodes[gname], 5);
  for (var h in hulls) {
    draw_hull.polygon(hulls[h].path)
      .opacity(0.2)
      .stroke('#000')
      .fill('#ddd');
  }
}

function draw_cvxhulls(gname) {
  // console.log("draw_cvxhulls", gname)
  if (group_flag[gname]) {
    draw_hull.clear();
  } else {
    var hulls = traceHulls(every_nodes[gname], 5);
    for (var h in hulls) {
      // console.log("hulls[g]", h, hulls[h].path)
      draw_hull.polygon(hulls[h].path)
        .opacity(0.2)
        .stroke('#000')
        .fill('#ddd');
    }
  }
}

function traceHulls(nodes, offset) {
  // console.log("convexHulls", nodes)
  var hulls = {};
  // create point sets
  for (var k=0; k<nodes.length; ++k) {
    var n = nodes[k];
    var name = n.id().split("_");
    var i = name[1];
        l = hulls[i] || (hulls[i] = []);
    var rOffset = 0;
    var xpos = n.attr('px'), ypos = n.attr('py');
    l.push([xpos-rOffset-offset, ypos-rOffset-offset]);
    l.push([xpos-rOffset-offset, ypos+rOffset+offset]);
    l.push([xpos+rOffset+offset, ypos-rOffset-offset]);
    l.push([xpos+rOffset+offset, ypos+rOffset+offset]);
  }
  // console.log(hulls)
  // create convex hulls
  var hullset = [];
  for (i in hulls) {
    hullset.push({group: i, path: d3.polygonHull(hulls[i])});
  }
  // console.log(hullset)
  return hullset;
}


function toggle_dimension(gid) {
  var timeline = new SVG.Timeline();

  gname = glist[gid];
  group_flag[gname] = !group_flag[gname];
  for (var e in every_nodes[gname]) {
    var original_x = every_nodes[gname][e].attr("px"),
        original_y = every_nodes[gname][e].attr("py");
    var type = every_nodes[gname][e].id().split("_")[2];
    console.log("type", gname, type)
    if (group_flag[gname]) {
      legend_rect[gname].fill(colors[gid%colors.length]);
      if (type == "average") {
        every_nodes[gname][e].timeline(timeline);
        every_nodes[gname][e].animate(500, 0, "absolute").center(original_x, original_y);
        // every_nodes_t[gname][e].attr("visibility", "hidden");
      }
    } else {
      legend_rect[gname].fill("#eee");
      if (type == "average") {
        every_nodes[gname][e].timeline(timeline);
        every_nodes[gname][e].animate(500, 0, "absolute").center(original_x, 100);
        // every_nodes_t[gname][e].attr("visibility", "hidden");
      }
    }
  }

  every_edges[gname][0].timeline(timeline);
  every_edges[gname][0].animate(500, 0, "absolute").attr("d", calculate_edge(gname));
}

function calculate_edge(gname) {
  var yearlist = Array.from(yearSet).sort();
  var curves = [];
  for (var y = 0; y < yearlist.length; y++) {
    var cur = SVG("#"+gname+"_"+yearlist[y]);
    if (plottype == "indv") {
      cur = SVG("#"+gname+"_"+yearlist[y]+"_average");
    }
    if (cur) {
      curves.push([cur.node.getAttribute("cx"), cur.node.getAttribute("cy")].join(","))
    }
  }

  var d = "M"+curves.join(" L"); // straight line
  // var d = "M"+curves[0]+" T"+curves.join(" "); // curved line
  return d;
}

function draw_edges_group(gname) {
  if (group_flag[gname]) {
    draw_edge.clear();
    every_edges[gname] = [];
  } else {
    var d = calculate_edge(gname);
    // console.log(d)
    var path = draw_edge.path(d).id(gname+"_path")
      .fill("transparent")
      .stroke(colors[glist.indexOf(gname)%colors.length]);
    every_edges[gname].push(path);
  }
}
