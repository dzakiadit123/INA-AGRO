const STORAGE_KEYS = {
  USER: "ina_agro_curated_user_v1",
  HISTORY: "ina_agro_curated_history_v1",
  CONSENT: "ina_agro_curated_consent_v1",
};

const INA_AGRO_COMMODITIES = [
  {
    no: 1,
    kategori: "Hortikultura Umbi",
    nama: "Bawang Merah",
    latin: "Allium cepa var. aggregatum",
    kaggleSlug: "srinivas1/allium-onion-garlic-yield-soil-dataset",
    presetKey: "shallot",
    specs: "N ~92 kg/ha • P ~56 kg/ha • K ~86 kg/ha • Suhu 25–32 °C • Kelembapan 50–76% • pH 5.6–7.1 • Hujan 40–130 mm/bln.",
  },
  {
    no: 2,
    kategori: "Hortikultura Dataran Tinggi",
    nama: "Bawang Putih",
    latin: "Allium sativum",
    kaggleSlug: "srinivas1/allium-onion-garlic-yield-soil-dataset",
    presetKey: "garlic",
    specs: "N ~98 kg/ha • P ~68 kg/ha • K ~104 kg/ha • Suhu 15–22.5 °C • Kelembapan 62–84% • pH 5.8–7.3 • Hujan 70–175 mm/bln.",
  },
  {
    no: 3,
    kategori: "Hortikultura Buah",
    nama: "Cabai Merah",
    latin: "Capsicum annuum",
    kaggleSlug: "devendra111/capsicum-chili-cultivation-soil-climate",
    presetKey: "red_chili",
    specs: "N ~115 kg/ha • P ~72 kg/ha • K ~96 kg/ha • Suhu 20–28 °C • Kelembapan 62–85% • pH 5.5–7.1 • Hujan 95–210 mm/bln.",
  },
  {
    no: 4,
    kategori: "Hortikultura Buah",
    nama: "Cabai Rawit",
    latin: "Capsicum frutescens",
    kaggleSlug: "devendra111/capsicum-chili-cultivation-soil-climate",
    presetKey: "bird_eye_chili",
    specs: "N ~86 kg/ha • P ~54 kg/ha • K ~74 kg/ha • Suhu 23.5–32 °C • Kelembapan 55–80% • pH 5.3–7.0 • Hujan 65–168 mm/bln.",
  },
  {
    no: 5,
    kategori: "Pangan Utama (Serealia)",
    nama: "Jagung",
    latin: "Zea mays",
    kaggleSlug: "atharvaingle/crop-recommendation-dataset",
    presetKey: "maize",
    specs: "N ~78 kg/ha • P ~48 kg/ha • K ~22 kg/ha • Suhu 19–31 °C • Kelembapan 52–82% • pH 5.4–7.2 • Hujan 65–195 mm/bln.",
  },
  {
    no: 6,
    kategori: "Hortikultura Dataran Tinggi",
    nama: "Kentang",
    latin: "Solanum tuberosum",
    kaggleSlug: "zsinghrahulk/potato-crop-dataset",
    presetKey: "potato",
    specs: "N ~112 kg/ha • P ~76 kg/ha • K ~128 kg/ha • Suhu 13.5–22 °C • Kelembapan 68–90% • pH 4.9–6.5 • Hujan 95–240 mm/bln.",
  },
];

