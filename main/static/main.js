
function buildHoneypotObj(id, name, compose){
  return {
    "id":id,
    "name": name,
    "compose": compose,
    "height": 50,
    "type": "honeypot",
    "fill": {
      "src": "/static/main/favicon.ico"
    }
  }
}

function addHoneypot(){
  let honeypotName = document.getElementById("honeypot-name").value;
  let compose = document.getElementById("docker-compose").value;
  let honeypotId = document.getElementById("honeypot-id").value;
  // Add
  if(honeypotId == ""){
    let id = Math.floor(Math.random() * 1000) + 1;
    let honeypotObj = buildHoneypotObj(id, honeypotName, compose)
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
            if (graphdata.nodes[i].id == tag.id) {
              document.getElementById("honeypot-name").value = graphdata.nodes[i].name
              document.getElementById("docker-compose").value = graphdata.nodes[i].compose
              document.getElementById("honeypot-id").value = graphdata.nodes[i].id
              let myModal = new bootstrap.Modal(document.getElementById('exampleModal'), {});
              myModal.show();
              break;
            }
          }
        }
      }
    });

  }

function sendData(){
    let data = new FormData();
    data.append("csrfmiddlewaretoken", '{{csrf_token}}');
    data.append("data",JSON.stringify(graphdata));
    axios.post('/test/', data)
        .then(res => alert("Form Submitted"))
        .catch(errors => console.log(errors))
}
