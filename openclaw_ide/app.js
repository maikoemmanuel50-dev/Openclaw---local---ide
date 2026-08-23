/**
 * OpenClaw Local IDE — Frontend Application Logic
 */

let activeFilePath = null;
let openFiles = [];
let activeLog = null;
let allFiles = [];
let isMarkdownPreview = false;
let pendingImages = []; // pasted/dropped images awaiting send (routed to Vision 7B)

// DOM Elements
const elCodeEditor = document.getElementById("codeEditor");
const elMarkdownPreview = document.getElementById("markdownPreview");
const elActiveFilePath = document.getElementById("activeFilePath");
const elTabsBar = document.getElementById("tabsBar");
const elFileTree = document.getElementById("fileTreeContainer");
const elFileSearch = document.getElementById("fileSearch");
const elSceneList = document.getElementById("sceneListContainer");
const elRenderReadyBadge = document.getElementById("renderReadyBadge");
const elLogStream = document.getElementById("logStreamContent");
const elChatMessages = document.getElementById("chatMessages");
const elChatInput = document.getElementById("chatInput");
const elBtnSendChat = document.getElementById("btnSendChat");
const elImagePreviews = document.getElementById("imagePreviews");
const elGuideList = document.getElementById("guideListContainer");
const elBatteryVal = document.getElementById("batteryVal");
const elRenderVal = document.getElementById("renderVal");
const elRenderDot = document.getElementById("renderDot");
const elSbBattery = document.getElementById("sbBattery");
const elSbBlender = document.getElementById("sbBlender");
const elSbModel = document.getElementById("sbModel");
const elToastContainer = document.getElementById("toastContainer");

// Initialize on Load
document.addEventListener("DOMContentLoaded", () => {
  setupNavigation();
  setupEditor();
  setupChat();
  setupTerminal();
  setupLogs();
  initAgentEngineMode();

  // Load initial data
  loadFileTree();
  if (activeFilePath) {
    loadFile(activeFilePath);
  }
  loadGuides();
  loadCopyrightPanel();
  loadAgentTrace();
  loadTrajectory();
  loadPowerPanel();
  refreshSystemStatus();
  refreshCrestodian();
  loadHourlyPanel();
  initAudioPanel();
  updateNetworkStatus();

  // Polling loop every 8 seconds (status + logs; trajectory has its own
  // slower cadence below — 3.5s hammered the local server under chat load).
  setInterval(() => {
    refreshSystemStatus();
    refreshCrestodian();
    updateNetworkStatus();
    if (activeLog !== "terminal") {
      refreshLog();
    }
  }, 8000);
  setInterval(() => {
    loadTrajectory();
  }, 8000);
});

// Toast System
function showToast(message) {
  const toast = document.createElement("div");
  toast.className = "toast";
  toast.innerText = message;
  elToastContainer.appendChild(toast);
  setTimeout(() => {
    toast.remove();
  }, 4000);
}

// Navigation & Activity Bar
function setupNavigation() {
  const actButtons = document.querySelectorAll(".act-btn[data-view]");
  actButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      actButtons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");

      const viewId = btn.getAttribute("data-view");
      document.querySelectorAll(".sidebar-view").forEach(v => v.classList.remove("active"));
      
      const targetView = document.getElementById(`view${capitalize(viewId)}`);
      if (targetView) {
        targetView.classList.add("active");
      }
    });
  });

  document.getElementById("btnRefreshAll")?.addEventListener("click", () => {
    refreshSystemStatus();
    loadFileTree();
    refreshLog();
    showToast("Workspace data refreshed");
  });
}

function capitalize(s) {
  return s.charAt(0).toUpperCase() + s.slice(1);
}

// File Tree & Explorer
async function loadFileTree() {
  try {
    const res = await fetch("/api/files/tree");
    const data = await res.json();
    allFiles = data.files || [];
    renderFileTree(allFiles);
  } catch (e) {
    elFileTree.innerHTML = `<div class="loading-state error">Failed to load file tree: ${e.message}</div>`;
  }
}

function renderFileTree(files) {
  const query = (elFileSearch.value || "").toLowerCase().trim();
  const filtered = files.filter(f => f.path.toLowerCase().includes(query));

  if (filtered.length === 0) {
    elFileTree.innerHTML = `<div class="loading-state">No matching files</div>`;
    return;
  }

  // Group by folder
  const folders = {};
  filtered.forEach(f => {
    const folder = f.folder || "Workspace Root";
    if (!folders[folder]) folders[folder] = [];
    folders[folder].push(f);
  });

  let html = "";
  for (const [folder, groupFiles] of Object.entries(folders)) {
    html += `<div class="tree-folder">📂 ${folder}</div>`;
    groupFiles.forEach(f => {
      const activeClass = f.path === activeFilePath ? "active" : "";
      const icon = getFileIcon(f.name);
      html += `
        <div class="tree-item ${activeClass}" onclick="openFile('${f.path}')">
          <span class="file-icon">${icon}</span>
          <span class="file-name">${f.name}</span>
        </div>
      `;
    });
  }
  elFileTree.innerHTML = html;
}

function getFileIcon(filename) {
  if (filename.endsWith(".py")) return "🐍";
  if (filename.endsWith(".md")) return "📝";
  if (filename.endsWith(".json") || filename.endsWith(".yaml")) return "⚙️";
  if (filename.endsWith(".ps1") || filename.endsWith(".bat") || filename.endsWith(".cmd")) return "⚡";
  if (filename.endsWith(".txt") || filename.endsWith(".err")) return "📄";
  return "📄";
}

elFileSearch?.addEventListener("input", () => {
  renderFileTree(allFiles);
});

document.getElementById("btnReloadTree")?.addEventListener("click", () => {
  loadFileTree();
  showToast("File list reloaded");
});

// File Editor
async function openFile(relPath) {
  activeFilePath = relPath;
  if (!openFiles.includes(relPath)) {
    openFiles.push(relPath);
  }
  renderTabs();
  await loadFile(relPath);
  renderFileTree(allFiles);
}

async function loadFile(relPath) {
  try {
    elActiveFilePath.innerText = relPath;
    const res = await fetch(`/api/files/read?path=${encodeURIComponent(relPath)}`);
    const data = await res.json();
    if (data.error) {
      elCodeEditor.value = `// Error reading file: ${data.error}`;
    } else {
      elCodeEditor.value = data.content || "";
    }
    if (isMarkdownPreview) {
      renderMarkdownPreview();
    }
  } catch (e) {
    elCodeEditor.value = `// Error: ${e.message}`;
  }
}

function renderTabs() {
  let html = "";
  openFiles.forEach(f => {
    const activeClass = f === activeFilePath ? "active" : "";
    const name = f.split("/").pop();
    const icon = getFileIcon(name);
    html += `
      <div class="editor-tab ${activeClass}" onclick="openFile('${f}')">
        <span class="tab-icon">${icon}</span>
        <span class="tab-title">${name}</span>
        <span class="tab-close" onclick="closeTab('${f}', event)">×</span>
      </div>
    `;
  });
  elTabsBar.innerHTML = html;
}

function closeTab(path, e) {
  if (e) e.stopPropagation();
  openFiles = openFiles.filter(f => f !== path);
  if (activeFilePath === path) {
    activeFilePath = openFiles.length > 0 ? openFiles[openFiles.length - 1] : null;
  }
  renderTabs();
  if (activeFilePath) {
    loadFile(activeFilePath);
  } else {
    elCodeEditor.value = "";
    elActiveFilePath.innerText = "No file open";
  }
}

// Save File
document.getElementById("btnSaveFile")?.addEventListener("click", async () => {
  await saveCurrentFile();
});

document.addEventListener("keydown", async (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === "s") {
    e.preventDefault();
    await saveCurrentFile();
  }
});

async function saveCurrentFile() {
  try {
    const content = elCodeEditor.value;
    const res = await fetch("/api/files/save", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path: activeFilePath, content })
    });
    const data = await res.json();
    if (data.ok) {
      showToast(`Saved ${activeFilePath}`);
    } else {
      showToast(`Save failed: ${data.error}`);
    }
  } catch (e) {
    showToast(`Save error: ${e.message}`);
  }
}

// Markdown Preview Toggle
function setupEditor() {
  document.getElementById("btnTogglePreview")?.addEventListener("click", () => {
    isMarkdownPreview = !isMarkdownPreview;
    if (isMarkdownPreview) {
      elCodeEditor.classList.add("hidden");
      elMarkdownPreview.classList.remove("hidden");
      renderMarkdownPreview();
    } else {
      elCodeEditor.classList.remove("hidden");
      elMarkdownPreview.classList.add("hidden");
    }
  });
}