const PRESET_SCENARIOS = {
  shallot: {
    lokasi_wilayah: "Kec. Brebes, Kab. Brebes (Sentra Bawang Merah)",
    N: 92, P: 56, K: 86,
    temperature: 28.2, humidity: 64, ph: 6.3, rainfall: 82,
  },
  garlic: {
    lokasi_wilayah: "Kec. Sembalun, Kab. Lombok Timur (Dataran Tinggi)",
    N: 98, P: 68, K: 104,
    temperature: 18.6, humidity: 73, ph: 6.5, rainfall: 118,
  },
  red_chili: {
    lokasi_wilayah: "Kec. Lembang, Kab. Bandung Barat",
    N: 115, P: 72, K: 96,
    temperature: 24.2, humidity: 74, ph: 6.3, rainfall: 148,
  },
  bird_eye_chili: {
    lokasi_wilayah: "Kec. Pare, Kab. Kediri",
    N: 86, P: 54, K: 74,
    temperature: 27.6, humidity: 68.5, ph: 6.1, rainfall: 112,
  },
  maize: {
    lokasi_wilayah: "Kec. Dramaga, Kab. Bogor",
    N: 78, P: 48, K: 22,
    temperature: 24.5, humidity: 66, ph: 6.2, rainfall: 115,
  },
  potato: {
    lokasi_wilayah: "Kec. Pangalengan, Kab. Bandung (Dataran Tinggi)",
    N: 112, P: 76, K: 128,
    temperature: 17.8, humidity: 79.5, ph: 5.7, rainfall: 165,
  },
  anomali: {
    lokasi_wilayah: "Kec. Cisarua, Kab. Bogor (Uji Curah Hujan Ekstrem)",
    N: 20, P: 15, K: 15,
    temperature: 36.5, humidity: 88, ph: 4.5, rainfall: 295,
  },
};

let currentPrediction = null;
let currentPayload = null;

document.addEventListener("DOMContentLoaded", () => {
  seedDefaultHistoryIfEmpty();
  renderCommoditiesGrid();
  updateHistoryBadge();
  renderHistoryList();
  syncConsentCheckboxes();
  bindAllEvents();

  const savedUser = localStorage.getItem(STORAGE_KEYS.USER);
  if (savedUser) {
    enterApplication(JSON.parse(savedUser));
  }
});

function seedDefaultHistoryIfEmpty() {
  if (!localStorage.getItem(STORAGE_KEYS.HISTORY)) {
    const sample = [
      {
        id: 401,
        timestamp: "24 Nov 2026, 09:30",
        payload: PRESET_SCENARIOS.shallot,
        result: {
          rekomendasi_top3: [
            { komoditas: "Bawang Merah", skor_kecocokan: 98.5, label: "Tinggi", kelas_kesesuaian: "Kelas S1 - Sangat Sesuai", kode_kelas: "S1" },
            { komoditas: "Cabai Rawit", skor_kecocokan: 1.5, label: "Rendah", kelas_kesesuaian: "Kelas N - Tidak Sesuai", kode_kelas: "N" },
            { komoditas: "Jagung", skor_kecocokan: 0.0, label: "Rendah", kelas_kesesuaian: "Kelas N - Tidak Sesuai", kode_kelas: "N" },
          ],
        },
      },
      {
        id: 402,
        timestamp: "24 Nov 2026, 10:15",
        payload: PRESET_SCENARIOS.potato,
        result: {
          rekomendasi_top3: [
            { komoditas: "Kentang", skor_kecocokan: 99.0, label: "Tinggi", kelas_kesesuaian: "Kelas S1 - Sangat Sesuai", kode_kelas: "S1" },
            { komoditas: "Bawang Putih", skor_kecocokan: 1.0, label: "Rendah", kelas_kesesuaian: "Kelas N - Tidak Sesuai", kode_kelas: "N" },
            { komoditas: "Cabai Merah", skor_kecocokan: 0.0, label: "Rendah", kelas_kesesuaian: "Kelas N - Tidak Sesuai", kode_kelas: "N" },
          ],
        },
      },
    ];
    localStorage.setItem(STORAGE_KEYS.HISTORY, JSON.stringify(sample));
  }
}

function enterApplication(user) {
  localStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(user));
  document.getElementById("authScreen").classList.add("hidden");
  document.getElementById("appShell").classList.remove("hidden");

  const initials = user.nama.split(" ").map((w) => w[0]).slice(0, 2).join("").toUpperCase();
  document.getElementById("navUserInitials").textContent = initials || "PD";
  document.getElementById("navUserName").textContent = user.nama;
  document.getElementById("welcomeBadgeName").textContent = user.nama;
  document.getElementById("profileNameVal").textContent = user.nama;
  document.getElementById("profileEmailVal").textContent = user.email;
}

