// =============================
// Utility: Smooth scroll on custom buttons
// =============================

document.querySelectorAll("[data-scroll]").forEach((btn) => {
  btn.addEventListener("click", (e) => {
    const target = btn.getAttribute("data-scroll");
    const el = document.querySelector(target);
    if (!el) return;
    e.preventDefault();
    el.scrollIntoView({ behavior: "smooth", block: "start" });
  });
});

// =============================
// Animated background particles
// Simple lightweight particle field for cyber vibe
// =============================

(function initParticles() {
  const canvas = document.getElementById("bg-particles");
  if (!canvas) return;

  const ctx = canvas.getContext("2d");
  const particles = [];
  const maxParticles = 56;

  function resize() {
    canvas.width = window.innerWidth * 2;
    canvas.height = window.innerHeight * 2;
  }

  window.addEventListener("resize", resize);
  resize();

  // Create particles with random positions and velocities
  for (let i = 0; i < maxParticles; i++) {
    particles.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      r: 0.8 + Math.random() * 1.4,
      vx: -0.05 + Math.random() * 0.1,
      vy: -0.05 + Math.random() * 0.1,
      alpha: 0.15 + Math.random() * 0.45,
    });
  }

  function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Connect some particles for subtle network effect
    for (let i = 0; i < particles.length; i++) {
      const p = particles[i];

      // Move
      p.x += p.vx;
      p.y += p.vy;

      // Wrap around edges
      if (p.x < 0) p.x = canvas.width;
      if (p.x > canvas.width) p.x = 0;
      if (p.y < 0) p.y = canvas.height;
      if (p.y > canvas.height) p.y = 0;

      // Draw node
      const grd = ctx.createRadialGradient(
        p.x,
        p.y,
        0,
        p.x,
        p.y,
        p.r * 6
      );
      grd.addColorStop(0, `rgba(96, 165, 250, ${p.alpha})`);
      grd.addColorStop(1, "transparent");
      ctx.fillStyle = grd;
      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r * 4, 0, Math.PI * 2);
      ctx.fill();
    }

    requestAnimationFrame(draw);
  }

  draw();
})();

// =============================
// Watermark section logic
// Front-end only simulation: store "watermark" metadata in memory
// =============================

const wmDropzone = document.getElementById("wm-dropzone");
const wmInput = document.getElementById("wm-input");
const wmOwnerInput = document.getElementById("wm-owner-id");
const wmStrengthInput = document.getElementById("wm-strength");
const wmStrengthLabel = document.getElementById("wm-strength-label");
const wmApplyBtn = document.getElementById("wm-apply-btn");
const wmPreviewPlaceholder = document.getElementById("wm-preview-placeholder");
const wmPreviewOriginal = document.getElementById("wm-preview-original");
const wmPreviewWatermarked = document.getElementById("wm-preview-watermarked");

// Internal "database" of watermarked images (keyed by fake hash)
const watermarkStore = new Map();

// Utility that builds a lightweight "hash" based on file name + size
async function hashFile(file) {
  // WARNING: This is NOT cryptographically secure; used only as demo stub.
  const arrayBuffer = await file.arrayBuffer();
  const view = new Uint8Array(arrayBuffer);
  let hash = 0;
  for (let i = 0; i < view.length; i += Math.ceil(view.length / 512)) {
    hash = (hash * 31 + view[i]) >>> 0;
  }
  return `${file.name}-${file.size}-${hash}`;
}

// Utility to show selected image
function loadImagePreview(file, imgEl) {
  const reader = new FileReader();
  reader.onload = (e) => {
    imgEl.src = e.target.result;
    imgEl.classList.add("visible");
  };
  reader.readAsDataURL(file);
}

// Update strength label meaningfully
function updateStrengthLabel(value) {
  const val = Number(value);
  let label = "Low";
  if (val > 80) label = "Very high";
  else if (val > 60) label = "High";
  else if (val > 40) label = "Medium";
  else if (val > 20) label = "Soft";
  wmStrengthLabel.textContent = label;
}

updateStrengthLabel(wmStrengthInput.value);
wmStrengthInput.addEventListener("input", (e) =>
  updateStrengthLabel(e.target.value)
);

// Drag & drop wiring for watermark upload
function setupDropzone(dropzoneEl, inputEl, onFileSelected) {
  dropzoneEl.addEventListener("click", () => inputEl.click());

  dropzoneEl.addEventListener("dragenter", (e) => {
    e.preventDefault();
    e.stopPropagation();
    dropzoneEl.classList.add("drag-over");
  });
  dropzoneEl.addEventListener("dragover", (e) => {
    e.preventDefault();
    e.stopPropagation();
    dropzoneEl.classList.add("drag-over");
  });
  dropzoneEl.addEventListener("dragleave", (e) => {
    e.preventDefault();
    e.stopPropagation();
    dropzoneEl.classList.remove("drag-over");
  });
  dropzoneEl.addEventListener("drop", (e) => {
    e.preventDefault();
    dropzoneEl.classList.remove("drag-over");
    const file = e.dataTransfer.files?.[0];
    if (file && file.type.startsWith("image/")) {
      onFileSelected(file);
    }
  });

  inputEl.addEventListener("change", () => {
    const file = inputEl.files?.[0];
    if (file && file.type.startsWith("image/")) {
      onFileSelected(file);
    }
  });
}

let currentWMFile = null;

// When user selects an image, show it as "original" and clear watermarked preview
setupDropzone(wmDropzone, wmInput, (file) => {
  currentWMFile = file;
  wmPreviewPlaceholder.style.display = "none";
  loadImagePreview(file, wmPreviewOriginal);
  wmPreviewWatermarked.src = "";
  wmPreviewWatermarked.classList.remove("visible");
});