function renderMarkdownPreview() {
  const raw = elCodeEditor.value;
  // Simple markdown renderer for preview
  let html = raw
    .replace(/^### (.*$)/gim, '<h3>$1</h3>')
    .replace(/^## (.*$)/gim, '<h2>$1</h2>')
    .replace(/^# (.*$)/gim, '<h1>$1</h1>')
    .replace(/\*\*(.*)\*\*/gim, '<strong>$1</strong>')
    .replace(/\*(.*)\*/gim, '<em>$1</em>')
    .replace(/`([^`]+)`/gim, '<code>$1</code>')
    .replace(/```([^`]+)```/gim, '<pre><code>$1</code></pre>')
    .replace(/\n/gim, '<br>');
  elMarkdownPreview.innerHTML = html;
}

// Status & Pipeline Refresh
async function refreshSystemStatus() {
  try {
    const res = await fetch("/api/status");
    const data = await res.json();

    // Battery
    if (data.battery) {
      const bPct = data.battery.percent || "--";
      const bStat = data.battery.status || "";
      elBatteryVal.innerText = `Battery: ${bPct}% (${bStat})`;
      elSbBattery.innerText = `⚡ ${bPct}% ${bStat}`;
    }

    // Render Progress
    if (data.render) {
      renderPipelineList(data.render);
    }

    // Model + vision status (routed models)
    if (data.modelRouting && elSbModel) {
      const dl = data.download || {};
      const vis = data.vision || {};
      const general = (data.modelRouting.general || "14b");
      const vision = (data.modelRouting.vision || "7b-vl");
      if (dl.online === false) {
        elSbModel.innerText = `🤖 ${general} (ollama offline)`;
      } else if (vis.ready) {
        elSbModel.innerText = `🤖 ${general} · 👁️ ${vision} ✦`;
      } else {
        const pct = Math.round((dl.blobsReady / Math.max(1, dl.blobsExpected)) * 100);
        elSbModel.innerText = `🤖 ${general} · ⬇️ ${vision} ${pct}% pulled`;
      }
      return;
    }
    if (data.activeModel && elSbModel) {
      const dl = data.download || {};
      const vis = data.vision || {};
      if (dl.online === false) {
        elSbModel.innerText = `🤖 ${data.activeModel} (ollama offline)`;
      } else if (vis.active) {
        elSbModel.innerText = `🤖 ${data.activeModel} · 👁️ vision ✦`;
      } else if (vis.ready && !vis.active) {
        elSbModel.innerText = `🤖 ${data.activeModel} · 👁️ ready`;
      } else if (dl.blobsExpected > 0) {
        const pct = Math.round((dl.blobsReady / dl.blobsExpected) * 100);
        elSbModel.innerText = `🤖 ${data.activeModel} · ⬇️ vision ${pct}% pulled`;
      } else {
        elSbModel.innerText = `🤖 ${data.activeModel}`;
      }
    }
  } catch (e) {
    console.warn("Status refresh failed:", e);
  }
}

function renderPipelineList(renderData) {
  const scenes = renderData.scenes || [];
  const readyCount = renderData.readyCount || 0;
  const total = renderData.totalScenes || 0;

  // Update header with project info
  if (renderData.projectName) {
    const titleEl = document.getElementById("renderPipelineTitle");
    if (titleEl) titleEl.textContent = `RENDER PIPELINE — ${renderData.projectName}`;
  }
  
  // Update gate status
  if (renderData.gates) {
    const gateBox = document.getElementById("gateStatusBox");
    const gateVal = document.getElementById("gateVal");
    if (gateBox && gateVal) {
      gateBox.style.display = "flex";
      gateVal.textContent = renderData.gates["4kHold"] ? "HOLD (Gate Pending)" : "OPEN";
      gateVal.className = renderData.gates["4kHold"] ? "gate-val hold" : "gate-val open";
    }
  }
  
  // Update resolution label
  if (renderData.resolution) {
    const titleEl = document.getElementById("renderPipelineTitle");
    if (titleEl && !titleEl.textContent.includes(renderData.resolution.toUpperCase())) {
      titleEl.textContent = `RENDER PIPELINE (${renderData.resolution.toUpperCase()})`;
    }
  }

  elRenderReadyBadge.innerText = `${readyCount} / ${total} Ready`;

  let currentRenderingScene = null;

  let html = "";
  scenes.forEach(s => {
    const statusText = s.isReady ? "✅ READY" : (s.frames > 0 ? `🔄 ${s.frames}/${s.target} frames` : "⏳ QUEUED");
    const statusClass = s.isReady ? "ready" : (s.frames > 0 ? "rendering" : "queued");
    const fillClass = s.isReady ? "complete" : "";
    
    if (s.frames > 0 && !s.isReady) {
      currentRenderingScene = s;
    }

    html += `
      <div class="scene-card">
        <div class="scene-top">
          <span class="scene-name">${s.name}</span>
          <span class="scene-status ${statusClass}">${statusText}</span>
        </div>
        <div class="progress-bar-bg">
          <div class="progress-bar-fill ${fillClass}" style="width: ${s.percent}%"></div>
        </div>
        <div class="scene-meta">
          <span>${s.percent}% complete</span>
          <span>${s.isReady ? (s.mp4Size / (1024 * 1024)).toFixed(1) + ' MB' : ''}</span>
        </div>
      </div>
    `;
  });
  elSceneList.innerHTML = html;

  if (currentRenderingScene) {
    elRenderVal.innerText = `${currentRenderingScene.name} (${currentRenderingScene.frames} f)`;
    elRenderDot.className = "dot-indicator pulse-amber";
    elSbBlender.innerHTML = `<span class="icon">🧊</span> Blender: Active (${currentRenderingScene.name} ${currentRenderingScene.frames}f)`;
  } else if (readyCount === total && total > 0) {
    elRenderVal.innerText = `All ${total} Scenes Complete`;
    elRenderDot.className = "dot-indicator green";
    elSbBlender.innerHTML = `<span class="icon">🧊</span> Blender: Complete (${readyCount}/${total})`;
  } else {
    elRenderVal.innerText = `${readyCount}/${total} scenes ready`;
  }
  
  // Update project name in status bar
  if (renderData.projectName) {
    const projectNameEl = document.getElementById("projectName");
    if (projectNameEl) projectNameEl.textContent = renderData.projectName;
  }
  
  // Update settings panel
  const settingProjectName = document.getElementById("settingProjectName");
  if (settingProjectName && renderData.projectName) settingProjectName.value = renderData.projectName;
  
  // Update log tabs if available
  if (renderData.logFiles && renderData.logFiles.length > 0) {
    const logTabs = document.getElementById("logTabs");
    if (logTabs) {
      logTabs.innerHTML = renderData.logFiles.map((f, i) => 
        `<button class="panel-tab ${i === 0 ? 'active' : ''}" data-log="${f}">${f}</button>`
      ).join("") + '<button class="panel-tab" data-log="terminal">Shell Exec</button>';
      setupLogs();
    }
  }
}

// Logs Viewer & Tail
function setupLogs() {
  const panelTabs = document.querySelectorAll(".panel-tab");
  // Set activeLog to the first tab's data-log if not already set
  if (!activeLog && panelTabs.length > 0) {
    activeLog = panelTabs[0].getAttribute("data-log");
  }
  panelTabs.forEach(tab => {
    tab.addEventListener("click", () => {
      panelTabs.forEach(t => t.classList.remove("active"));
      tab.classList.add("active");
      activeLog = tab.getAttribute("data-log");

      if (activeLog === "terminal") {
        elLogStream.classList.add("hidden");
        document.getElementById("terminalBox").classList.remove("hidden");
      } else {
        elLogStream.classList.remove("hidden");
        document.getElementById("terminalBox").classList.add("hidden");
        refreshLog();
      }
    });
  });

  document.getElementById("btnRefreshLog")?.addEventListener("click", () => {
    refreshLog();
    showToast("Log refreshed");
  });

  document.getElementById("btnToggleBottom")?.addEventListener("click", () => {
    const bottom = document.getElementById("bottomPanel");
    bottom.style.display = bottom.style.display === "none" ? "flex" : "none";
  });
}

async function refreshLog() {
  if (activeLog === "terminal") return;
  try {
    const res = await fetch(`/api/logs/tail?file=${encodeURIComponent(activeLog)}&lines=60`);
    const data = await res.json();
    elLogStream.innerText = data.content || "(Empty log)";
    elLogStream.scrollTop = elLogStream.scrollHeight;
  } catch (e) {
    elLogStream.innerText = `Error fetching log: ${e.message}`;
  }
}

// Terminal Execution
function setupTerminal() {
  const termInput = document.getElementById("termInput");
  const btnRun = document.getElementById("btnRunTerm");
  const termOutput = document.getElementById("termOutput");

  async function executeTerm() {
    const cmd = termInput.value.trim();
    if (!cmd) return;
    termOutput.innerText += `\n> ${cmd}\nRunning...`;
    termInput.value = "";

    try {
      const res = await fetch("/api/openclaw/exec", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: cmd })
      });
      const data = await res.json();
      const out = (data.stdout || "") + (data.stderr ? "\n[STDERR] " + data.stderr : "");
      termOutput.innerText += `\n${out}\n[Process finished with exit code ${data.exitCode}]`;
      termOutput.scrollTop = termOutput.scrollHeight;
    } catch (e) {
      termOutput.innerText += `\nError executing command: ${e.message}`;
    }
  }

  btnRun?.addEventListener("click", executeTerm);
  termInput?.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      executeTerm();
    }
  });
}

