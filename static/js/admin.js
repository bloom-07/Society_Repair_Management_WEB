// Clean admin.js - loads complaints and handles assign/status actions
async function loadAdminComplaints(q = '', status = '') {
  const params = new URLSearchParams();
  if (q) params.set('q', q);
  if (status) params.set('status', status);
  const url = '/admin/requests' + (params.toString() ? ('?' + params.toString()) : '');
  const res = await fetch(url, { credentials: 'same-origin' });
  const data = await res.json();
  window.adminData = data || [];
  const totalEl = document.getElementById("total"); if (totalEl) totalEl.innerText = (data || []).length;
  renderAdminTable(data || []);
}

function renderAdminTable(data) {
  const tbody = document.querySelector("#adminTable tbody");
  if (!tbody) return;
  tbody.innerHTML = "";
  let pending = 0, completed = 0, inprogress = 0;
  (data || []).forEach(c => {
    const status = (c.Req_Status || '').toLowerCase();
    if (status === "pending") pending++;
    if (status === "completed") completed++;
    if (status === "in progress" || status === "inprogress" || status === "assigned") inprogress++;

    const tr = document.createElement("tr");
    if (status === 'completed') tr.classList.add('completed-row');
    if (status === 'in progress' || status === 'inprogress' || status === 'assigned') tr.classList.add('inprogress-row');

    // Determine badge class
    let badgeClass = 'badge-closed';
    if (status === 'pending') badgeClass = 'badge-pending';
    if (status === 'completed') badgeClass = 'badge-completed';
    if (status === 'in progress' || status === 'inprogress' || status === 'assigned') badgeClass = 'badge-assigned';

    tr.innerHTML = `
      <td>${c.Request_ID}</td>
      <td>${c.Resident_Name}</td>
      <td>${c.Flat_No || '-'}</td>
      <td>${c.Personnel_ID || '-'}</td>
      <td>${c.Personnel_Name || '-'}</td>
      <td><span class="badge ${badgeClass}">${c.Req_Status}</span></td>
      <td>${c.Issue_Description}</td>
      <td>${c.Req_Date || ''}</td>
      <td>${c.Completion_Date || ''}</td>
      <td>
        <button class="btn sm" onclick="assignPersonnel('${c.Request_ID}')">Assign</button>
        <button class="btn sm secondary" onclick="markInProgress('${c.Request_ID}')">In Progress</button>
        <button class="btn sm secondary" onclick="markCompleted('${c.Request_ID}')">Done</button>
      </td>
    `;
    tbody.appendChild(tr);
  });

  const pendingEl = document.getElementById("pending"); if (pendingEl) pendingEl.innerText = pending;
  const inprogressEl = document.getElementById("inprogress"); if (inprogressEl) inprogressEl.innerText = inprogress;
  const completedEl = document.getElementById("completed"); if (completedEl) completedEl.innerText = completed;
}

function applyAdminFilters() {
  const qEl = document.getElementById('adminSearch');
  const statusEl = document.getElementById('adminStatus');
  const q = (qEl && qEl.value || '').trim();
  const status = (statusEl && statusEl.value || '').trim();
  loadAdminComplaints(q, status);
}

async function markCompleted(id) {
  const today = new Date().toISOString().split('T')[0];
  await fetch("/admin/status", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ request_id: id, status: "Completed", completion_date: today }),
    credentials: 'same-origin'
  });
  loadAdminComplaints();
}

async function markInProgress(id) {
  await fetch("/admin/status", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ request_id: id, status: "In Progress" }),
    credentials: 'same-origin'
  });
  loadAdminComplaints();
}

function assignPersonnel(requestId){
  openAssignModal(requestId);
}

let currentRequestId = null;

async function loadPersonnelDropdown() {
  const res = await fetch('/admin/personnel', { credentials: 'same-origin' });
  const personnel = await res.json();
  const select = document.getElementById('personnelSelect');
  if (!select) return;
  select.innerHTML = '<option value="">-- Select Personnel --</option>';
  (personnel || []).forEach(p => {
    const opt = document.createElement('option');
    opt.value = p.Personnel_ID;
    opt.textContent = `${p.Personnel_Name} (${p.Personnel_ID}) - ${p.Specialization}`;
    if (!p.Is_Available) opt.disabled = true;
    select.appendChild(opt);
  });
}

function openAssignModal(requestId) {
  currentRequestId = requestId;
  loadPersonnelDropdown();
  const modal = document.getElementById('assignModal'); if (modal) modal.style.display = 'block';
}

function closeAssignModal() {
  currentRequestId = null;
  const modal = document.getElementById('assignModal'); if (modal) modal.style.display = 'none';
}

async function submitAssign() {
  const pidEl = document.getElementById('personnelSelect');
  if (!pidEl) return alert('No personnel selector');
  const pid = pidEl.value;
  if (!pid) {
    alert('Please select a personnel');
    return;
  }
  await fetch('/admin/assign', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ request_id: currentRequestId, personnel_id: pid }),
    credentials: 'same-origin'
  });
  closeAssignModal();
  loadAdminComplaints();
}

// DOM ready wiring
document.addEventListener('DOMContentLoaded', () => {
  // initial load
  loadAdminComplaints();

  // live search debounce
  const search = document.getElementById('adminSearch');
  if (search) {
    let timeout = null;
    search.addEventListener('input', () => {
      clearTimeout(timeout);
      timeout = setTimeout(() => applyAdminFilters(), 300);
    });
  }

  const statusSel = document.getElementById('adminStatus');
  if (statusSel) statusSel.addEventListener('change', () => applyAdminFilters());
});