function switchTab(tabName) {
  document.querySelectorAll(".nav-pill-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.getAttribute("data-tab") === tabName);
  });
  document.querySelectorAll(".tab-view").forEach((view) => {
    view.classList.toggle("hidden", view.id !== `view-${tabName}`);
  });
  if (tabName === "rekomendasi") {
    showWizardInputStep();
  }
}

function showWizardInputStep() {
  document.getElementById("wizardInputCard").classList.remove("hidden");
  document.getElementById("wizardResultCard").classList.add("hidden");
}

function showWizardResultStep() {
  document.getElementById("wizardInputCard").classList.add("hidden");
  document.getElementById("wizardResultCard").classList.remove("hidden");
  window.scrollTo({ top: 0, behavior: "smooth" });
}

function applyPreset(key) {
  const d = PRESET_SCENARIOS[key];
  if (!d) return;
  document.getElementById("lokasiWilayah").value = d.lokasi_wilayah;
  document.getElementById("inputN").value = d.N;
  document.getElementById("inputP").value = d.P;
  document.getElementById("inputK").value = d.K;
  document.getElementById("inputTemp").value = d.temperature;
  document.getElementById("inputHumidity").value = d.humidity;
  document.getElementById("inputPh").value = d.ph;
  document.getElementById("inputRainfall").value = d.rainfall;
}

function renderCommoditiesGrid() {
  const container = document.getElementById("commoditiesGrid");
  container.innerHTML = INA_AGRO_COMMODITIES.map(
    (c) => `
    <div class="commodity-card">
      <div>
        <span class="comm-tag">#${c.no} • ${c.kategori}</span>
        <h4>${c.nama}</h4>
        <div class="comm-latin">${c.latin}</div>
        <div class="comm-source-pill">Kaggle: ${c.kaggleSlug}</div>
        <div class="comm-specs">${c.specs}</div>
      </div>
      <button type="button" class="btn-test-comm" data-try-preset="${c.presetKey}">
        Uji Lahan ${c.nama} →
      </button>
    </div>
  `
  ).join("");
}

