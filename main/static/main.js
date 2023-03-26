
function buildHoneypotObj(id, name, compose,ovf,vm_username,vm_password){
  return {
    "id":id,
    "name": name,
    "compose": compose,
    "ovf": ovf,
    "vm_username": vm_username,
    "vm_password": vm_password,
    "height": 50,
    "type": "honeypot",
    "fill": {
      "src": "/static/main/favicon.ico"
    }
  }
}

function addHoneypot(){
  let honeypotName = document.getElementById("honeypot_name").value;
  let compose = document.getElementById("docker_compose").value;
  let honeypotId = document.getElementById("honeypot_id").value;
  let ovf = document.getElementById("ovf").value
  let vm_username = document.getElementById("vm_username").value;
  let vm_password = document.getElementById("vm_password").value;
  console.log(honeypotName)
  if (honeypotName == "") return;
  // Add
  if(honeypotId == ""){
    let id = Math.floor(Math.random() * 1000) + 1;
    let honeypotObj = buildHoneypotObj(id, honeypotName, compose,ovf,vm_username,vm_password)
    let honeypotConnectionObj = {
      "from": "switch",
      "to": id
    }
    // Deepcopy
    data=JSON.parse(JSON.stringify(graphdata));
    data["nodes"].push(honeypotObj);
    data["edges"].push(honeypotConnectionObj);
  }
  else{
    // Deepcopy
    data=JSON.parse(JSON.stringify(graphdata));
    let nodes = data["nodes"];
    for(let i=0;i<nodes.length;i++){
      if(nodes[i].id == honeypotId){
        data["nodes"][i]["name"] = honeypotName;
        data["nodes"][i]["compose"] = compose;
        data["nodes"][i]["ovf"].value = ovf
        data["nodes"][i]["vm_username"].value = vm_username
        data["nodes"][i]["vm_password"].value = vm_password
        break;
      }
    }
  }
  graphdata=data;
  renderGraph(graphdata);
}

function renderGraph(graphdata){
    const parent = document.getElementById("graphcontainer")
    while (parent.firstChild) {
        parent.firstChild.remove()
    }

    var chart = anychart.graph(graphdata);
    var nodes = chart.nodes();
    // set the size of nodes
    nodes.normal().height(30);
    nodes.hovered().height(45);
    nodes.selected().height(45);

    // set the stroke of nodes
    nodes.normal().stroke(null);
    nodes.hovered().stroke("#333333", 3);
    nodes.selected().stroke("#333333", 3);

    // enable the labels of nodes
    chart.nodes().labels().enabled(true);

    // configure the labels of nodes
    chart.nodes().labels().format("{%name}");
    chart.nodes().labels().fontSize(12);
    chart.nodes().labels().fontWeight(600);
    // draw the chart
    chart.container("graphcontainer").draw();

    // onclick
    chart.listen('click', function(e) {
      var tag = e.domTarget.tag;
      if (tag) {
        if (tag.type === 'node') {
          for (var i = 0; i < graphdata.nodes.length; i++) {
            if (graphdata.nodes[i].id == tag.id  && graphdata.nodes[i].type == "honeypot") {
              document.getElementById("honeypot_name").value = graphdata.nodes[i].name
              document.getElementById("docker_compose").value = graphdata.nodes[i].compose
              document.getElementById("honeypot_id").value = graphdata.nodes[i].id
              document.getElementById("ovf").value = graphdata.nodes[i].ovf
              document.getElementById("vm_username").value = graphdata.nodes[i].vm_username
              document.getElementById("vm_password").value = graphdata.nodes[i].vm_password
              let myModal = new bootstrap.Modal(document.getElementById('exampleModal'), {});
              myModal.show();
              break;
            }
          }
        }
      }
    });

  }