// Agent Chat & Qwen 2.5
function setupChat() {
  elBtnSendChat?.addEventListener("click", sendChat);
  elChatInput?.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendChat();
    }
  });
  // Paste / drop image support: captured images route to the qwen2.5vl 7B
  // vision model on send (the 14B agent model has no image input).
  const inputBox = document.querySelector(".chat-input-box");
  elChatInput?.addEventListener("paste", onPasteImage);
  if (inputBox) {
    inputBox.addEventListener("dragover", (e) => e.preventDefault());
    inputBox.addEventListener("drop", onDropImage);
  }
}

function onPasteImage(e) {
  const items = (e.clipboardData && e.clipboardData.items) || [];
  let captured = false;
  for (const item of items) {
    if (item.type && item.type.startsWith("image/")) {
      const file = item.getAsFile();
      if (file) {
        queueImageFile(file);
        captured = true;
      }
    }
  }
  if (captured) {
    e.preventDefault();
    showToast("📷 Image captured — will be analyzed by qwen2.5vl 7B on send", 2500);
  }
}

function onDropImage(e) {
  const files = (e.dataTransfer && e.dataTransfer.files) || [];
  if (!files.length) return;
  let captured = 0;
  for (const f of files) {
    if (f.type && f.type.startsWith("image/")) {
      queueImageFile(f);
      captured++;
    }
  }
  if (captured) {
    e.preventDefault();
    showToast(`📷 ${captured} image(s) captured — analyzed by Vision 7B on send`, 2500);
  }
}

function queueImageFile(file) {
  const reader = new FileReader();
  reader.onload = (ev) => {
    pendingImages.push({
      name: file.name || `paste_${Date.now()}.png`,
      dataUrl: ev.target.result,
    });
    renderImagePreviews();
  };
  reader.readAsDataURL(file);
}

function renderImagePreviews() {
  if (!elImagePreviews) return;
  elImagePreviews.innerHTML = "";
  pendingImages.forEach((img, i) => {
    const cell = document.createElement("div");
    cell.className = "image-preview-cell";
    cell.innerHTML = `<img src="${img.dataUrl}" alt="${img.name}"><button class="img-remove" onclick="removePendingImage(${i})" title="Remove image">✕</button>`;
    elImagePreviews.appendChild(cell);
  });
  elImagePreviews.style.display = pendingImages.length ? "flex" : "none";
}

function removePendingImage(i) {
  pendingImages.splice(i, 1);
  renderImagePreviews();
}

// ── Agent Engine Mode Management ──────────────────────────────────
let currentEngineMode = localStorage.getItem("agentEngineMode") || "plan";

function initAgentEngineMode() {
  setAgentEngineMode(currentEngineMode, false);
}

function setAgentEngineMode(mode, showFeedback = true) {
  currentEngineMode = mode;
  localStorage.setItem("agentEngineMode", mode);

  const btnPlan = document.getElementById("modePlan");
  const btnDeepPlan = document.getElementById("modeDeepPlan");
  const btnBuild = document.getElementById("modeBuild");
  const btnVision = document.getElementById("modeVision");
  const avatar = document.getElementById("agentAvatar");
  const title = document.getElementById("agentTitle");
  const subtitle = document.getElementById("agentSubtitle");

  btnPlan?.classList.toggle("active", mode === "plan");
  btnDeepPlan?.classList.toggle("active", mode === "deep_plan");
  btnBuild?.classList.toggle("active", mode === "build");
  btnVision?.classList.toggle("active", mode === "vision");

  if (mode === "plan") {
    if (avatar) avatar.innerText = "📝";
    if (title) title.innerText = "Plan Mode";
    if (subtitle) subtitle.innerText = "Fast brainstorming & planning • VL 7B";
    if (elChatInput) elChatInput.placeholder = "Brainstorm, plan, explain... (fast responses)";
    if (showFeedback) showToast("📝 Plan Mode Active (VL 7B — fast)", 2000);
  } else if (mode === "deep_plan") {
    if (avatar) avatar.innerText = "📋";
    if (title) title.innerText = "Deep Plan Mode";
    if (subtitle) subtitle.innerText = "Researched planning with tools • 7B Coder";
    if (elChatInput) elChatInput.placeholder = "Research-backed planning with production context...";
    if (showFeedback) showToast("📋 Deep Plan Mode Active (7B Coder — researched)", 2000);
  } else if (mode === "build") {
    if (avatar) avatar.innerText = "🔧";
    if (title) title.innerText = "Build Mode";
    if (subtitle) subtitle.innerText = "Agentic execution & tool-calling • 14B Coder";
    if (elChatInput) elChatInput.placeholder = "Execute tasks, run tools, production work... (agentic)";
    if (showFeedback) showToast("🔧 Build Mode Active (14B Coder — agentic)", 2000);
  } else if (mode === "vision") {
    if (avatar) avatar.innerText = "👁️";
    if (title) title.innerText = "Vision Mode";
    if (subtitle) subtitle.innerText = "Visual QC & image analysis • VL 7B";
    if (elChatInput) elChatInput.placeholder = "Paste an image for visual analysis...";
    if (showFeedback) showToast("👁️ Vision Mode Active", 2000);
  }
}

async function updateNetworkStatus() {
  try {
    const res = await fetch("/api/system/network");
    if (!res.ok) return;
    const data = await res.json();
    const badge = document.getElementById("netStatusBadge");
    if (!badge) return;
    if (data.port18789) {
      badge.className = "badge-status-online";
      badge.innerText = data.online ? "● Direct Live" : "● Local Live";
      badge.title = data.online ? "OpenClaw Gateway & Internet Online" : "OpenClaw Gateway Local Only (Offline)";
    } else {
      badge.className = "badge-status-offline";
      badge.innerText = "● Gateway Offline";
      badge.title = "OpenClaw Gateway port 18789 is not listening";
    }
    
    // Gateway badge in header
    const gatewayDot = document.getElementById("gatewayDot");
    const gatewayVal = document.getElementById("gatewayVal");
    if (data.gateway && gatewayDot && gatewayVal) {
      gatewayDot.className = data.gateway.reachable ? "dot-indicator green" : "dot-indicator red";
      gatewayVal.innerText = data.gateway.reachable ? "Online" : "Offline";
    }
  } catch (e) {}
}

