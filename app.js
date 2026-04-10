const STORAGE_KEY = "attendanceRecordsV1";

const clockInBtn = document.getElementById("clockInBtn");
const clockOutBtn = document.getElementById("clockOutBtn");
const clearBtn = document.getElementById("clearBtn");
const exportBtn = document.getElementById("exportBtn");
const recordsList = document.getElementById("recordsList");
const lastAction = document.getElementById("lastAction");
const chartCanvas = document.getElementById("hoursChart");

function loadRecords() {
  return JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]");
}

function saveRecords(records) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(records));
}

function formatDateTime(iso) {
  return new Date(iso).toLocaleString("ja-JP", { hour12: false });
}

function addRecord(type) {
  const records = loadRecords();
  const record = { id: crypto.randomUUID(), type, timestamp: new Date().toISOString() };
  records.unshift(record);
  saveRecords(records);
  render();
}

function clearRecords() {
  if (!confirm("記録をすべて削除します。よろしいですか？")) return;
  saveRecords([]);
  render();
}

function exportCsv() {
  const records = loadRecords().slice().reverse();
  const rows = [["種別", "日時"]];
  records.forEach((r) => rows.push([r.type === "in" ? "出勤" : "退勤", formatDateTime(r.timestamp)]));

  const csv = rows.map((row) => row.map((v) => `"${String(v).replace(/"/g, '""')}"`).join(",")).join("\n");
  const blob = new Blob([csv], { type: "text/csv;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `attendance-${new Date().toISOString().slice(0, 10)}.csv`;
  a.click();
  URL.revokeObjectURL(url);
}

function recordsToDailyHours(records) {
  const sorted = records.slice().sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
  const map = new Map();
  let openClockIn = null;

  sorted.forEach((r) => {
    const t = new Date(r.timestamp);
    if (r.type === "in") {
      openClockIn = t;
    } else if (r.type === "out" && openClockIn) {
      const end = t;
      const dayKey = openClockIn.toISOString().slice(0, 10);
      const diffHours = Math.max(0, (end - openClockIn) / (1000 * 60 * 60));
      map.set(dayKey, (map.get(dayKey) || 0) + diffHours);
      openClockIn = null;
    }
  });

  const days = [];
  for (let i = 13; i >= 0; i--) {
    const d = new Date();
    d.setHours(0, 0, 0, 0);
    d.setDate(d.getDate() - i);
    const key = d.toISOString().slice(0, 10);
    days.push({
      key,
      label: `${d.getMonth() + 1}/${d.getDate()}`,
      hours: Number((map.get(key) || 0).toFixed(2)),
    });
  }

  return days;
}

function drawChart(days) {
  const ctx = chartCanvas.getContext("2d");
  const { width, height } = chartCanvas;
  ctx.clearRect(0, 0, width, height);

  const pad = { left: 40, right: 10, top: 15, bottom: 34 };
  const plotW = width - pad.left - pad.right;
  const plotH = height - pad.top - pad.bottom;

  const maxHour = Math.max(8, ...days.map((d) => d.hours));

  ctx.strokeStyle = "#dbe5f2";
  ctx.lineWidth = 1;
  for (let y = 0; y <= 4; y++) {
    const yy = pad.top + (plotH * y) / 4;
    ctx.beginPath();
    ctx.moveTo(pad.left, yy);
    ctx.lineTo(width - pad.right, yy);
    ctx.stroke();

    const label = ((maxHour * (4 - y)) / 4).toFixed(1);
    ctx.fillStyle = "#607089";
    ctx.font = "12px sans-serif";
    ctx.fillText(label, 4, yy + 4);
  }

  const barGap = 6;
  const barW = (plotW - barGap * (days.length - 1)) / days.length;

  days.forEach((d, i) => {
    const h = (d.hours / maxHour) * plotH;
    const x = pad.left + i * (barW + barGap);
    const y = pad.top + plotH - h;

    ctx.fillStyle = "#1b73e8";
    ctx.fillRect(x, y, barW, h);

    ctx.fillStyle = "#4f5e75";
    ctx.font = "11px sans-serif";
    if (i % 2 === 0) ctx.fillText(d.label, x - 3, height - 12);
  });
}

function render() {
  const records = loadRecords();

  recordsList.innerHTML = "";
  if (!records.length) {
    recordsList.innerHTML = "<li>記録はまだありません。</li>";
    lastAction.textContent = "まだ記録はありません。";
  } else {
    records.forEach((r) => {
      const li = document.createElement("li");
      li.innerHTML = `
        <span class="tag ${r.type}">${r.type === "in" ? "出勤" : "退勤"}</span>
        <span>${formatDateTime(r.timestamp)}</span>
      `;
      recordsList.appendChild(li);
    });

    const latest = records[0];
    lastAction.textContent = `直近: ${latest.type === "in" ? "出勤" : "退勤"} (${formatDateTime(latest.timestamp)})`;
  }

  drawChart(recordsToDailyHours(records));
}

clockInBtn.addEventListener("click", () => addRecord("in"));
clockOutBtn.addEventListener("click", () => addRecord("out"));
clearBtn.addEventListener("click", clearRecords);
exportBtn.addEventListener("click", exportCsv);

render();
