/**
 * Watering App - Modern Vanilla JavaScript
 * A lightweight frontend for the watering system
 */

const API_BASE = "/watering.api";
const MAX_TANK_ML = 5000;

// DOM Elements
const elements = {
  controls: document.getElementById("controls"),
  loading: document.getElementById("loading"),
  lastRefill: document.getElementById("last-refill"),
  progressFill: document.getElementById("progress-fill"),
  historyList: document.getElementById("history-list"),
  status: document.getElementById("status"),
  refillBtn: document.getElementById("refill-btn"),
  refillDialog: document.getElementById("refill-dialog"),
  refillVolume: document.getElementById("refill-volume"),
  dialogCancel: document.getElementById("dialog-cancel"),
};

// State
let isWatering = false;

/**
 * Format a date as relative time (e.g., "5 minutes ago")
 */
function formatRelativeTime(dateString) {
  const date = new Date(dateString + "Z"); // Assume UTC
  const now = new Date();
  const diffMs = now - date;
  const diffSec = Math.floor(diffMs / 1000);
  const diffMin = Math.floor(diffSec / 60);
  const diffHour = Math.floor(diffMin / 60);
  const diffDay = Math.floor(diffHour / 24);

  const rtf = new Intl.RelativeTimeFormat("en", { numeric: "auto" });

  if (diffSec < 60) return rtf.format(-diffSec, "second");
  if (diffMin < 60) return rtf.format(-diffMin, "minute");
  if (diffHour < 24) return rtf.format(-diffHour, "hour");
  if (diffDay < 30) return rtf.format(-diffDay, "day");

  return date.toLocaleDateString();
}

/**
 * Update status message
 */
function setStatus(message, type = "info") {
  elements.status.textContent = message;
  elements.status.className = `status ${type}`;
}

/**
 * Show/hide loading state
 */
function setLoading(loading) {
  isWatering = loading;
  elements.controls.classList.toggle("hidden", loading);
  elements.loading.classList.toggle("hidden", !loading);

  // Disable all buttons while loading
  document.querySelectorAll(".btn").forEach((btn) => {
    btn.disabled = loading;
  });
}

/**
 * Fetch history from API
 */
async function fetchHistory() {
  try {
    const response = await fetch(`${API_BASE}/history`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    const data = await response.json();
    renderHistory(data);
    setStatus("Ready");
  } catch (error) {
    console.error("Failed to fetch history:", error);
    setStatus(`Error: ${error.message}`, "error");
    renderEmptyHistory();
  }
}

/**
 * Render history data
 */
function renderHistory(data) {
  // Last refill
  const refillInfo = elements.lastRefill;
  if (data.last_filling) {
    const fillDate = formatRelativeTime(data.last_filling.filldate);
    const remaining = data.remaining || 0;
    const total = data.last_filling.quantity || MAX_TANK_ML;
    const percent = Math.max(0, Math.min(100, (remaining / MAX_TANK_ML) * 100));

    refillInfo.querySelector(".refill-date").textContent = fillDate;
    refillInfo.querySelector(
      ".refill-remaining"
    ).textContent = `${remaining}ml of ${total}ml remaining`;
    elements.progressFill.style.width = `${percent}%`;
  } else {
    refillInfo.querySelector(".refill-date").textContent = "No refills yet";
    refillInfo.querySelector(".refill-remaining").textContent = "";
    elements.progressFill.style.width = "0%";
  }

  // Watering history
  const list = elements.historyList;
  if (data.history && data.history.length > 0) {
    list.innerHTML = data.history
      .map(
        (item) => `
        <li>
          <span class="quantity">${item.quantity}ml</span>
          <span class="time">${formatRelativeTime(item.waterdate)}</span>
        </li>
      `
      )
      .join("");
  } else {
    list.innerHTML = '<li class="empty-state">No recent waterings</li>';
  }
}

/**
 * Render empty history state
 */
function renderEmptyHistory() {
  elements.lastRefill.querySelector(".refill-date").textContent = "—";
  elements.lastRefill.querySelector(".refill-remaining").textContent = "";
  elements.progressFill.style.width = "0%";
  elements.historyList.innerHTML =
    '<li class="empty-state">Unable to load history</li>';
}

/**
 * Trigger watering
 */
async function water(volume) {
  if (isWatering) return;

  setLoading(true);
  setStatus(`Watering ${volume}ml...`);

  try {
    const response = await fetch(`${API_BASE}/water/${volume}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    const data = await response.json();
    setStatus(`Watered ${data.volume}ml in ${data.duration}s`, "success");
    await fetchHistory();
  } catch (error) {
    console.error("Watering failed:", error);
    setStatus(`Error: ${error.message}`, "error");
  } finally {
    setLoading(false);
  }
}

/**
 * Record a refill
 */
async function recordRefill(volume) {
  setStatus(`Recording refill of ${volume}ml...`);

  try {
    const response = await fetch(`${API_BASE}/fill/${volume}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);

    setStatus(`Refill of ${volume}ml recorded`, "success");
    await fetchHistory();
  } catch (error) {
    console.error("Refill failed:", error);
    setStatus(`Error: ${error.message}`, "error");
  }
}

/**
 * Open refill dialog
 */
function openRefillDialog() {
  elements.refillVolume.value = MAX_TANK_ML;
  elements.refillDialog.showModal();
}

/**
 * Initialize event listeners
 */
function initEventListeners() {
  // Watering buttons
  elements.controls.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-volume]");
    if (btn) {
      const volume = parseInt(btn.dataset.volume, 10);
      water(volume);
    }
  });

  // Refill button
  elements.refillBtn.addEventListener("click", openRefillDialog);

  // Dialog cancel
  elements.dialogCancel.addEventListener("click", () => {
    elements.refillDialog.close();
  });

  // Dialog submit
  elements.refillDialog.addEventListener("close", () => {
    if (elements.refillDialog.returnValue === "") return; // Cancelled

    const volume = parseInt(elements.refillVolume.value, 10);
    if (volume > 0) {
      recordRefill(volume);
    }
  });

  // Close dialog on backdrop click
  elements.refillDialog.addEventListener("click", (e) => {
    if (e.target === elements.refillDialog) {
      elements.refillDialog.close();
    }
  });
}

// Initialize app
document.addEventListener("DOMContentLoaded", () => {
  initEventListeners();
  fetchHistory();
});