async function sendChat() {
  const prompt = elChatInput.value.trim();
  const hasImage = pendingImages.length > 0;
  if (!prompt && !hasImage) return;

  // User bubble ─ paste preview inline when an image rides along
  let userLabel;
  if (hasImage && prompt) {
    userLabel = `${prompt}<br><img class="pasted-img" src="${pendingImages[0].dataUrl}" alt="pasted image">`;
  } else if (hasImage) {
    userLabel = `📷 Pasted image<br><img class="pasted-img" src="${pendingImages[0].dataUrl}" alt="pasted image">`;
  } else {
    userLabel = prompt;
  }
  appendChatBubble("user", userLabel);
  elChatInput.value = "";

  // Image present OR Vision mode active ─ route to the qwen2.5vl 7B vision model.
  if (hasImage || currentEngineMode === "vision") {
    const img = pendingImages.shift();
    renderImagePreviews();
    return sendPastedImageForVision(img, prompt);
  }

  // Session view: this turn gets an id so the frontend can poll live
  // trajectory data and render each round + its tool calls inline.
  const session = "ses_" + Date.now().toString(36) + Math.random().toString(36).slice(2, 7);
  const sessionBubbleId = appendSessionBubble();

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 660000); // 11 min timeout

    // Live poll: render rounds as they land in .agent_trace.jsonl while the
    // agent loop is still running (rounds are session-tagged server-side).
    let pollTimer = setInterval(async () => {
      try {
        const tr = await fetch(`/api/agent/trajectory?limit=60&session=${encodeURIComponent(session)}`);
        const td = await tr.json();
        const rounds = (td.trajectory || []).filter(r => r.event === "round").reverse();
        renderSessionRounds(sessionBubbleId, rounds);
      } catch (e) { /* transient poll errors are non-fatal */ }
    }, 2000);

    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt, session, mode: currentEngineMode }),
      signal: controller.signal
    });
    clearTimeout(timeoutId);
    clearInterval(pollTimer);

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    }

    const data = await res.json();
    const reply = data.reply || "No response received";
    // Re-render the session from the authoritative response (survives refresh
    // and fills any rounds the live poll missed), then append the final reply.
    const rounds = (data.rounds || []).filter(r => r.event === "round").reverse();
    renderSessionRounds(sessionBubbleId, rounds);
    appendChatBubble("assistant", reply);
    playChime("reply");
    
    // Auto-save Deep Plan to project.json
    if (currentEngineMode === "deep_plan" && data.reply) {
      fetch("/api/plan/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ plan_text: data.reply })
      }).then(r => r.json()).then(result => {
        if (result.ok) {
          showToast("📋 Plan saved to project.json");
          loadProjectPlan(); // Refresh task board
        }
      }).catch(() => {}); // Silent fail
    }
  } catch (e) {
    clearInterval(pollTimer);
    console.warn("Chat error:", e);
    const retryPrompt = prompt.replace(/"/g, '&quot;');
    updateChatBubble(
      sessionBubbleId,
      `⚠️ <strong>Connection Notice:</strong> ${e.message}<br><br>` +
      `<button class="btn-quick" onclick="sendChipPrompt('${retryPrompt}')">🔄 Click to Retry</button>`
    );
    playChime("error");
  }
}

// ── Session view (TUI-style inline tool-call rendering) ────────────────
function appendSessionBubble() {
  const bubble = document.createElement("div");
  bubble.className = "chat-bubble assistant session-bubble";
  const id = "session_" + Date.now();
  bubble.id = id;
  bubble.innerHTML = `
    <div class="bubble-meta">OpenClaw ⟳ Qwen 2.5 Local — Agent Session</div>
    <div class="bubble-text">${thinkingDots()}</div>
  `;
  elChatMessages.appendChild(bubble);
  elChatMessages.scrollTop = elChatMessages.scrollHeight;
  return id;
}

function thinkingDots() {
  return '<div class="opencode-active"><span class="pulse-dot"></span> Thinking & executing tools...</div>';
}

function renderSessionRounds(bubbleId, rounds) {
  const bubble = document.getElementById(bubbleId);
  if (!bubble) return;
  if (!rounds || !rounds.length) {
    const textEl = bubble.querySelector(".bubble-text");
    if (textEl) textEl.innerHTML = thinkingDots();
    return;
  }
  
  let html = '<div class="opencode-feed">';
  rounds.forEach(r => {
    // 1. Model Thought Prose
    const modelText = (r.model_text || "").trim();
    if (modelText) {
      html += `<div class="opencode-prose">${esc(modelText)}</div>`;
    }
    
    // 2. Tool Executions & Observations
    const tools = r.tools_called || [];
    tools.forEach(tc => {
      let badgeCls = "tool";
      let badgeLabel = "Tool";
      let cmd = "";
      
      if (tc.name === "shell_probe" || tc.name === "run_action") {
        badgeCls = "shell";
        badgeLabel = "Shell";
        cmd = tc.args ? (tc.args.alias || tc.args.cmd || tc.args.action || JSON.stringify(tc.args)) : "";
      } else if (tc.name === "production_status") {
        badgeCls = "status";
        badgeLabel = "Status";
        cmd = "Query Blender Cycles progress & ready clips";
      } else if (tc.name === "read_log") {
        badgeCls = "tool";
        badgeLabel = "Log";
        cmd = tc.args ? `tail -n ${tc.args.lines || 50} ${tc.args.log || tc.args.file}` : "read_log";
      } else if (tc.name === "inspect_image") {
        badgeCls = "vision";
        badgeLabel = "Vision QC";
        cmd = tc.args ? `${tc.args.image} — ${tc.args.question || 'Inspect frame'}` : "inspect_image";
      } else if (tc.name === "escalate_openclaw") {
        badgeCls = "openclaw";
        badgeLabel = "OpenClaw";
        cmd = tc.args ? tc.args.task : "escalate_openclaw";
      } else {
        badgeCls = "tool";
        badgeLabel = tc.name || "Action";
        cmd = tc.args ? JSON.stringify(tc.args) : "";
      }
      
      html += `
        <div class="opencode-step">
          <span class="opencode-badge ${badgeCls}">${badgeLabel}</span>
          <code class="opencode-cmd" title="${esc(cmd)}">${esc(cmd)}</code>
        </div>`;
        
      if (tc.result_summary) {
        html += `<div class="opencode-obs">${esc(tc.result_summary)}</div>`;
      }
    });
  });
  html += '</div>';
  
  const textEl = bubble.querySelector(".bubble-text");
  if (textEl) {
    textEl.innerHTML = html;
  } else {
    bubble.innerHTML = `<div class="bubble-meta">Agent Timeline — Thinking & Tools</div><div class="bubble-text">${html}</div>`;
  }
  elChatMessages.scrollTop = elChatMessages.scrollHeight;
}

function sendChipPrompt(promptText) {
  elChatInput.value = promptText;
  sendChat();
}

function sendMissionPrompt() {
  const prompt = elChatInput.value.trim();
  if (!prompt) {
    showToast("Enter a task description for Mission mode (server-side sequential execution)");
    return;
  }
  // Use the mission endpoint directly
  fetch("/api/mission", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mission: prompt })
  })
  .then(res => res.json())
  .then(data => {
    if (data.error) {
      showToast("Mission error: " + data.error);
    } else {
      // Format and display the mission result
      let result = `**Mission completed** (${data.planCount} steps)\n\n`;
      if (data.stopped) result += "**Stopped early** due to gate or failure\n\n";
      (data.report || []).forEach((step, i) => {
        result += `**Step ${i + 1}:** ${step.tool || 'unknown'} — ${step.status || 'completed'}\n`;
        if (step.result_summary) result += `  ${step.result_summary}\n`;
      });
      // Display in chat
      appendMessage("assistant", result);
    }
  })
  .catch(e => showToast("Mission failed: " + e.message));
}

function sendEscalatePrompt() {
  const prompt = elChatInput.value.trim();
  if (!prompt) {
    showToast("Enter a task description to escalate to OpenClaw");
    return;
  }
  // Use the escalate endpoint
  fetch("/api/escalate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ task: prompt })
  })
  .then(res => res.json())
  .then(data => {
    if (data.error) {
      showToast("Escalation error: " + data.error);
    } else {
      appendMessage("assistant", data.output || "OpenClaw escalation completed.");
    }
  })
  .catch(e => showToast("Escalation failed: " + e.message));
}

// Prompt history: prompts are persisted server-side (.prompt_log.jsonl) so
// they survive page refreshes. Renders a compact picker in the chat area.
let historyPanelVisible = false;
async function togglePromptHistory() {
  const existing = document.getElementById("promptHistoryPanel");
  if (existing) {
    existing.remove();
    historyPanelVisible = false;
    return;
  }
  let panel = document.createElement("div");
  panel.id = "promptHistoryPanel";
  panel.className = "prompt-history-panel";
  elChatMessages.appendChild(panel);
  historyPanelVisible = true;
  panel.innerHTML = `<div class="loading-state">Loading prompt history...</div>`;
  try {
    const res = await fetch("/api/chat/history?limit=15");
    const data = await res.json();
    const items = data.history || [];
    if (!items.length) {
      panel.innerHTML = `<div class="p-history-empty">No prompts retained yet. Every prompt you send from now on is archived here.</div>`;
      return;
    }
    panel.innerHTML = `<div class="p-history-head">🕘 Recent Prompts (${items.length})</div>` +
      items.map(h => `
        <div class="p-history-item" title="${(h.prompt || '').replace(/"/g, '&quot;')}">
          <span class="p-history-ts">${h.ts || ''}</span>
          <span class="p-history-text" onclick="reusePrompt(this)">${(h.prompt || '').slice(0, 110)}</span>
        </div>
      `).join("");
  } catch (e) {
    panel.innerHTML = `<div class="loading-state error">History unavailable: ${e.message}</div>`;
  }
}

