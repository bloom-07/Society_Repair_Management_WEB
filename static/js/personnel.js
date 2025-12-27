// personnel.js — loads personnel and provides scrolling + add/toggle actions
let personnelData = [];
let renderIndex = 0;
const RENDER_CHUNK = 25;

async function fetchPersonnel() {
  const res = await fetch('/admin/personnel', { credentials: 'same-origin' });
  personnelData = await res.json();
  renderIndex = 0;
  const container = document.getElementById('personnelContainer');
  if (container) container.scrollTop = 0;
  renderMorePersonnel();
}

function renderMorePersonnel() {
  const tbody = document.querySelector('#personnelTable tbody');
  const end = Math.min(personnelData.length, renderIndex + RENDER_CHUNK);
  for (let i = renderIndex; i < end; i++) {
    const p = personnelData[i];
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${p.Personnel_ID}</td>
      <td>${p.Personnel_Name}</td>
      <td>${p.Specialization || ''}</td>
      <td>${p.Contact_No || ''}</td>
      <td>${p.Email || ''}</td>
      <td>${p.Is_Available ? 'Yes' : 'No'}</td>
      <td><button onclick="togglePersonnelAvailability('${p.Personnel_ID}', ${p.Is_Available ? 'true' : 'false'})">${p.Is_Available ? 'Set Busy' : 'Set Available'}</button></td>
    `;
    tbody.appendChild(tr);
  }
  renderIndex = end;
  document.getElementById('loadingMore').style.display = renderIndex < personnelData.length ? 'block' : 'none';
}

function setupScrollLoader() {
  const container = document.getElementById('personnelContainer');
  if (!container) return;
  container.addEventListener('scroll', () => {
    if (container.scrollTop + container.clientHeight >= container.scrollHeight - 80) {
      if (renderIndex < personnelData.length) {
        renderMorePersonnel();
      }
    }
  });
}

function showAddPersonnelForm(){
  const f = document.getElementById('addPersonnelForm'); if(f) f.style.display = 'block';
}
function hideAddPersonnelForm(){
  const f = document.getElementById('addPersonnelForm'); if(f) f.style.display = 'none';
}

async function submitNewPersonnel(){
  const id = (document.getElementById('new_personnel_id').value || '').trim();
  const name = (document.getElementById('new_personnel_name').value || '').trim();
  const email = (document.getElementById('new_personnel_email').value || '').trim();
  const contact = (document.getElementById('new_personnel_contact').value || '').trim();
  const spec = (document.getElementById('new_personnel_spec').value || '').trim();
  if (!id || !name) { alert('ID and Name required'); return; }
  const res = await fetch('/admin/personnel', { method: 'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ personel_id: id, personnel_id: id, name, email, contact, specialization: spec }), credentials: 'same-origin' });
  const data = await res.json();
  if (data && data.error) { alert('Error: ' + data.error); return; }
  hideAddPersonnelForm();
  // clear
  ['new_personnel_id','new_personnel_name','new_personnel_email','new_personnel_contact','new_personnel_spec'].forEach(id => { const el = document.getElementById(id); if(el) el.value=''; });
  await fetchPersonnel();
}

async function togglePersonnelAvailability(personnelId, currentlyAvailable){
  const newAvail = !currentlyAvailable;
  await fetch('/admin/personnel/availability', { method: 'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ personnel_id: personnelId, available: newAvail }), credentials: 'same-origin' });
  // optimistic update in local array
  const idx = personnelData.findIndex(p=>p.Personnel_ID===personnelId);
  if (idx>=0) personnelData[idx].Is_Available = newAvail;
  // re-render table quickly
  const tbody = document.querySelector('#personnelTable tbody'); tbody.innerHTML=''; renderIndex=0; renderMorePersonnel();
}

function setupSearch() {
  const top = document.getElementById('personnelSearchTop');
  if (!top) return;
  let t=null; top.addEventListener('input', ()=>{
    clearTimeout(t); t = setTimeout(()=>{
      const q = (top.value||'').toLowerCase().trim();
      const filtered = personnelData.filter(p => (p.Personnel_ID||'').toLowerCase().includes(q) || (p.Personnel_Name||'').toLowerCase().includes(q) || (p.Specialization||'').toLowerCase().includes(q));
      const tbody = document.querySelector('#personnelTable tbody'); tbody.innerHTML=''; renderIndex=0; personnelData = filtered; renderMorePersonnel();
    },250);
  });
}

// init
document.addEventListener('DOMContentLoaded', async ()=>{
  await fetchPersonnel();
  setupScrollLoader();
  setupSearch();
});