function bindAllEvents() {
  document.getElementById("loginForm").addEventListener("submit", (e) => {
    e.preventDefault();
    const email = document.getElementById("loginEmail").value.trim() || "petani.demo@ina-agro.id";
    const nama =
      email === "petani.demo@ina-agro.id"
        ? "Petani Demo"
        : email.split("@")[0].replace(/[._]/g, " ").replace(/\w/g, (c) => c.toUpperCase());
    enterApplication({ nama, email });
  });

  document.getElementById("createAccountBtn").addEventListener("click", () => {
    enterApplication({ nama: "Petani Mitra Baru", email: "mitra.baru@ina-agro.id" });
  });

  document.querySelectorAll("[data-quick-nav]").forEach((tile) => {
    tile.addEventListener("click", () => {
      enterApplication({ nama: "Petani Demo", email: "petani.demo@ina-agro.id" });
      switchTab(tile.getAttribute("data-quick-nav"));
    });
  });

  document.querySelectorAll(".nav-pill-btn").forEach((btn) => {
    btn.addEventListener("click", () => switchTab(btn.getAttribute("data-tab")));
  });

  document.getElementById("brandLockup").addEventListener("click", () => switchTab("home"));
  document.getElementById("heroStartBtn").addEventListener("click", () => switchTab("rekomendasi"));

  document.getElementById("commoditiesGrid").addEventListener("click", (e) => {
    const btn = e.target.closest("[data-try-preset]");
    if (!btn) return;
    const key = btn.getAttribute("data-try-preset");
    document.getElementById("presetDropdown").value = key;
    applyPreset(key);
    switchTab("rekomendasi");
  });

  document.getElementById("presetDropdown").addEventListener("change", (e) => {
    applyPreset(e.target.value);
  });

  document.getElementById("backToHomeBtn").addEventListener("click", () => switchTab("home"));
  document.getElementById("backToInputBtn").addEventListener("click", () => showWizardInputStep());

  document.getElementById("landConditionForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const submitBtn = document.getElementById("submitPredictBtn");
    submitBtn.disabled = true;
    submitBtn.textContent = "Menganalisis Kondisi Lahan...";

    const payload = {
      lokasi_wilayah: document.getElementById("lokasiWilayah").value,
      N: parseFloat(document.getElementById("inputN").value),
      P: parseFloat(document.getElementById("inputP").value),
      K: parseFloat(document.getElementById("inputK").value),
      temperature: parseFloat(document.getElementById("inputTemp").value),
      humidity: parseFloat(document.getElementById("inputHumidity").value),
      ph: parseFloat(document.getElementById("inputPh").value),
      rainfall: parseFloat(document.getElementById("inputRainfall").value),
      consent_opt_in: document.getElementById("consentCheckbox").checked,
    };

    try {
      const res = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error("Server error");
      const data = await res.json();
      currentPayload = payload;
      currentPrediction = data;
      renderPredictionView(data);
      showWizardResultStep();
    } catch (err) {
      alert("Pastikan server FastAPI (python -m uvicorn app:app --reload) sedang berjalan di port 8000.");
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "Dapatkan Rekomendasi";
    }
  });

  document.getElementById("saveHistoryBtn").addEventListener("click", () => {
    if (!currentPrediction || !currentPayload) return;
    const history = JSON.parse(localStorage.getItem(STORAGE_KEYS.HISTORY) || "[]");
    history.unshift({
      id: Date.now(),
      timestamp: new Date().toLocaleString("id-ID", {
        day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit",
      }),
      payload: currentPayload,
      result: currentPrediction,
    });
    localStorage.setItem(STORAGE_KEYS.HISTORY, JSON.stringify(history));
    updateHistoryBadge();
    renderHistoryList();
    const btn = document.getElementById("saveHistoryBtn");
    btn.textContent = "✓ Tersimpan di Riwayat";
    setTimeout(() => { btn.textContent = "Simpan Riwayat"; }, 1800);
  });

  document.getElementById("viewDetailBtn").addEventListener("click", () => {
    if (!currentPrediction) return;
    document.getElementById("jsonPreviewBox").textContent = JSON.stringify(currentPrediction, null, 2);
    document.getElementById("detailModal").classList.remove("hidden");
  });

  document.getElementById("closeDetailModal").addEventListener("click", () => {
    document.getElementById("detailModal").classList.add("hidden");
  });

  document.getElementById("profileConsentCheckbox").addEventListener("change", (e) => {
    localStorage.setItem(STORAGE_KEYS.CONSENT, JSON.stringify(e.target.checked));
    document.getElementById("consentCheckbox").checked = e.target.checked;
  });

  document.getElementById("deleteHistoryBtn").addEventListener("click", () => {
    localStorage.setItem(STORAGE_KEYS.HISTORY, JSON.stringify([]));
    updateHistoryBadge();
    renderHistoryList();
  });

  document.getElementById("logoutBtn").addEventListener("click", () => {
    localStorage.removeItem(STORAGE_KEYS.USER);
    document.getElementById("appShell").classList.add("hidden");
    document.getElementById("authScreen").classList.remove("hidden");
  });
}