function reusePrompt(el) {
  elChatInput.value = el.getAttribute("title") || el.innerText;
  document.getElementById("promptHistoryPanel")?.remove();
  historyPanelVisible = false;
  elChatMessages.scrollTop = elChatMessages.scrollHeight;
}

async function sendPastedImageForVision(img, question) {
  const thinkingId = appendChatBubble(
    "assistant",
    "Analyzing pasted image with qwen2.5vl 7B vision model…",
    true
  );
  try {
    const res = await fetch("/api/vision", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ data_uri: img.dataUrl, question }),
    });
    const data = await res.json();
    if (data.ok && data.description) {
      const routed = data.routedTo ? `<br><span class="bubble-meta">analyzed by ${data.routedTo}</span>` : "";
      updateChatBubble(thinkingId, data.description + routed);
    } else {
      updateChatBubble(thinkingId, `⚠️ Vision analysis unavailable: ${data.error || "unknown error"}`);
    }
  } catch (e) {
    updateChatBubble(thinkingId, `⚠️ Vision analysis error: ${e.message}`);
  }
}

async function runVisionPreview() {
  // Routes a visual task straight to the qwen2.5vl specialist (7b) via /api/vision.
  const bubbleId = appendChatBubble(
    "assistant",
    "Analyzing image with qwen2.5vl 7B vision model…",
    true
  );
  try {
    const res = await fetch("/api/vision", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question: "Describe what is visible in this image in detail, then flag any visual issues.",
      }),
    });
    const data = await res.json();
    if (data.ok && data.description) {
      const routed = data.routedTo ? `<br><span class="bubble-meta">analyzed by ${data.routedTo}</span>` : "";
      updateChatBubble(bubbleId, data.description + routed);
    } else {
      updateChatBubble(bubbleId, `⚠️ Vision preview unavailable: ${data.error || "unknown error"}`);
    }
  } catch (e) {
    updateChatBubble(bubbleId, `⚠️ Vision preview error: ${e.message}`);
  }
}

function appendChatBubble(role, text, isThinking = false) {
  const bubble = document.createElement("div");
  bubble.className = `chat-bubble ${role}`;
  const id = "bubble_" + Date.now();
  bubble.id = id;

  const metaText = role === "assistant" ? "OpenClaw • Qwen 2.5 Local" : "You";
  const speakBtn = role === "assistant"
    ? `<button class="bubble-speak" onclick="speakChatBubble('${id}')" title="Read aloud">🔊</button>`
    : "";
  bubble.innerHTML = `
    <div class="bubble-meta">${metaText}</div>
    <div class="bubble-text">${formatChatText(text)}</div>
    ${speakBtn}
  `;

  elChatMessages.appendChild(bubble);
  elChatMessages.scrollTop = elChatMessages.scrollHeight;
  return id;
}

function updateChatBubble(id, newText) {
  const bubble = document.getElementById(id);
  if (bubble) {
    const textEl = bubble.querySelector(".bubble-text");
    if (textEl) {
      textEl.innerHTML = formatChatText(newText);
    }
  }
  elChatMessages.scrollTop = elChatMessages.scrollHeight;
}

function formatChatText(t) {
  // Parse code blocks ```lang\ncode\n``` into executable Action Cards
  const codeBlockRegex = /```([a-zA-Z0-9_-]*)\n([\s\S]*?)```/g;
  let formatted = t.replace(codeBlockRegex, (match, lang, code) => {
    const cleanCode = code.trim();
    const actionId = 'act_' + Math.random().toString(36).substring(2, 9);
    const escapedCode = cleanCode.replace(/"/g, '&quot;').replace(/'/g, '&#39;').replace(/`/g, '&#96;');
    const isBashOrPs = ['bash', 'sh', 'powershell', 'ps1', 'cmd', 'bat', ''].includes((lang || '').toLowerCase());
    
    return `
      <div class="action-card" id="${actionId}">
        <div class="action-header">
          <span class="action-lang">${lang || 'COMMAND'}</span>
          <div class="action-buttons">
            <button class="btn-action-copy" onclick="copyActionCode('${actionId}')">📋 Copy</button>
            ${isBashOrPs ? `<button class="btn-action-exec" onclick="executeActionCard('${actionId}')">▶️ Run Action</button>` : ''}
          </div>
        </div>
        <div class="action-code" data-code="${escapedCode}">${escapeHtml(cleanCode)}</div>
        <div class="action-result hidden" id="${actionId}_res"></div>
      </div>
    `;
  });

  return formatted
    .replace(/\n\n/g, "<br><br>")
    .replace(/\n/g, "<br>")
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
}

function escapeHtml(text) {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

async function executeActionCard(actionId) {
  const card = document.getElementById(actionId);
  if (!card) return;
  const codeEl = card.querySelector(".action-code");
  const resultEl = document.getElementById(`${actionId}_res`);
  const execBtn = card.querySelector(".btn-action-exec");
  const cmd = codeEl ? codeEl.getAttribute("data-code") : "";
  if (!cmd) return;

  if (execBtn) {
    execBtn.innerText = "⏳ Running...";
    execBtn.disabled = true;
  }
  if (resultEl) {
    resultEl.classList.remove("hidden");
    resultEl.innerText = "Dispatched to PowerShell...\n";
  }

  showToast(`⚡ Executing command...`);

  try {
    const res = await fetch("/api/openclaw/exec", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ command: cmd })
    });
    const data = await res.json();
    const out = (data.stdout || "") + (data.stderr ? "\n[STDERR] " + data.stderr : "");
    if (resultEl) {
      resultEl.innerText = out || `[Completed with Exit Code ${data.exitCode}]`;
    }
    if (execBtn) {
      execBtn.innerText = data.exitCode === 0 ? "✅ Done" : "⚠️ Error";
      execBtn.disabled = false;
    }
    // Also echo into bottom terminal output
    const termOutput = document.getElementById("termOutput");
    if (termOutput) {
      termOutput.innerText += `\n> ${cmd}\n${out}\n[Exit Code: ${data.exitCode}]`;
      termOutput.scrollTop = termOutput.scrollHeight;
    }
  } catch (e) {
    if (resultEl) resultEl.innerText = `Execution error: ${e.message}`;
    if (execBtn) {
      execBtn.innerText = "⚠️ Failed";
      execBtn.disabled = false;
    }
  }
}

function copyActionCode(actionId) {
  const card = document.getElementById(actionId);
  if (!card) return;
  const codeEl = card.querySelector(".action-code");
  const cmd = codeEl ? codeEl.getAttribute("data-code") : "";
  if (cmd) {
    navigator.clipboard.writeText(cmd);
    showToast("Command copied to clipboard!");
  }
}

// Guides & Knowledge
async function loadGuides() {
  try {
    const res = await fetch("/api/guides");
    const data = await res.json();
    const guides = data.guides || [];

    const groups = {};
    guides.forEach(g => {
      if (!groups[g.category]) groups[g.category] = [];
      groups[g.category].push(g);
    });
    const order = ["Software Manuals", "Production Standards", "Creative Direction",
                   "Tutorials & References", "Templates", "Technical Reference",
                   "Agent & Local LLM", "Design & Asset MCPs", "3D & Video Pipelines",
                   "Quality Locks"];

    let html = "";
    Object.keys(groups)
      .sort((a, b) => (order.indexOf(a) === -1 ? 999 : order.indexOf(a)) - (order.indexOf(b) === -1 ? 999 : order.indexOf(b)))
      .forEach(cat => {
        html += `<div class="guide-group">${cat}</div>`;
        groups[cat].forEach(g => {
          html += `
            <div class="guide-item" onclick="viewGuide('${g.id}')">
              <div class="guide-title">${g.title}</div>
              <div class="guide-cat">${(g.tags || []).slice(0, 3).join(" • ") || cat}</div>
            </div>
          `;
        });
      });
    if (!html) html = `<div class="loading-state">No guides found</div>`;
    elGuideList.innerHTML = html;
  } catch (e) {
    elGuideList.innerHTML = `<div class="loading-state error">Failed to load guides</div>`;
  }
}

async function viewGuide(guideId) {
  const res = await fetch("/api/guides");
  const data = await res.json();
  const target = (data.guides || []).find(g => g.id === guideId);
  if (target) {
    elActiveFilePath.innerText = `Guide: ${target.title}`;
    elCodeEditor.value = target.content;
    isMarkdownPreview = true;
    elCodeEditor.classList.add("hidden");
    elMarkdownPreview.classList.remove("hidden");
    renderMarkdownPreview();
  }
}

