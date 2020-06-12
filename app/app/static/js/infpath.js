const colors = ["#065143", "#129490", "#70B77E", "#A2DDE1", "#4363d8",
  "#E0A890", "#fe4a49", "#FCAB10", "#ff9234", "#e6194B",
  "#0b409c", "#5e227f", "#caabd8", "#ff6bd6"];

class InfPath {

  constructor(div_id, w, h) {
    this.margin = 5;
    this.legend_margin = 200;
    this.text_margin = 15;

    this.div_id = div_id;
    this.width = w, this.height = h;
    this.svg = d3.select("#"+this.div_id)
      .append('svg')
      .attr('width', this.width)
      .attr('height', this.height);

    this.div_id = div_id;
    this.plottype = "avg";

    this.g_circles = this.svg.append("g");
    this.g_legends = this.svg.append("g");
  }

  drawCloud(data, plottype) {
    this.plottype = plottype;

    var nsize = 2, nsizeb = 6;
    if (this.plottype == "avg") {
      nsize = 6, nsizeb = 10;
    }

    var bbox = [this.width,-this.width,this.height,-this.height,0,0];
    var groups = new Set();
    var glist = [];
    var yearSet = new Set();
    var group_flag = {};
    var every_nodes = {};
    var every_nodes_t = {};
    var every_edges = {};
    var legend_rect = {};
    var legend_text = {};
    var data_circles = [];

    for (var key in data) {
      // calculating boundary box
      bbox[0] = Math.min(bbox[0], data[key][0]-this.margin)
      bbox[1] = Math.max(bbox[1], data[key][0]+this.margin)
      bbox[2] = Math.min(bbox[2], data[key][1]-this.margin)
      bbox[3] = Math.max(bbox[3], data[key][1]+this.margin)
      // save names of nodes
      var name = key.split("_");
      // var gname = name[0]+"-"+name[1];
      var gname = name[0];
      var year = name[1];
      var paperid = name[2];
      groups.add(gname);
      yearSet.add(year);
      data_circles.push({
        id: key,
        group: gname,
        year: year,
        paperid: paperid,
        ox: data[key][0],
        oy: data[key][1],
      });

      group_flag[gname] = true;
      every_nodes[gname] = [];
      every_nodes_t[gname] = [];
      every_edges[gname] = [];
    }
    bbox[4] = (bbox[0]+bbox[1])/2;
    bbox[5] = (bbox[2]+bbox[3])/2;

    glist = Array.from(groups); // list of names
    var xd = bbox[1]-bbox[0],
        yd = bbox[3]-bbox[2];
    var xs = (this.width-this.legend_margin)/xd, ys = this.height/yd;
    // console.log("original", xd, yd, xs, ys);
    // draw circle for each point

    var bubble = this.g_circles.append('g').selectAll('.bubble')
        .data(data_circles)
      .enter().append('circle')
        .attr('id', function(d){return d.id;})
        .attr('class', function(d){ return 'bubble g'+d.group; })
        .attr('cx', d => bbox[0]+(d.ox-bbox[4])*xs+(this.width-this.legend_margin)/2 )
        .attr('cy', d => bbox[1]+(d.oy-bbox[5])*ys+this.height/2 )
        .attr('r', nsize)
        .style('fill', function(d){ return colors[glist.indexOf(d.group)%colors.length] })

    // draw legends
    for (var gid in glist) {
      gname = glist[gid];
      legend_rect[gname] = this.g_legends.append('rect')
          .attr('x', this.width-this.legend_margin)
          .attr('y', gid*25+100)
          .attr('width', 20)
          .attr('height', 20)
          .attr('id', gid)
          .style('stroke', colors[gid%colors.length])
          .style('fill', colors[gid%colors.length])
          .on('click', function(d) { toggle_group(gid) })
          .on('mouseover', function(d) { highlight_group(gname) })
          .on('mouseout', function(d) { reset_highlight() });

      legend_text[gname] = this.g_legends.append('text')
          .text(glist[gid])
          .attr('id', gid)
          .attr('x', this.width-this.legend_margin+30)
          .attr('y', gid*25+115)
          .style('fill', '#000');

    }

    // for (var key in data) {
    //   var name = key.split("_");
    //   // var gname = name[0]+"-"+name[1];
    //   var gname = name[0];
    //   var year = name[1];
    //   var paperid = name[2];
    //   var newx = (data[key][0]-bbox[4])*xs+(width-legend_margin)/2,
    //       newy = (data[key][1]-bbox[5])*ys+height/2;
    //   // console.log(gname, year, paperid, data[key][0], data[key][1], newx, newy);
    //   paths[gname][year] = [newx, newy];
    //   var circle = this.g_circles.append("circle")
    //   ).circle(nsize*2).id(key)
    //       .attr("ox", data[key][0]).attr("oy", data[key][1])
    //       .attr("px", newx).attr("py", newy)
    //       .center(newx, newy)
    //       .fill(colors[glist.indexOf(gname)%colors.length]);
    //   circle.mouseover(function() { highlight_node(this.node.id) });
    //   circle.mouseout(function() { reset_highlight() });
    //   circle.click(function() { zoom_in_node(this.node.id) });
    //   every_nodes[gname].push(circle);
    // }
    // console.log("paths", paths)
  }

}

function toggle_group(gid) {
  gname = glist[gid];
  group_flag[gname] = !group_flag[gname];
  console.log("set group flag", gname, group_flag[gname])
  for (var e in every_nodes[gname]) {
    if (group_flag[gname]) {
      legend_rect[gname].fill(colors[gid%colors.length]);
      every_nodes[gname][e].attr("visibility", "visible");
      every_nodes_t[gname][e].attr("visibility", "visible");
    } else {
      legend_rect[gname].fill("#eee");
      every_nodes[gname][e].attr("visibility", "hidden");
      every_nodes_t[gname][e].attr("visibility", "hidden");
    }
  }
}

function highlight_group(gname) {
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
      var label = "";
      if (plottype == "avg" || (plottype == "indv" && name[2] == "average")) {
        label = name[1];
      }
      every_nodes_t[gname][e].text(label).attr("visibility", "hidden")
          .attr("x", newx+text_margin).attr("y", newy)
    }
  }
}
