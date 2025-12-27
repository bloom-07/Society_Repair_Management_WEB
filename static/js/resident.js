async function raiseRequest() {
  const issue = document.getElementById("issue").value;
  if (!issue) return alert("Please enter issue description");

  await fetch("/resident/request", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ issue })
  });

  document.getElementById("issue").value = "";
  loadRequests();
}

async function loadRequests() {
  const res = await fetch("/resident/requests");
  const data = await res.json();

  const tbody = document.getElementById("requestTable");
  tbody.innerHTML = "";

  data.forEach(r => {
    const status = (r.Req_Status||'').toLowerCase();
    let cls = '';
    if (status === 'completed') cls = 'completed-row';
    if (status === 'in progress' || status === 'inprogress' || status === 'assigned') cls = 'inprogress-row';
    tbody.innerHTML += `
      <tr class="${cls}">
        <td>${r.Request_ID}</td>
        <td>${r.Req_Status}</td>
        <td>${r.Issue_Description}</td>
        <td>${r.Req_Date}</td>
        <td>${r.Completion_Date || ''}</td>
        <td>${r.Personnel_ID || '-'}</td>
        <td>${r.Personnel_Name || "-"}</td>
      </tr>
    `;
  });
}

async function loadPersonnel() {
  const res = await fetch("/resident/personnel");
  const data = await res.json();

  const tbody = document.getElementById("personnelTable");
  tbody.innerHTML = "";

  data.forEach(p => {
    tbody.innerHTML += `
      <tr>
        <td>${p.Personnel_ID}</td>
        <td>${p.Personnel_Name}</td>
        <td>${p.Specialization}</td>
        <td>${p.Contact_No}</td>
        <td>${p.Is_Available ? "Yes" : "No"}</td>
      </tr>
    `;
  });
}

loadRequests();
loadPersonnel();
