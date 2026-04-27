// ── TAB SWITCHING ──────────────────────────────
function showTab(name) {
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.snav-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('panel-' + name).classList.add('active');
  const btn = document.getElementById('snav-' + name);
  if (btn) btn.classList.add('active');
  window.scrollTo({ top: 0 });
}

// ── SEARCHABLE DROPDOWN ────────────────────────
function toggleList(listId) {
  const list = document.getElementById(listId);
  const isOpen = list.classList.contains('open');
  document.querySelectorAll('.dropdown-list').forEach(d => d.classList.remove('open'));
  if (!isOpen) list.classList.add('open');
}

function filterList(inputEl, listId, valId) {
  const query = inputEl.value.toLowerCase();
  const list = document.getElementById(listId);
  list.classList.add('open');
  document.getElementById(valId).value = ''; // clear selection when typing
  list.querySelectorAll('.dropdown-item').forEach(item => {
    item.classList.toggle('hidden', !item.textContent.toLowerCase().includes(query));
  });
}

function pickItem(inputId, listId, valId, value) {
  document.getElementById(inputId).value = value;
  document.getElementById(valId).value = value;
  document.getElementById(listId).classList.remove('open');
}

// Close dropdowns on outside click
document.addEventListener('click', function (e) {
  if (!e.target.closest('.search-select-wrap')) {
    document.querySelectorAll('.dropdown-list').forEach(d => d.classList.remove('open'));
  }
});

// ── AUTH HELPER ────────────────────────────────
function handleUnauth(data) {
  if (data && data.redirect) {
    alert('Please login first.');
    window.location.href = data.redirect;
    return true;
  }
  return false;
}

// ── FIND DONORS ────────────────────────────────
async function findDonors() {
  const blood_type = document.getElementById('find-blood-type').value;
  const city = document.getElementById('find-city-val').value || document.getElementById('find-city-input').value.trim();
  const urgency = document.getElementById('find-urgency').value;

  if (!blood_type) { alert('Please select a blood type.'); return; }

  const btn = document.getElementById('find-btn');
  btn.textContent = '⏳ Searching...';
  btn.disabled = true;

  try {
    const res = await fetch('/api/find-donors', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ blood_type, city, urgency })
    });
    const data = await res.json();
    if (handleUnauth(data)) return;

    const container = document.getElementById('find-results');

    if (!data.success || data.total === 0) {
      container.innerHTML = `<div class="card" style="text-align:center;padding:2rem;color:var(--text-muted);">
        <div style="font-size:2.5rem">😔</div>
        <p style="margin-top:0.8rem;font-size:1rem;">No donors found for <strong style="color:var(--text)">${blood_type}</strong>${city ? ' in <strong style="color:var(--text)">' + city + '</strong>' : ''}</p>
        <p style="margin-top:0.5rem;font-size:0.85rem;">Try without a city filter, or post an Emergency Request.</p>
      </div>`;
      return;
    }

    let html = `<div class="results-count">✅ Found ${data.total} Donor${data.total > 1 ? 's' : ''}</div>`;

    if (data.exact_matches.length > 0) {
      html += `<div class="section-label">🎯 Exact Match — ${blood_type}</div>`;
      html += `<div class="donor-grid">` + data.exact_matches.map(d => donorCard(d, true)).join('') + `</div>`;
    }
    if (data.compatible_donors.length > 0) {
      html += `<div class="section-label">🔄 Compatible Donors</div>`;
      html += `<div class="donor-grid">` + data.compatible_donors.map(d => donorCard(d, false)).join('') + `</div>`;
    }

    container.innerHTML = html;
  } finally {
    btn.textContent = '🔍 Find Matching Donors';
    btn.disabled = false;
  }
}

