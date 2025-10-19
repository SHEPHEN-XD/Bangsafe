// BANGSAFE frontend script - dynamic API base stored in localStorage
const YEAR = new Date().getFullYear();
document.getElementById('year').textContent = YEAR;

const welcome = document.getElementById('welcome');
const app = document.getElementById('app');
const enterBtn = document.getElementById('enter');
const apiInput = document.getElementById('apiInput');
const saveApi = document.getElementById('saveApi');
const urlInput = document.getElementById('url');
const scanBtn = document.getElementById('scanBtn');
const resultEl = document.getElementById('result');
const feedEl = document.getElementById('feed');
const reportBtn = document.getElementById('reportBtn');

function getApiBase(){
  return localStorage.getItem('BANGSAFE_API') || '';
}
function setApiBase(u){
  localStorage.setItem('BANGSAFE_API', u);
}

// load saved API
const saved = getApiBase();
if(saved) apiInput.value = saved;

enterBtn.addEventListener('click', ()=>{
  welcome.style.display='none';
  app.classList.remove('hidden');
  loadFeed();
});

saveApi.addEventListener('click', ()=>{
  const v = apiInput.value.trim();
  if(!v){ alert('Enter backend URL (or localhost for local dev)'); return; }
  setApiBase(v);
  alert('Saved API URL. Now use Scan button.');
});

async function apiPost(path, body){
  let base = getApiBase();
  if(!base){
    alert('Please set backend URL first (top-right).');
    throw 'no api';
  }
  // remove trailing slash
  if(base.endsWith('/')) base = base.slice(0,-1);
  const url = base + path;
  const res = await fetch(url, {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify(body)
  });
  if(!res.ok) throw await res.text();
  return await res.json();
}

scanBtn.addEventListener('click', async ()=>{
  const url = urlInput.value.trim();
  if(!url){ alert('Enter URL to scan'); return; }
  resultEl.textContent = 'Scanning...';
  try{
    const data = await apiPost('/scan', {url});
    showResult(data);
  }catch(e){
    resultEl.textContent = 'Scan failed: '+e;
  }
});

reportBtn.addEventListener('click', async ()=>{
  const url = urlInput.value.trim();
  if(!url){ alert('Enter URL to report'); return; }
  const note = prompt('আপনি কেন রিপোর্ট করছেন? (ঐচ্ছিক)');
  try{
    const base = getApiBase();
    if(!base) return alert('Set backend URL first.');
    const urlFull = (base.endsWith('/')? base.slice(0,-1):base) + '/report';
    const res = await fetch(urlFull, {method:'POST',headers:{'Content-Type':'application/json'},body: JSON.stringify({url, note})});
    if(!res.ok) throw await res.text();
    alert('Reported. ধন্যবাদ।');
    loadFeed();
  }catch(e){
    alert('Report failed: '+e);
  }
});

function showResult(data){
  resultEl.innerHTML = '';
  const v = document.createElement('div'); v.className='verdict';
  v.innerHTML = `<b>Verdict:</b> ${data.verdict.toUpperCase()} (${data.score}/100)`;
  resultEl.appendChild(v);
  if(Array.isArray(data.reasons) && data.reasons.length){
    const ul = document.createElement('ul');
    data.reasons.forEach(r=>{ const li=document.createElement('li'); li.textContent=r; ul.appendChild(li);});
    resultEl.appendChild(ul);
  }else{
    const p = document.createElement('div'); p.textContent='No specific suspicious patterns found.'; resultEl.appendChild(p);
  }
}

async function loadFeed(){
  feedEl.textContent = 'Loading...';
  const base = getApiBase();
  if(!base){ feedEl.textContent = 'Set backend URL (top-right) to show reports.'; return; }
  try{
    const res = await fetch((base.endsWith('/')? base.slice(0,-1):base) + '/reports?limit=50');
    if(!res.ok) throw await res.text();
    const items = await res.json();
    feedEl.innerHTML = '';
    if(items.length===0) feedEl.textContent = 'কোনো রিপোর্ট নেই।';
    items.forEach(it=>{
      const d = new Date(it.ts*1000).toLocaleString();
      const el = document.createElement('div'); el.className='item';
      el.innerHTML = `<b>${it.url}</b><div style="color:var(--muted);font-size:12px">${it.note || ''} • ${d}</div>`;
      feedEl.appendChild(el);
    });
  }catch(e){
    feedEl.textContent = 'Feed load failed: '+e;
  }
}