function renderPredictionView(data) {
  document.getElementById("resultLocationSubtitle").textContent = `Analisis kurasi Kaggle selesai • ${data.lokasi_wilayah}`;

  const anomalyArea = document.getElementById("resultAnomalyArea");
  if (data.anomali_cuaca && data.anomali_cuaca.length > 0) {
    anomalyArea.innerHTML = data.anomali_cuaca
      .map((a) => `<div class="anomaly-alert"><strong>Peringatan Anomali (${a.parameter}):</strong> ${a.pesan}</div>`)
      .join("");
  } else {
    anomalyArea.innerHTML = "";
  }

  const top3Area = document.getElementById("resultTop3Area");
  top3Area.innerHTML = data.rekomendasi_top3
    .map(
      (item, idx) => `
      <div class="result-rank-card ${idx === 0 ? "is-top1" : ""}">
        <div class="result-rank-top">
          <div>
            <div class="rank-eyebrow">${idx === 0 ? "REKOMENDASI UTAMA" : `ALTERNATIF #${idx + 1}`}</div>
            <div class="rank-commodity-name">${item.komoditas}</div>
            <span class="rank-class-pill cls-${item.kode_kelas}">${item.kelas_kesesuaian}</span>
            <div class="rank-source-sub">Sumber Kaggle: ${item.sumber_kaggle}</div>
          </div>
          <div class="rank-score-box">
            <div class="rank-score-num">${item.skor_kecocokan}%</div>
            <div class="rank-score-sub">tingkat kesesuaian (${item.label})</div>
          </div>
        </div>
      </div>
    `
    )
    .join("");

  const factorArea = document.getElementById("resultFactorsArea");
  factorArea.innerHTML = data.faktor_penjelas
    .map(
      (f) => `
      <div class="factor-tile">
        <div class="factor-tile-label">${f.faktor}</div>
        <div class="factor-tile-val">${f.nilai}</div>
        <div class="factor-tile-status ${f.status === "Sesuai" ? "st-sesuai" : "st-warn"}">${f.status}</div>
      </div>
    `
    )
    .join("");

  const topCode = data.rekomendasi_top3[0].kode_kelas;
  document.querySelectorAll("[data-legend-code]").forEach((row) => {
    const code = row.getAttribute("data-legend-code");
    row.style.background = code === topCode ? "var(--green-100)" : "#ffffff";
    row.style.borderColor = code === topCode ? "var(--green-700)" : "var(--border)";
  });

  document.getElementById("resultDisclaimer").textContent = data.catatan;
}

function updateHistoryBadge() {
  const history = JSON.parse(localStorage.getItem(STORAGE_KEYS.HISTORY) || "[]");
  document.getElementById("navHistoryCount").textContent = history.length;
}

function renderHistoryList() {
  const container = document.getElementById("historyContainer");
  const history = JSON.parse(localStorage.getItem(STORAGE_KEYS.HISTORY) || "[]");
  if (history.length === 0) {
    container.innerHTML = `<p style="color:var(--text-muted); font-size:0.9rem;">Belum ada riwayat evaluasi lahan tersimpan.</p>`;
    return;
  }

  container.innerHTML = history
    .map((h) => {
      const top = h.result.rekomendasi_top3[0];
      return `
        <div class="result-rank-card" style="margin-bottom:12px;">
          <div class="result-rank-top">
            <div>
              <div style="font-size:0.78rem; color:var(--text-muted);">${h.timestamp}</div>
              <div style="font-size:1.02rem; font-weight:800; margin:2px 0;">${h.payload.lokasi_wilayah}</div>
              <div style="font-size:0.82rem; color:var(--text-body);">
                N:${h.payload.N} P:${h.payload.P} K:${h.payload.K} • Suhu ${h.payload.temperature}°C • Kelembapan ${h.payload.humidity}% • pH ${h.payload.ph} • Hujan ${h.payload.rainfall} mm
              </div>
            </div>
            <div class="rank-score-box">
              <div style="font-weight:800; color:var(--green-800); font-size:1.05rem;">${top.komoditas} (${top.skor_kecocokan}%)</div>
              <span class="rank-class-pill cls-${top.kode_kelas}">${top.kelas_kesesuaian}</span>
            </div>
          </div>
        </div>
      `;
    })
    .join("");
}

function syncConsentCheckboxes() {
  const val = JSON.parse(localStorage.getItem(STORAGE_KEYS.CONSENT) || "false");
  document.getElementById("consentCheckbox").checked = val;
  document.getElementById("profileConsentCheckbox").checked = val;
}
