async function loadData(){
  const sym = document.getElementById('symbol').value;
  const status = document.getElementById('status');
  status.textContent = 'Loading...';
  try {
    const r = await fetch(`/api/data?symbol=${sym}`);
    const data = await r.json();
    if (!r.ok) throw new Error(data.error || 'Fetch failed');

    document.getElementById('summary').innerHTML =
      `<b>Symbol:</b> ${data.symbol} &nbsp; <b>Expiry:</b> ${data.expiry || '-'} &nbsp; ` +
      `<b>Underlying:</b> ${data.underlying || '-'} &nbsp; <b>PCR:</b> ${data.pcr} &nbsp; ` +
      `<b>Recommendation:</b> ${data.recommendation}`;

    const sup = document.getElementById('supports');
    const resi = document.getElementById('resistances');
    sup.innerHTML = ''; resi.innerHTML = '';
    (data.supports || []).forEach((s, i) => {
      const li = document.createElement('li'); li.textContent = `S${i+1}: ${s}`; sup.appendChild(li);
    });
    (data.resistances || []).forEach((r, i) => {
      const li = document.createElement('li'); li.textContent = `R${i+1}: ${r}`; resi.appendChild(li);
    });

    const tbody = document.querySelector('#tbl tbody');
    tbody.innerHTML = '';
    (data.strikesWindow || []).forEach(row => {
      const tr = document.createElement('tr');
      tr.innerHTML = `<td>${row.strike}</td><td>${row.callOI}</td><td>${row.putOI}</td>`;
      tbody.appendChild(tr);
    });

    status.textContent = 'Updated';
  } catch (e) {
    status.textContent = 'Error: ' + (e.message || e);
    console.error(e);
  }
}

document.getElementById('refresh').addEventListener('click', loadData);
window.onload = loadData;
// auto refresh every 60s
setInterval(loadData, 60000);
