const API = "http://127.0.0.1:8000/api";
let state = null;
let chart = null;

async function loadDemo(){
  try{
    const r=await fetch(API+"/demo");
    if(!r.ok) throw new Error("Backend unavailable");
    state=await r.json();
    render();
  }catch(e){
    document.getElementById("error").textContent="Start the Python backend first: uvicorn app:app --reload";
  }
}
function render(){
  const subjects=state.subjects;
  document.getElementById("overall").textContent=state.overall+"%";
  document.getElementById("risk").textContent=Object.values(subjects).filter(x=>x.status==="AT RISK").length;
  document.getElementById("minutes").textContent=state.study_plan.reduce((a,x)=>a+x.minutes,0)+" min";
  document.getElementById("count").textContent=Object.keys(subjects).length;
  const names=Object.keys(subjects);
  const colors=undefined;
  if(chart) chart.destroy();
  chart=new Chart(document.getElementById("trendChart"),{
    type:"line",
    data:{labels:["Quiz 1","Quiz 2","Quiz 3","Quiz 4"],datasets:names.map(n=>({label:n,data:subjects[n].scores,borderWidth:2,tension:.35,fill:false}))},
    options:{responsive:true,plugins:{legend:{position:"bottom"}},scales:{y:{min:0,max:100}}}
  });
  document.getElementById("priority-list").innerHTML=state.study_plan.map((x,i)=>`<div class="priority"><div><b>${i+1}. ${x.subject}</b><br><small>${x.reason}</small></div><span>${x.minutes} min</span></div>`).join("");
  document.getElementById("subject-table").innerHTML=`<div class="subject-row"><b>Subject</b><b>Recent</b><b>Average</b><b>Status</b></div>`+
    names.map(n=>{let x=subjects[n];let cls=x.status==="AT RISK"?"risk-status":x.status==="WATCH"?"watch-status":"good-status";return `<div class="subject-row"><b>${n}</b><span>${x.recent}%</span><span>${x.average}%</span><span class="status ${cls}">${x.status}</span><div class="bar"><i style="width:${x.recent}%"></i></div></div>`}).join("");
  document.getElementById("subject-cards").innerHTML=names.map(n=>{let x=subjects[n];return `<article class="subject-card"><h3>${n}</h3><div class="score">${x.recent}%</div><div class="trend">${x.trend>=0?"▲":"▼"} ${Math.abs(x.trend)} points from first quiz · ${x.status}</div></article>`}).join("");
  document.getElementById("full-plan").innerHTML=state.study_plan.map(x=>`<div class="plan-item"><div><strong>${x.subject}</strong><small>Priority based on ${x.reason.toLowerCase()} status</small></div><span class="time">${x.minutes} min</span></div>`).join("");
}
function analyzeInput(){
  const lines=document.getElementById("input-data").value.split("\n").map(x=>x.trim()).filter(Boolean);
  const subjects={};
  try{
    for(const line of lines){
      const idx=line.indexOf(":"); if(idx<1) throw new Error("Use Subject: 80, 70, 90");
      const name=line.slice(0,idx).trim();
      const scores=line.slice(idx+1).split(",").map(Number).filter(Number.isFinite);
      if(!scores.length || scores.some(x=>x<0||x>100)) throw new Error("Scores must be 0–100.");
      subjects[name]={scores};
    }
    fetch(API+"/analyze",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({subjects})})
      .then(r=>r.json()).then(d=>{state=d;document.getElementById("error").textContent="";show("dashboard");render();});
  }catch(e){document.getElementById("error").textContent=e.message}
}
function show(view){
  document.querySelectorAll(".view").forEach(x=>x.classList.add("hidden"));
  document.getElementById(view).classList.remove("hidden");
  document.querySelectorAll(".nav").forEach(x=>x.classList.toggle("active",x.dataset.view===view));
  const titles={dashboard:"Good morning 👋",subjects:"Your subjects",plan:"Today's study plan",data:"Enter quiz results"};
  document.getElementById("page-title").textContent=titles[view];
}
document.querySelectorAll(".nav").forEach(x=>x.addEventListener("click",()=>show(x.dataset.view)));
loadDemo();