function donorCard(donor, isExact) {
  const waMsg = encodeURIComponent(`Hi ${donor.name}, I urgently need ${donor.blood_type} blood. Can you please help? Found you on RaktaSetu.`);
  const waLink = `https://wa.me/91${donor.phone}?text=${waMsg}`;
  return `<div class="donor-card ${isExact ? 'exact' : ''}">
    <div class="donor-header">
      <div class="donor-name">${donor.name}</div>
      <div class="blood-type-badge">${donor.blood_type}</div>
    </div>
    <span class="${isExact ? 'exact-tag' : 'compatible-tag'}">${isExact ? '✅ Exact Match' : '🔄 Compatible'}</span>
    <div class="donor-info">
      <div><span class="available-dot"></span>Available Now</div>
      <div>📍 ${donor.city}</div>
      <div>📅 Last donated: ${donor.last_donated}</div>
      <div class="donor-phone">📞 ${donor.phone}</div>
    </div>
    <a class="whatsapp-btn" href="${waLink}" target="_blank">💬 Contact on WhatsApp</a>
  </div>`;
}

// ── EMERGENCY ──────────────────────────────────
async function postEmergency() {
  const patient_name = document.getElementById('em-patient').value.trim();
  const blood_type   = document.getElementById('em-blood-type').value;
  const hospital     = document.getElementById('em-hospital-val').value || document.getElementById('em-hospital-input').value.trim();
  const contact      = document.getElementById('em-contact').value.trim();
  const city         = document.getElementById('em-city-val').value || document.getElementById('em-city-input').value.trim();
  const units_needed = document.getElementById('em-units').value || 1;
  const msgEl        = document.getElementById('em-result');

  if (!patient_name || !blood_type || !hospital || !contact) {
    msgEl.className = 'result-msg error';
    msgEl.textContent = '⚠️ Please fill all required fields (Patient Name, Blood Type, Hospital, Contact).';
    return;
  }

  const res = await fetch('/api/emergency-request', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ patient_name, blood_type, hospital, contact, city, units_needed })
  });
  const data = await res.json();
  if (handleUnauth(data)) return;

  if (data.success) {
    msgEl.className = 'result-msg success';
    msgEl.textContent = '🚨 ' + data.message;
  } else {
    msgEl.className = 'result-msg error';
    msgEl.textContent = data.error || 'Something went wrong.';
  }
}

// ── AI CHAT ────────────────────────────────────
let chatHistory = [];

async function sendChat() {
  const input = document.getElementById('chat-input');
  const msg = input.value.trim();
  if (!msg) return;

  const chatBox = document.getElementById('chat-box');
  chatBox.innerHTML += `<div class="chat-msg user"><div class="avatar">👤</div><div class="bubble">${msg}</div></div>`;
  input.value = '';
  chatBox.scrollTop = chatBox.scrollHeight;
  chatHistory.push({ role: 'user', content: msg });

  const typingId = 'typing-' + Date.now();
  chatBox.innerHTML += `<div class="chat-msg bot" id="${typingId}"><div class="avatar">🤖</div><div class="bubble"><div class="typing-bubble"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div></div></div>`;
  chatBox.scrollTop = chatBox.scrollHeight;

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: msg, history: chatHistory.slice(0, -1) })
    });
    const data = await res.json();
    if (handleUnauth(data)) return;

    document.getElementById(typingId).remove();
    const reply = data.reply || 'Sorry, something went wrong.';
    chatBox.innerHTML += `<div class="chat-msg bot"><div class="avatar">🤖</div><div class="bubble">${reply.replace(/\n/g, '<br>')}</div></div>`;
    chatBox.scrollTop = chatBox.scrollHeight;
    chatHistory.push({ role: 'assistant', content: reply });

  } catch (e) {
    document.getElementById(typingId).remove();
    chatBox.innerHTML += `<div class="chat-msg bot"><div class="avatar">🤖</div><div class="bubble">⚠️ Connection error. Please check your internet.</div></div>`;
    chatBox.scrollTop = chatBox.scrollHeight;
  }
}