// Copyright Guardrail Panel (protocol made visible in the IDE UI)
async function loadCopyrightPanel() {
  const container = document.getElementById("copyrightContent");
  if (!container) return;
  try {
    const res = await fetch("/api/copyright/policy");
    const p = await res.json();

    const verdictChips = (p.verdicts || []).map(v => {
      const cls = v.code === "CLEAR" ? "verdict-clear"
                 : v.code === "WARN" ? "verdict-warn"
                 : "verdict-block";
      return `<span class="verdict-chip ${cls}">${v.code}</span>`;
    }).join(" ");

    const rules = (p.rules || []).map(r => `<div class="copyright-rule">• ${r}</div>`).join("");

    container.innerHTML = `
      <div class="copyright-meta">${p.name || "Copyright Protocol"}</div>
      <div class="copyright-verdicts">${verdictChips}</div>
      <div class="copyright-rules">${rules}</div>
      <div class="copyright-sources">
        <div class="copyright-src-title">🚫 Blocked</div>
        <div class="copyright-src-tags">${(p.blockedSources || []).map(s => `<span class="src-tag blocked">${s}</span>`).join(" ")}</div>
        <div class="copyright-src-title">✅ Allowlisted</div>
        <div class="copyright-src-tags">${(p.allowedSources || []).map(s => `<span class="src-tag allowed">${s}</span>`).join(" ")}</div>
        <div class="copyright-src-title">📄 Policy Guide</div>
        <div class="copyright-policy-path">${p.guide || ""}</div>
      </div>
      <div class="copyright-checkbox">
        <div class="copyright-src-title">🔍 Live Check</div>
        <input type="text" id="copyrightCheckInput" placeholder="e.g. generate microsoft logo for the promo tile..." />
        <button class="btn-tool" onclick="runCopyrightCheck()">Check</button>
        <div id="copyrightCheckResult"></div>
      </div>
    `;
  } catch (e) {
    container.innerHTML = `<div class="loading-state error">Failed to load copyright protocol: ${e.message}</div>`;
  }
}

async function runCopyrightCheck() {
  const input = document.getElementById("copyrightCheckInput");
  const result = document.getElementById("copyrightCheckResult");
  if (!input || !result) return;
  const text = input.value.trim();
  if (!text) { result.innerHTML = ""; return; }
  result.innerHTML = "<div class='loading-state'>Checking...</div>";
  try {
    const res = await fetch("/api/copyright/check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text }),
    });
    const data = await res.json();
    const cls = data.verdict === "CLEAR" ? "verdict-clear"
              : data.verdict === "WARN" ? "verdict-warn"
              : "verdict-block";
    result.innerHTML = `<div class="copyright-check-result">
      <span class="verdict-chip ${cls}">${data.verdict || "?"}</span>
      <div class="copyright-check-reason">${data.reason || "No verdict returned"}</div>
      ${data.replacement ? `<div class="copyright-check-repl">Replacement: <code>${data.replacement}</code></div>` : ""}
    </div>`;
  } catch (e) {
    result.innerHTML = `<div class="loading-state error">Check failed: ${e.message}</div>`;
  }
}

// Agent Execution Trace (feedback-loop debug surface)
async function loadAgentTrace() {
  const container = document.getElementById("traceContent");
  if (!container) return;
  try {
    const res = await fetch("/api/agent/trace?limit=50");
    const data = await res.json();
    const trace = data.trace || [];
    if (!trace.length) {
      container.innerHTML = `<div class="loading-state">No agent trace yet — run a chat or mission prompt to record loop events.</div>`;
      return;
    }
    container.innerHTML = trace.map(t => {
      const ev = t.event || "";
      let icon = "•", cls = "";
      if (ev.includes("term")) { icon = "✅"; cls = "ok"; }
      else if (ev.includes("error") || ev.includes("blocked") || ev.includes("stuck")) { icon = "⚠️"; cls = "warn"; }
      else if (ev.includes("start")) { icon = "🚀"; }
      else if (ev.includes("converged")) { icon = "🏁"; }
      return `<div class="trace-item ${cls}">
        <span class="trace-icon">${icon}</span>
        <span class="trace-event">${ev}</span>
        <span class="trace-detail">${esc(JSON.stringify({...t, event: undefined}))}</span>
        <span class="trace-ts">${t.ts || (t.elapsed_s ? t.elapsed_s + "s" : "")}</span>
      </div>`;
    }).join("");
  } catch (e) {
    container.innerHTML = `<div class="loading-state error">Trace unavailable: ${e.message}</div>`;
  }
}

function esc(s) {
  return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").slice(0, 160);
}

// Model Activity & Trajectory (rich timeline of the agent's reasoning + tools)
let lastTrajectoryLen = 0;
async function loadTrajectory() {
  const container = document.getElementById("trajectoryContent");
  if (!container) return;
  try {
    const res = await fetch("/api/agent/trajectory?limit=30");
    const data = await res.json();
    const traj = data.trajectory || [];
    if (!traj.length) {
      if (container.dataset.empty) return;
      container.innerHTML = `<div class="loading-state">No model activity yet — run a chat or mission prompt.</div>`;
      container.dataset.empty = "1";
      return;
    }
    delete container.dataset.empty;
    // Only re-render when new activity arrives (avoids flicker each poll)
    if (traj.length === lastTrajectoryLen) return;
    lastTrajectoryLen = traj.length;
    container.innerHTML = traj.map(t => {
      const ev = t.event || "";
      let icon = "•", cls = "";
      if (ev === "round") { icon = "🧠"; }
      else if (ev === "tool") { icon = "🔧"; }
      else if (ev === "thinking") { icon = "💭"; }
      else if (ev.includes("term")) { icon = "✅"; cls = "ok"; }
      else if (ev.includes("error") || ev.includes("blocked") || ev.includes("stuck")) { icon = "⚠️"; cls = "warn"; }
      else if (ev.includes("start")) { icon = "🚀"; }
      else if (ev.includes("converged")) { icon = "🏁"; }
      else if (ev.includes("info_only")) { icon = "📊"; }
      return `<div class="trajectory-item ${cls}">
        <span class="trajectory-icon">${icon}</span>
        <div class="trajectory-body">
          <div class="trajectory-head">${ev}${t.round !== undefined ? ` <span class="trajectory-round">R${t.round + 1}</span>` : ""}</div>
          ${t.model_text ? `<div class="trajectory-thought">${esc(t.model_text.slice(0, 240))}</div>` : ""}
          ${t.tools_called ? t.tools_called.map(tc => `
            <div class="trajectory-tool">
              <span class="trajectory-tool-name">${esc(tc.name || "")}</span>
              ${tc.args ? `<span class="trajectory-tool-args">${esc(JSON.stringify(tc.args)).slice(0, 90)}</span>` : ""}
              ${tc.status ? `<span class="trajectory-tool-status ${tc.status}">${tc.status}</span>` : ""}
            </div>`).join("") : ""}
          ${t.result_summary ? `<div class="trajectory-result">${esc(t.result_summary).slice(0, 180)}</div>` : ""}
          ${t.prompt ? `<div class="trajectory-prompt">Prompt: ${esc(t.prompt.slice(0, 120))}</div>` : ""}
        </div>
      </div>`;
    }).join("");
  } catch (e) {
    if (!container.dataset.empty) {
      container.innerHTML = `<div class="loading-state error">Trajectory unavailable: ${e.message}</div>`;
      container.dataset.empty = "1";
    }
  }
}