// Preview toggle (Original vs Watermarked) micro-interaction
const previewToggleButtons = document.querySelectorAll(
  "[data-preview-mode]"
);

previewToggleButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    previewToggleButtons.forEach((b) => b.classList.remove("chip-active"));
    btn.classList.add("chip-active");

    const mode = btn.getAttribute("data-preview-mode");
    if (mode === "original") {
      wmPreviewOriginal.style.display = "block";
      wmPreviewWatermarked.style.display = "none";
    } else {
      wmPreviewOriginal.style.display = "none";
      wmPreviewWatermarked.style.display = "block";
    }
  });
});

// Apply invisible watermark simulation
wmApplyBtn.addEventListener("click", async () => {
  if (!currentWMFile) {
    wmDropzone.classList.add("drag-over");
    setTimeout(() => wmDropzone.classList.remove("drag-over"), 600);
    return;
  }

  const ownerId = wmOwnerInput.value.trim();
  if (!ownerId) {
    wmOwnerInput.focus();
    wmOwnerInput.classList.add("shake");
    setTimeout(() => wmOwnerInput.classList.remove("shake"), 400);
    return;
  }

  // Start fake loading state
  wmApplyBtn.classList.add("loading");
  wmApplyBtn.disabled = true;

  // Simulate network / processing delay
  await new Promise((res) => setTimeout(res, 1200 + Math.random() * 800));

  const hash = await hashFile(currentWMFile);
  const strength = Number(wmStrengthInput.value);

  // Store "watermark" in memory
  watermarkStore.set(hash, {
    ownerId,
    strength,
    timestamp: Date.now(),
  });

  // For demo we just reuse the original image; in real system watermarked binary differs
  loadImagePreview(currentWMFile, wmPreviewWatermarked);

  // Activate watermarked view
  previewToggleButtons.forEach((b) => {
    const mode = b.getAttribute("data-preview-mode");
    b.classList.toggle("chip-active", mode === "watermarked");
  });
  wmPreviewOriginal.style.display = "none";
  wmPreviewWatermarked.style.display = "block";

  // End loading
  wmApplyBtn.classList.remove("loading");
  wmApplyBtn.disabled = false;

  // Small affordance: briefly highlight the watermarked preview
  wmPreviewWatermarked.style.transform = "scale(1.02)";
  wmPreviewWatermarked.style.opacity = "0.85";
  setTimeout(() => {
    wmPreviewWatermarked.style.transform = "";
    wmPreviewWatermarked.style.opacity = "1";
  }, 320);
});

// =============================
// Verify section logic
// =============================

const vfDropzone = document.getElementById("vf-dropzone");
const vfInput = document.getElementById("vf-input");
const vfBtn = document.getElementById("vf-btn");
const vfStatus = document.getElementById("vf-status");
const vfDetected = document.getElementById("vf-detected");
const vfOwner = document.getElementById("vf-owner");
const vfConfidence = document.getElementById("vf-confidence");
const vfBars = document.getElementById("vf-bars");

let currentVfFile = null;

// Setup drag & drop for verification upload
setupDropzone(vfDropzone, vfInput, (file) => {
  currentVfFile = file;
  vfStatus.textContent = "Ready to verify";
  vfStatus.className = "status-pill status-idle";
});

// Verify action simulation
vfBtn.addEventListener("click", async () => {
  if (!currentVfFile) {
    vfDropzone.classList.add("drag-over");
    setTimeout(() => vfDropzone.classList.remove("drag-over"), 600);
    return;
  }

  vfBtn.classList.add("loading");
  vfBtn.disabled = true;

  vfStatus.textContent = "Scanning for invisible watermark…";
  vfStatus.className = "status-pill status-idle";

  // Keep bars animating as if "processing"
  vfBars.style.opacity = "1";

  await new Promise((res) => setTimeout(res, 1100 + Math.random() * 900));

  const hash = await hashFile(currentVfFile);
  const record = watermarkStore.get(hash);

  // Fake confidence generator:
  //   If found: 85–99%
  //   If not: 8–35%
  let confidence;
  if (record) {
    confidence = 85 + Math.round(Math.random() * 14);
  } else {
    confidence = 8 + Math.round(Math.random() * 27);
  }

  if (record) {
    vfStatus.textContent = "Watermark verified";
    vfStatus.className = "status-pill status-success";
    vfDetected.textContent = "Yes";
    vfOwner.textContent = record.ownerId;
    vfConfidence.textContent = `${confidence}%`;
  } else {
    vfStatus.textContent = "No known watermark found";
    vfStatus.className = "status-pill status-error";
    vfDetected.textContent = "No";
    vfOwner.textContent = "Unknown";
    vfConfidence.textContent = `${confidence}%`;
  }

  // Brief accent animation on bars to emphasize result
  vfBars.classList.add("flash");
  setTimeout(() => vfBars.classList.remove("flash"), 400);

  vfBtn.classList.remove("loading");
  vfBtn.disabled = false;
});

// Optional: small shake animation via class toggled above
const style = document.createElement("style");
style.textContent = `
  .shake {
    animation: shake 0.3s ease-in-out;
  }
  @keyframes shake {
    0%, 100% { transform: translateX(0); }
    25% { transform: translateX(-3px); }
    50% { transform: translateX(3px); }
    75% { transform: translateX(-2px); }
  }
  .flash span {
    animation-duration: 0.45s !important;
  }
`;
document.head.appendChild(style);