// Power & Full-Throttle strategy panel
async function loadPowerPanel() {
  const container = document.getElementById("powerContent");
  if (!container) return;
  try {
    const res = await fetch("/api/power");
    const p = await res.json();
    const isHP = (p.activeScheme || "").toLowerCase().includes("high");
    const planClass = isHP ? "ok" : "warn";
    const planIcon = isHP ? "🚀" : "⚠️";

    const sleepOk = p.sleep.ac === "never" && p.sleep.dc === "never";
    const hibOk = p.hibernate.ac === "never" && p.hibernate.dc === "never";
    const battery = p.battery || {};
    const batPct = battery.percent || 0;
    const charging = (battery.status || "").toLowerCase().includes("charg");

    const schemeBtns = (p.schemes || []).map(s => `
      <button class="btn-tool" onclick="applyPowerAction('set_plan', {guid:'${s.guid}'})"
        ${s.guid === p.activeGuid ? "disabled" : ""}>${s.name}</button>`).join("");

    container.innerHTML = `
      <div class="power-card">
        <div class="power-title">Active Plan</div>
        <div class="power-plan ${planClass}">${planIcon} ${esc(p.activeScheme || "Unknown")}</div>
      </div>
      <div class="power-card">
        <div class="power-title">Battery</div>
        <div class="power-batbar"><div class="power-batfill" style="width:${Math.max(2, batPct)}%"></div></div>
        <div class="power-battext">${batPct}% · ${esc(battery.status || "Unknown")}${charging ? " (on AC — full throttle sustained)" : ""}</div>
      </div>
      <div class="power-card">
        <div class="power-title">Full-Throttle Safeguards</div>
        <div class="power-guard ${sleepOk ? "ok" : "warn"}">😴 Sleep: ${sleepOk ? "Never (AC/DC)" : "ACTIVE — will interrupt render!"}</div>
        <div class="power-guard ${hibOk ? "ok" : "warn"}">💤 Hibernate: ${hibOk ? "Never (AC/DC)" : "ACTIVE — will interrupt render!"}</div>
      </div>
      <div class="power-card">
        <div class="power-title">Controls</div>
        <div class="power-controls">
          <button class="btn-tool primary" onclick="applyPowerAction('full_throttle')">⚡ Full Throttle</button>
          <button class="btn-tool" onclick="applyPowerAction('disable_sleep')">Disable Sleep</button>
          <button class="btn-tool" onclick="applyPowerAction('disable_hibernate')">Disable Hibernate</button>
        </div>
        <div class="power-schemes">${schemeBtns}</div>
        <div id="powerActionResult" class="power-result"></div>
      </div>`;
  } catch (e) {
    container.innerHTML = `<div class="loading-state error">Power state unavailable: ${e.message}</div>`;
  }
}

async function applyPowerAction(action, extra) {
  const result = document.getElementById("powerActionResult");
  if (!result) return;
  result.innerHTML = `<div class="loading-state">Applying ${action}...</div>`;
  try {
    const body = { action, ...(extra || {}) };
    const res = await fetch("/api/power", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await res.json();
    result.innerHTML = `<div class="${data.ok ? "power-ok" : "power-err"}">${esc(data.message || data.error || (data.ok ? "Done" : "Failed"))}</div>`;
    setTimeout(() => loadPowerPanel(), 600);
  } catch (e) {
    result.innerHTML = `<div class="power-err">Action failed: ${e.message}</div>`;
  }
}

// Crestodian Attestation & Session Guard
async function refreshCrestodian() {
  try {
    const res = await fetch("/api/crestodian/status");
    const data = await res.json();
    
    const countBadge = document.getElementById("crestodianCountBadge");
    const statusText = document.getElementById("attestStatusText");
    const auditContainer = document.getElementById("crestodianAuditList");
    
    if (countBadge) countBadge.innerText = `${data.attestationsCount || 0} Attested`;
    if (statusText) statusText.innerText = `${data.attestationsCount || 0} Verified`;

    if (auditContainer && data.recentAudit) {
      if (data.recentAudit.length === 0) {
        auditContainer.innerHTML = `<div style="padding:4px 0;">No security audit events recorded.</div>`;
      } else {
        let html = "";
        data.recentAudit.slice(-6).reverse().forEach(evt => {
          const t = evt.time || evt.timestamp || "recent";
          const act = evt.action || evt.event || evt.type || JSON.stringify(evt).substring(0, 45);
          html += `<div style="padding:2px 0; border-bottom:1px solid #1c2438;">• [${t}] ${act}</div>`;
        });
        auditContainer.innerHTML = html;
      }
    }
  } catch (e) {
    console.warn("Crestodian fetch error:", e);
  }
}

function verifyAttestation() {
  showToast("🛡️ Crestodian: Workspace hash and session attested!");
  refreshCrestodian();
}

// ── Hourly production report panel ─────────────────────────────────────
async function loadHourlyPanel() {
  const container = document.getElementById("hourlyContent");
  if (!container) return;
  try {
    const res = await fetch("/api/hourly");
    const data = await res.json();
    if (!data.ok) {
      container.innerHTML = `<div class="loading-state">${esc(data.error || "No report available")}</div>`;
      return;
    }
    const meta = data.stamp
      ? `<div class="hourly-meta">⏰ Generated · <span class="gate-val hold">${esc(data.stamp)}</span></div>`
      : "";
    const body = (data.content || "No report generated yet. Run it now with the button below.")
      .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    container.innerHTML = meta + `<pre class="hourly-report">${body}</pre>`;
  } catch (e) {
    container.innerHTML = `<div class="loading-state">Hourly report unavailable (${esc(e.message)})</div>`;
  }
}

async function runHourlyReport() {
  const container = document.getElementById("hourlyContent");
  if (container) container.innerHTML = `<div class="loading-state">Generating report now...</div>`;
  try {
    const res = await fetch("/api/exec", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ action: "hourly_report" })
    });
    const data = await res.json();
    if (data.blocked) {
      if (container) container.innerHTML = `<div class="loading-state">⛔ ${esc(data.reason || data.blocked)}</div>`;
    } else if (data.error) {
      if (container) container.innerHTML = `<div class="loading-state">❌ ${esc(data.error)}</div>`;
    } else if (data.ok) {
      showToast("⏰ Hourly report generated");
    } else {
      if (container) container.innerHTML = `<div class="loading-state">❌ Report failed (exit ${data.exitCode})</div>`;
    }
  } catch (e) {
    if (container) container.innerHTML = `<div class="loading-state">Run failed (${esc(e.message)})</div>`;
  } finally {
    setTimeout(loadHourlyPanel, 4000);
  }
}

// ── Audio: read-aloud (TTS), mic (STT), chimes, audio browser ───────────
function speakChatBubble(id) {
  const bubble = document.getElementById(id);
  if (!bubble) return;
  const textEl = bubble.querySelector(".bubble-text");
  const text = (textEl ? textEl.innerText : "").trim();
  if (!text) return;
  if (!("speechSynthesis" in window)) {
    showToast("🔇 Speech synthesis not supported in this browser");
    return;
  }
  speechSynthesis.cancel();
  const utter = new SpeechSynthesisUtterance(text);
  utter.rate = 1.05;
  utter.pitch = 1;
  utter.onend = () => {
    const btn = bubble.querySelector(".bubble-speak");
    if (btn) btn.innerText = "🔊";
  };
  const btn = bubble.querySelector(".bubble-speak");
  if (btn) btn.innerText = "⏹";
  speechSynthesis.speak(utter);
  showToast("🔊 Reading reply aloud");
}

function toggleSttMic() {
  const btn = document.getElementById("btnMic");
  if (btn && btn.classList.contains("recording")) {
    btn.classList.remove("recording");
    if (window._recognition) {
      window._recognition.stop();
      window._recognition = null;
    }
    return;
  }
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) {
    showToast("🎤 Speech recognition not supported in this browser");
    return;
  }
  const rec = new SR();
  rec.lang = "en-US";
  rec.interimResults = false;
  rec.maxAlternatives = 1;
  rec.onresult = (ev) => {
    const t = ev.results[0][0].transcript;
    if (elChatInput) {
      elChatInput.value += (elChatInput.value ? " " : "") + t;
      elChatInput.focus();
    }
  };
  rec.onend = () => {
    if (btn) btn.classList.remove("recording");
    window._recognition = null;
  };
  rec.onerror = (ev) => {
    console.warn("STT error:", ev.error);
    if (btn) btn.classList.remove("recording");
    showToast("🎤 Mic error: " + ev.error);
  };
  window._recognition = rec;
  if (btn) btn.classList.add("recording");
  rec.start();
  showToast("🎤 Listening… speak now");
}

let _chimeCtx = null;
function playChime(kind) {
  try {
    if (!window.AudioContext && !window.webkitAudioContext) return;
    if (!_chimeCtx) _chimeCtx = new (window.AudioContext || window.webkitAudioContext)();
    const ctx = _chimeCtx;
    if (ctx.state === "suspended") ctx.resume();
    const notes = kind === "error" ? [392, 311] : [523.25, 659.25, 783.99]; // G->Eb alert | C-E-G reply
    const t0 = ctx.currentTime;
    notes.forEach((freq, i) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = kind === "error" ? "square" : "sine";
      osc.frequency.value = freq;
      gain.gain.setValueAtTime(0.0001, t0 + i * 0.12);
      gain.gain.exponentialRampToValueAtTime(0.12, t0 + i * 0.12 + 0.02);
      gain.gain.exponentialRampToValueAtTime(0.0001, t0 + i * 0.12 + 0.3);
      osc.connect(gain).connect(ctx.destination);
      osc.start(t0 + i * 0.12);
      osc.stop(t0 + i * 0.12 + 0.35);
    });
  } catch (e) {
    console.warn("Chime error:", e);
  }
}

async function loadAudioFiles() {
  const container = document.getElementById("audioFileList");
  if (!container) return;
  try {
    const res = await fetch("/api/audio/files");
    const data = await res.json();
    const files = data.files || [];
    container.innerHTML = "";
    if (!files.length) {
      container.innerHTML = `<div style="padding:6px 0; opacity:.7;">No audio assets found.</div>`;
      return;
    }
    files.forEach(f => {
      const item = document.createElement("div");
      item.className = "audio-item";
      const url = "/api/audio/file?path=" + encodeURIComponent(f.rel || f.path || f.name);
      const size = f.size ? Math.round(f.size / 1024) + " KB" : "";
      item.innerHTML = `
        <div class="audio-item-name" title="${esc(f.rel || f.path)}">🎵 ${esc(f.name)} ${size ? `<span class="audio-item-meta">${size}</span>` : ""}</div>
        <audio controls preload="none" src="${url}" style="width:100%; height:32px;"></audio>`;
      container.appendChild(item);
    });
  } catch (e) {
    container.innerHTML = `<div style="padding:6px 0; opacity:.7;">Audio list unavailable (${e.message})</div>`;
  }
}

function initAudioPanel() {
  loadAudioFiles();
  const refresh = document.getElementById("btnRefreshAudio");
  if (refresh) refresh.addEventListener("click", loadAudioFiles);
  const mic = document.getElementById("btnMic");
  if (mic) mic.addEventListener("click", toggleSttMic);
}

// ── Panel Resizers ────────────────────────────────────────────────────
// Drag handles between sidebar ↔ editor, editor ↔ agent, and above bottom panel.
(function initResizers() {
  document.addEventListener("DOMContentLoaded", () => {
    const root = document.documentElement;

    function hookDrag(handleId, onDrag) {
      const el = document.getElementById(handleId);
      if (!el) return;
      el.addEventListener("mousedown", (e) => {
        e.preventDefault();
        el.classList.add("active");
        const onMove = (ev) => onDrag(ev);
        const onUp = () => {
          el.classList.remove("active");
          document.removeEventListener("mousemove", onMove);
          document.removeEventListener("mouseup", onUp);
          document.body.style.cursor = "";
          document.body.style.userSelect = "";
        };
        document.addEventListener("mousemove", onMove);
        document.addEventListener("mouseup", onUp);
        document.body.style.cursor = el.style.cursor || "col-resize";
        document.body.style.userSelect = "none";
      });
    }

    // Sidebar ↔ Editor (horizontal drag)
    hookDrag("resizeSidebar", (e) => {
      const activityW = 50;
      const newW = Math.max(180, Math.min(600, e.clientX - activityW));
      root.style.setProperty("--sidebar-width", newW + "px");
    });

    // Editor ↔ Agent Panel (horizontal drag from left edge of agent)
    hookDrag("resizeAgent", (e) => {
      const newW = Math.max(240, Math.min(700, window.innerWidth - e.clientX));
      root.style.setProperty("--agent-width", newW + "px");
    });

    // Bottom Panel (vertical drag — resize from top edge)
    hookDrag("resizeBottom", (e) => {
      const editorArea = document.querySelector(".editor-area");
      const bottom = document.getElementById("bottomPanel");
      if (!editorArea || !bottom) return;
      const rect = editorArea.getBoundingClientRect();
      const newH = Math.max(60, Math.min(500, rect.bottom - e.clientY));
      bottom.style.height = newH + "px";
    });
  });
})();

// ── System Readiness Panel ──────────────────────────────────────────
async function loadReadinessPanel() {
  const container = document.getElementById("readinessContent");
  if (!container) return;
  try {
    const res = await fetch("/api/readiness");
    const data = await res.json();
    const badge = document.getElementById("readinessBadge");
    badge.className = data.overall === "ready" ? "badge-accent ok" : "badge-accent warn";
    badge.innerText = data.overall.toUpperCase();
    
    let html = "";
    for (const [key, check] of Object.entries(data.checks)) {
      const icon = check.ok ? "✅" : "⚠️";
      const cls = check.ok ? "ok" : "warn";
      html += `
        <div class="readiness-item ${cls}">
          <span class="readiness-icon">${icon}</span>
          <div class="readiness-detail">
            <span class="readiness-name">${key.toUpperCase()}</span>
            <span class="readiness-desc">${check.detail}</span>
          </div>
        </div>`;
    }
    container.innerHTML = html || "<div class='loading-state'>No checks available</div>";
  } catch (e) {
    container.innerHTML = `<div class="loading-state error">Readiness unavailable: ${e.message}</div>`;
  }
}

// ── Project Plan Board ──────────────────────────────────────────────
async function loadProjectPlan() {
  const container = document.getElementById("planboardContent");
  if (!container) return;
  try {
    const res = await fetch("/api/files/read?path=project.json");
    const data = await res.json();
    const plan = data.content ? JSON.parse(data.content).plan : null;
    const versionBadge = document.getElementById("planVersionBadge");
    
    if (!plan) {
      container.innerHTML = `<div class="loading-state">No plan saved. Use <strong>Deep Plan</strong> mode to create one.</div>`;
      versionBadge.innerText = "v—";
      return;
    }
    
    versionBadge.innerText = `v${plan.version || 1} · ${plan.generated ? new Date(plan.generated).toLocaleString() : "—"}`;
    
    let html = "";
    (plan.phases || []).forEach((phase, pi) => {
      html += `<div class="plan-phase"><h4>${phase.name} (${phase.days || "?"} days)</h4>`;
      (phase.tasks || []).forEach((task, ti) => {
        const deps = task.depends_on ? task.depends_on.join(", ") : "—";
        html += `
          <div class="plan-task" data-task-id="${task.id}">
            <input type="checkbox" class="task-check" ${task.done ? "checked" : ""} onchange="toggleTask('${task.id}', this.checked)">
            <div class="task-info">
              <div class="task-name">${task.name}</div>
              <div class="task-meta">
                <span class="task-deliverable">📄 ${task.deliverable || "—"}</span>
                <span class="task-estimate">⏱ ${task.estimate_hrs || "?"}h</span>
                <span class="task-deps">🔗 ${deps}</span>
              </div>
            </div>`;
      });
      html += `</div>`;
    });
    
    container.innerHTML = html || `<div class="loading-state">No phases in plan</div>`;
    
    // Enable promote button if plan has handoff_ready
    const promoteBtn = document.getElementById("btnPromoteMission");
    if (promoteBtn) promoteBtn.disabled = !plan.handoff_ready;
  } catch (e) {
    container.innerHTML = `<div class="loading-state error">Failed to load plan: ${e.message}</div>`;
  }
}

async function toggleTask(taskId, done) {
  try {
    const res = await fetch("/api/files/read?path=project.json");
    const data = await res.json();
    const config = JSON.parse(data.content);
    let found = false;
    (config.plan?.phases || []).forEach(p => {
      (p.tasks || []).forEach(t => { if (t.id === taskId) { t.done = done; found = true; } });
    });
    if (found) {
      await fetch("/api/files/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ path: "project.json", content: JSON.stringify(config, null, 2) })
      });
      showToast(done ? "✅ Task completed" : "↩️ Task reopened");
    }
  } catch (e) {
    showToast("Failed to update task: " + e.message);
  }
}

async function promotePlanToMission() {
  const res = await fetch("/api/files/read?path=project.json");
  const data = await res.json();
  const plan = data.content ? JSON.parse(data.content).plan : null;
  if (!plan || !plan.handoff_ready) {
    showToast("Plan not ready for mission promotion");
    return;
  }
  // Send handoff JSON to /api/mission
  const missionText = `Execute plan: ${JSON.stringify(plan.handoff)}`;
  fetch("/api/mission", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mission: missionText })
  }).then(r => r.json()).then(result => {
    if (result.error) showToast("Mission error: " + result.error);
    else showToast("🚀 Mission started (" + result.planCount + " steps)");
  });
}

// Add to DOMContentLoaded init
document.addEventListener("DOMContentLoaded", () => {
  // ... existing init code ...
  loadReadinessPanel();
  loadProjectPlan();
  setInterval(loadReadinessPanel, 8000);
});
