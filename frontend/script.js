// =============================
// Global API_BASE for all scripts
// =============================

console.log('🚀 script.js loaded');

const API_BASE = 'http://127.0.0.1:8000';

// =============================
// Theme Toggle Functionality
// =============================

let themeInitialized = false;

function initThemeToggle() {
  if (themeInitialized) {
    console.log('Theme already initialized, skipping...');
    return;
  }

  const btn = document.getElementById('theme-toggle-btn');

  if (!btn) {
    console.error('❌ Theme button not found');
    return;
  }

  console.log('✅ Theme button found, initializing...');
  themeInitialized = true;

  // Restore saved preference
  const saved = localStorage.getItem('theme-mode') || 'dark-mode';
  console.log('📦 Saved theme:', saved);

  if (saved === 'light-mode') {
    document.body.classList.add('light-mode');
    btn.textContent = '☀️';
  } else {
    document.body.classList.remove('light-mode');
    btn.textContent = '🌙';
  }

  // Add click handler
  btn.onclick = function (e) {
    e.preventDefault();
    console.log('🖱️ Button clicked!');

    const isLight = document.body.classList.contains('light-mode');
    console.log('Current theme is light:', isLight);

    if (isLight) {
      document.body.classList.remove('light-mode');
      document.documentElement.classList.remove('light-mode');
      document.documentElement.style.backgroundColor = '#050712';
      document.documentElement.style.background = '#050712';
      document.body.style.backgroundColor = '#050712';
      document.body.style.background = '#050712';
      btn.textContent = '🌙';
      localStorage.setItem('theme-mode', 'dark-mode');
      console.log('🌙 -> Dark mode');
    } else {
      document.body.classList.add('light-mode');
      document.documentElement.classList.add('light-mode');
      document.documentElement.style.backgroundColor = '#f8fafc';
      document.documentElement.style.background = '#f8fafc';
      document.body.style.backgroundColor = '#f8fafc';
      document.body.style.background = '#f8fafc';
      btn.textContent = '☀️';
      localStorage.setItem('theme-mode', 'light-mode');
      console.log('☀️ -> Light mode');
    }
  };
}

// Wait for DOM then initialize
if (document.readyState === 'loading') {
  console.log('📄 DOM still loading...');
  document.addEventListener('DOMContentLoaded', initThemeToggle);
} else {
  console.log('📄 DOM already loaded');
  initThemeToggle();
}

// =============================
// Page Navigation
// =============================
// Navigation enabled without page transition animations

// Simple notification system for the main page
function showNotification(message, type = 'info') {
  const notification = document.createElement('div');
  notification.className = `main-notification ${type}`;
  notification.textContent = message;
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 1rem 1.5rem;
    border-radius: 8px;
    color: white;
    font-weight: 500;
    z-index: 10000;
    animation: slideInRight 0.3s ease;
    background: ${type === 'success' ? '#22c55e' : type === 'error' ? '#ef4444' : '#3b82f6'};
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  `;

  document.body.appendChild(notification);

  setTimeout(() => {
    notification.style.animation = 'slideOutRight 0.3s ease';
    setTimeout(() => notification.remove(), 300);
  }, 3000);
}

// Add notification animations
const notificationStyle = document.createElement('style');
notificationStyle.textContent = `
  @keyframes slideInRight {
    from { transform: translateX(100%); opacity: 0; }
    to { transform: translateX(0); opacity: 1; }
  }
  
  @keyframes slideOutRight {
    from { transform: translateX(0); opacity: 1; }
    to { transform: translateX(100%); opacity: 0; }
  }
`;
document.head.appendChild(notificationStyle);

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

      // Use different colors based on theme
      const isLightMode = document.body.classList.contains('light-mode');
      const particleColor = isLightMode
        ? `rgba(37, 99, 235, ${p.alpha})` // Light blue for light mode
        : `rgba(96, 165, 250, ${p.alpha})`; // Lighter blue for dark mode

      grd.addColorStop(0, particleColor);
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

// Global drag & drop setup function
function setupDropzone(dropzoneEl, inputEl, onFileSelected) {
  if (!dropzoneEl || !inputEl) {
    console.log('Dropzone elements not found, skipping setup');
    return;
  }

  dropzoneEl.addEventListener("click", (e) => {
    // Prevent infinite loop if the input is inside the dropzone
    if (e.target === inputEl) return;

    // e.preventDefault(); 
    e.stopPropagation();
    console.log("Dropzone clicked, opening file picker");
    inputEl.click();
  });

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
    if (file) {
      if (file.type.startsWith("image/")) {
        onFileSelected(file);
      } else {
        alert("Please select a valid image file (PNG, JPEG).");
      }
    }
  });

  inputEl.addEventListener("change", () => {
    console.log("File input change event triggered");
    const file = inputEl.files?.[0];
    if (file) {
      if (file.type.startsWith("image/")) {
        console.log("Valid image file, calling onFileSelected");
        onFileSelected(file);
        inputEl.value = ''; // Reset
      } else {
        console.log("Invalid file or not an image");
        alert("Please select a valid image file (PNG, JPEG).");
        inputEl.value = '';
      }
    }
  });
}

// =============================
// Watermark Utility Functions
// =============================

// Internal "database" of watermarked images (keyed by fake hash)
const STORAGE_KEY = "pngprotect.watermarkStore.v1";

function loadStoreFromStorage() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return new Map();
    const arr = JSON.parse(raw);
    return new Map(Array.isArray(arr) ? arr : []);
  } catch (e) {
    console.warn("Failed to load watermark store:", e);
    return new Map();
  }
}

function saveStoreToStorage(map) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(Array.from(map.entries())));
  } catch (e) {
    console.warn("Failed to save watermark store:", e);
  }
}

const watermarkStore = loadStoreFromStorage();

// Utility that builds a lightweight "hash" based on file name + size
async function hashFile(file) {
  // Content-only hash: use SHA-256 of the file bytes so downloaded
  // copies will produce the same key when re-uploaded.
  const arrayBuffer = await file.arrayBuffer();
  try {
    if (window.crypto && crypto.subtle && crypto.subtle.digest) {
      const digest = await crypto.subtle.digest("SHA-256", arrayBuffer);
      const hex = Array.from(new Uint8Array(digest))
        .map((b) => b.toString(16).padStart(2, "0"))
        .join("");
      return hex;
    }
  } catch (e) {
    console.warn("SubtleCrypto digest failed, falling back to sample-hash", e);
  }

  // Fallback: deterministic sample-based hash derived from bytes only
  const view = new Uint8Array(arrayBuffer);
  let h = 0;
  for (let i = 0; i < view.length; i += Math.max(1, Math.ceil(view.length / 512))) {
    h = (h * 31 + view[i]) >>> 0;
  }
  return `${view.length}-${h}`;
}

// Utility to show selected image
function loadImagePreview(file, imgEl) {
  if (!imgEl) {
    console.error("loadImagePreview: imgEl is null");
    return;
  }
  const reader = new FileReader();
  reader.onload = (e) => {
    imgEl.src = e.target.result;
    imgEl.classList.add("visible");
  };
  reader.readAsDataURL(file);
}

// Update strength label meaningfully
function updateStrengthLabel(value) {
  const wmStrengthLabel = document.getElementById('wm-strength-label');
  if (!wmStrengthLabel) return; // Exit if element doesn't exist

  const val = Number(value);
  let label = "Low";
  if (val > 80) label = "Very high";
  else if (val > 60) label = "High";
  else if (val > 40) label = "Medium";
  else if (val > 20) label = "Soft";
  wmStrengthLabel.textContent = label;
}

// Initialize watermark functionality only if elements exist
function initWatermarkFunctionality() {
  try {
    console.log("===== INITIALIZING WATERMARK FUNCTIONALITY =====");

    const wmDropzone = document.getElementById("wm-dropzone");
    const wmInput = document.getElementById("wm-input");
    const wmOwnerInput = document.getElementById("wm-owner-id");
    const wmStrengthInput = document.getElementById("wm-strength");
    const wmStrengthLabel = document.getElementById("wm-strength-label");
    const wmApplyBtn = document.getElementById("wm-apply-btn");
    const wmPreviewPlaceholder = document.getElementById("wm-preview-placeholder");
    const wmPreviewOriginal = document.getElementById("wm-preview-original");
    const wmPreviewWatermarked = document.getElementById("wm-preview-watermarked");
    const wmDownloadBtn = document.getElementById("wm-download-btn");

    console.log("Elements found:", {
      wmDropzone: !!wmDropzone,
      wmInput: !!wmInput,
      wmOwnerInput: !!wmOwnerInput,
      wmStrengthInput: !!wmStrengthInput,
      wmApplyBtn: !!wmApplyBtn,
      wmPreviewOriginal: !!wmPreviewOriginal,
      wmPreviewWatermarked: !!wmPreviewWatermarked,
      wmDownloadBtn: !!wmDownloadBtn
    });

    // Only proceed if watermark elements exist
    if (!wmDropzone || !wmInput || !wmApplyBtn) {
      console.log('Watermark elements not found, skipping watermark functionality');
      return;
    }

    // Set up strength input if it exists
    if (wmStrengthInput) {
      updateStrengthLabel(wmStrengthInput.value);
      wmStrengthInput.addEventListener("input", (e) =>
        updateStrengthLabel(e.target.value)
      );
    }

    // Drag & drop wiring for watermark upload
    let currentWMFile = null;

    // When user selects an image, show it as "original" and clear watermarked preview
    setupDropzone(wmDropzone, wmInput, (file) => {
      try {
        console.log("File selected via dropzone:", file.name);
        currentWMFile = file;
        if (wmPreviewPlaceholder) wmPreviewPlaceholder.style.display = "none";
        loadImagePreview(file, wmPreviewOriginal);
        if (wmPreviewWatermarked) {
          wmPreviewWatermarked.src = "";
          wmPreviewWatermarked.classList.remove("visible");
        }
        if (wmDownloadBtn) {
          wmDownloadBtn.disabled = true;
          delete wmDownloadBtn.dataset.filename;
        }
        console.log("Image preview loaded:", file.name);
      } catch (err) {
        console.error("Error in file selection callback:", err);
      }
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
    wmApplyBtn.addEventListener("click", async (e) => {
      e.preventDefault();
      console.log("Watermark apply button clicked");

      if (!currentWMFile) {
        console.log("No file selected, showing error");
        wmDropzone.classList.add("drag-over");
        setTimeout(() => wmDropzone.classList.remove("drag-over"), 600);
        return;
      }

      const ownerId = wmOwnerInput.value.trim();
      if (!ownerId) {
        console.log("No owner ID provided");
        wmOwnerInput.focus();
        wmOwnerInput.classList.add("shake");
        setTimeout(() => wmOwnerInput.classList.remove("shake"), 400);
        return;
      }

      console.log("Starting watermark process for:", currentWMFile.name, "Owner:", ownerId);

      // Start fake loading state
      wmApplyBtn.classList.add("loading");
      wmApplyBtn.disabled = true;

      try {
        // Compute file hash for local storage check
        const fileHash = await hashFile(currentWMFile);
        console.log("File hash computed:", fileHash);

        // Check if this image has already been watermarked (stored in localStorage)
        if (watermarkStore.has(fileHash)) {
          const existingWatermark = watermarkStore.get(fileHash);
          wmApplyBtn.classList.remove("loading");
          wmApplyBtn.disabled = false;

          // Show error state
          wmOwnerInput.classList.add("shake");
          setTimeout(() => wmOwnerInput.classList.remove("shake"), 400);

          // Create and show error popup
          const errorDiv = document.createElement("div");
          errorDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: rgba(185, 28, 28, 0.95);
        color: #fecaca;
        padding: 16px 20px;
        border-radius: 12px;
        border: 1px solid rgba(248, 113, 113, 0.8);
        box-shadow: 0 0 30px rgba(185, 28, 28, 0.6);
        max-width: 400px;
        z-index: 10000;
        font-size: 0.9rem;
        animation: slideIn 0.3s ease-out;
      `;
          errorDiv.innerHTML = `
        <div style="font-weight: 600; margin-bottom: 4px;">⚠️ Image Already Watermarked</div>
        <div>This image was previously watermarked with owner ID: <strong>${existingWatermark.ownerId}</strong>. Cannot re-watermark.</div>
      `;
          document.body.appendChild(errorDiv);

          // Auto-remove after 5 seconds
          setTimeout(() => {
            errorDiv.style.animation = "slideOut 0.3s ease-out";
            setTimeout(() => errorDiv.remove(), 300);
          }, 5000);

          return;
        }

        console.log("Proceeding with watermarking...");

        // Send to backend to embed the watermark
        const strength = Number(wmStrengthInput.value);
        // Map strength slider (1-100) to watermark strength (1-10)
        const watermarkStrength = Math.max(1, Math.min(10, Math.ceil(strength / 10)));

        const formDataEmbed = new FormData();
        formDataEmbed.append("file", currentWMFile);
        formDataEmbed.append("owner_id", ownerId);
        formDataEmbed.append("strength", String(watermarkStrength));

        console.log("Sending watermark embed request to backend...");
        console.log("API endpoint: http://127.0.0.1:8000/watermark/embed");
        console.log("Form data: file=" + currentWMFile.name + ", owner_id=" + ownerId + ", strength=" + watermarkStrength);

        let embedResponse;
        try {
          embedResponse = await fetch("http://127.0.0.1:8000/watermark/embed", {
            method: "POST",
            body: formDataEmbed,
          });
          console.log("Fetch completed, got response object");
        } catch (fetchError) {
          console.error("FETCH ERROR:", fetchError);
          console.error("Fetch error message:", fetchError.message);
          throw new Error(`Network error contacting backend: ${fetchError.message}`);
        }

        console.log("Embed response status:", embedResponse.status);
        console.log("Content-Type:", embedResponse.headers.get('content-type'));

        if (!embedResponse.ok) {
          console.error("Response not OK, status:", embedResponse.status);
          try {
            const errorText = await embedResponse.text();
            console.error("Backend error response:", errorText);
            throw new Error(`Backend error: ${errorText}`);
          } catch (e) {
            throw new Error(`Backend returned status ${embedResponse.status}`);
          }
        }

        // Get the watermarked image blob - ONLY read once!
        console.log("About to read response as blob...");
        let watermarkedBlob;
        try {
          watermarkedBlob = await embedResponse.blob();
          console.log("Blob read successfully, size:", watermarkedBlob.size);
          console.log("Blob type:", watermarkedBlob.type);
        } catch (blobError) {
          console.error("ERROR reading blob:", blobError);
          console.error("Blob error message:", blobError.message);
          throw new Error(`Failed to read response blob: ${blobError.message}`);
        }
        console.log("Received watermarked image blob, size:", watermarkedBlob.size);

        if (!wmPreviewWatermarked) {
          console.error("CRITICAL: wmPreviewWatermarked element is NULL!");
          throw new Error("Preview image element not found in DOM");
        }

        // Display the watermarked preview
        const watermarkedUrl = URL.createObjectURL(watermarkedBlob);
        console.log("Setting watermarked preview src...");
        wmPreviewWatermarked.src = watermarkedUrl;
        console.log("Watermarked preview displayed");

        // Store watermark metadata in localStorage
        watermarkStore.set(fileHash, {
          ownerId,
          strength: watermarkStrength,
          timestamp: Date.now(),
          watermarkedImageUrl: watermarkedUrl,
        });
        saveStoreToStorage(watermarkStore);

        // Enable download button and set a reasonable filename
        if (wmDownloadBtn) {
          const safeOwner = ownerId.replace(/[^a-zA-Z0-9-_.]/g, "-") || "owner";
          const downloadFilename = `${safeOwner}-watermarked-${currentWMFile.name}`;
          wmDownloadBtn.disabled = false;
          wmDownloadBtn.dataset.filename = downloadFilename;
          wmDownloadBtn.dataset.blobUrl = watermarkedUrl;
        }

        // Activate watermarked view
        const previewToggleButtons = document.querySelectorAll(
          "[data-preview-mode]"
        );
        previewToggleButtons.forEach((b) => {
          const mode = b.getAttribute("data-preview-mode");
          b.classList.toggle("chip-active", mode === "watermarked");
        });

        if (wmPreviewOriginal) wmPreviewOriginal.style.display = "none";
        if (wmPreviewWatermarked) wmPreviewWatermarked.style.display = "block";

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

        // Show success notification
        const successDiv = document.createElement("div");
        successDiv.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: rgba(22, 163, 74, 0.95);
      color: #bbf7d0;
      padding: 16px 20px;
      border-radius: 12px;
      border: 1px solid rgba(34, 197, 94, 0.85);
      box-shadow: 0 0 30px rgba(22, 163, 74, 0.5);
      max-width: 400px;
      z-index: 10000;
      font-size: 0.9rem;
      animation: slideIn 0.3s ease-out;
    `;
        successDiv.innerHTML = `
      <div style="font-weight: 600; margin-bottom: 4px;">✓ Watermark Applied</div>
      <div>Image successfully watermarked with owner ID: ${ownerId}</div>
    `;
        document.body.appendChild(successDiv);

        setTimeout(() => {
          successDiv.style.animation = "slideOut 0.3s ease-out";
          setTimeout(() => successDiv.remove(), 300);
        }, 4000);
      } catch (error) {
        wmApplyBtn.classList.remove("loading");
        wmApplyBtn.disabled = false;

        console.error("Watermarking error:", error);
        console.error("Error message:", error?.message);
        console.error("Error stack:", error?.stack);

        // Show error notification
        const errorDiv = document.createElement("div");
        errorDiv.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: rgba(185, 28, 28, 0.95);
      color: #fecaca;
      padding: 16px 20px;
      border-radius: 12px;
      border: 1px solid rgba(248, 113, 113, 0.8);
      box-shadow: 0 0 30px rgba(185, 28, 28, 0.6);
      max-width: 400px;
      z-index: 10000;
      font-size: 0.9rem;
      animation: slideIn 0.3s ease-out;
    `;
        errorDiv.innerHTML = `
      <div style="font-weight: 600; margin-bottom: 4px;">✗ Error</div>
      <div>Failed to process watermark: ${error.message}</div>
    `;
        document.body.appendChild(errorDiv);

        setTimeout(() => {
          errorDiv.style.animation = "slideOut 0.3s ease-out";
          setTimeout(() => errorDiv.remove(), 300);
        }, 5000);
      }
    });

    // Download button behavior for watermarked preview
    if (wmDownloadBtn) {
      wmDownloadBtn.addEventListener("click", () => {
        const src = wmPreviewWatermarked.src;
        if (!src) return;
        const filename = wmDownloadBtn.dataset.filename || "watermarked.png";
        const a = document.createElement("a");
        a.href = src;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        a.remove();
      });
    }

  } catch (error) {
    console.error("CRITICAL ERROR in initWatermarkFunctionality:", error);
    console.error("Stack:", error.stack);
  }
} // End of initWatermarkFunctionality

// Call the function to initialize watermark functionality
initWatermarkFunctionality();

// =============================
// AI Shield Functionality
// =============================
function initAIShieldFunctionality() {
  try {
    console.log("===== INITIALIZING AI SHIELD FUNCTIONALITY =====");

    const aisDropzone = document.getElementById("ais-dropzone");
    const aisInput = document.getElementById("ais-input");
    const aisStrength = document.getElementById("ais-strength");
    const aisStrengthLabel = document.getElementById("ais-strength-label");
    const aisBtn = document.getElementById("ais-btn");
    const aisPreview = document.getElementById("ais-preview");
    const aisPlaceholder = document.getElementById("ais-placeholder");
    const aisScore = document.getElementById("ais-score");
    const aisStatus = document.getElementById("ais-status");
    const aisDownloadBtn = document.getElementById("ais-download-btn");

    // Only proceed if elements exist
    if (!aisDropzone || !aisInput || !aisBtn) {
      console.log('AI Shield elements not found, skipping functionality');
      return;
    }

    // Update strength label
    function updateShieldLabel(val) {
      if (!aisStrengthLabel) return;
      let label = "Standard";
      if (val < 20) label = "Low (Invisible)";
      else if (val < 50) label = "Standard (Balanced)";
      else if (val < 80) label = "High (Strong)";
      else label = "Maximum (Visible Noise)";
      aisStrengthLabel.textContent = label;
    }

    if (aisStrength) {
      updateShieldLabel(aisStrength.value);
      aisStrength.addEventListener("input", (e) => updateShieldLabel(e.target.value));
    }

    let currentAISFile = null;

    // Setup dropzone using the shared helper
    setupDropzone(aisDropzone, aisInput, (file) => {
      console.log("AI Shield file selected:", file.name);
      currentAISFile = file;

      // Show preview of ORIGINAL image first
      loadImagePreview(file, aisPreview);
      aisPreview.style.display = "block";
      if (aisPlaceholder) aisPlaceholder.style.display = "none";

      // Reset result state
      aisStatus.className = "status-pill status-idle";
      aisStatus.textContent = "Ready to protect";
      aisScore.textContent = "–";
      aisDownloadBtn.disabled = true;
    });

    // Apply Shield Button
    aisBtn.addEventListener("click", async (e) => {
      e.preventDefault();
      if (!currentAISFile) {
        aisDropzone.classList.add("drag-over");
        setTimeout(() => aisDropzone.classList.remove("drag-over"), 600);
        return;
      }

      const strengthVal = aisStrength.value;
      console.log("Applying AI Shield with strength:", strengthVal);

      // UI Loading state
      aisBtn.classList.add("loading");
      aisBtn.disabled = true;
      aisStatus.className = "status-pill status-loading";
      aisStatus.textContent = "Generating adversarial noise...";

      try {
        const formData = new FormData();
        formData.append("file", currentAISFile);
        formData.append("strength", strengthVal); // Backend handles mapping

        const response = await fetch(`${API_BASE}/protect/process`, {
          method: "POST",
          body: formData
        });

        if (!response.ok) {
          throw new Error(`Protection failed: ${response.statusText}`);
        }

        // Get headers
        const robustness = response.headers.get("X-Robustness-Score") || "N/A";

        // Get blob
        const protectedBlob = await response.blob();
        const protectedUrl = URL.createObjectURL(protectedBlob);

        // Update UI with result
        aisPreview.src = protectedUrl;
        aisScore.textContent = `${robustness}%`;

        aisStatus.className = "status-pill status-success";
        aisStatus.textContent = "Protection Applied";

        // Enable download
        aisDownloadBtn.disabled = false;
        aisDownloadBtn.onclick = () => {
          const a = document.createElement("a");
          a.href = protectedUrl;
          a.download = `protected_${currentAISFile.name}`;
          document.body.appendChild(a);
          a.click();
          a.remove();
        };

        // Show success notification
        showNotification("Image protected successfully!", "success");

      } catch (err) {
        console.error("AI Shield Error:", err);
        aisStatus.className = "status-pill status-error";
        aisStatus.textContent = "Protection Failed";
        showNotification(`Error: ${err.message}`, "error");
      } finally {
        aisBtn.classList.remove("loading");
        aisBtn.disabled = false;
      }
    });

  } catch (e) {
    console.error("Error initializing AI Shield:", e);
  }
}
initAIShieldFunctionality();

// =============================
// Verify section logic
// =============================

// Web3 / Registry state
let connectedAccount = null;
let registryAbi = null;
let registryAddress = null;
let lastExtractedText = null;
let lastWatermarkFound = false;

const WALLET_STORAGE_KEY = "pngprotect.walletConnection.v1";

// Initialize wallet elements with null checks
const connectWalletBtn = document.getElementById("connect-wallet-btn");
const disconnectWalletBtn = document.getElementById("disconnect-wallet-btn");
const walletAddressSpan = document.getElementById("wallet-address");
const registerBtn = document.getElementById("register-onchain-btn");
const registerStatus = document.getElementById("register-status");

async function fetchRegistryAbi() {
  try {
    const res = await fetch("http://127.0.0.1:8000/registry/abi");
    if (!res.ok) {
      console.error("Failed to fetch registry ABI:", res.status);
      return null;
    }
    const json = await res.json();
    console.log("Registry ABI response:", json);
    registryAbi = json.abi || json;
    registryAddress = json.contract_address || json.contractAddress || json.address || null;
    console.log("Registry Address:", registryAddress, "ABI:", registryAbi ? "loaded" : "not loaded");
    return json;
  } catch (e) {
    console.error("Failed to fetch registry ABI:", e);
    return null;
  }
}

async function connectWallet() {
  if (!connectWalletBtn || !disconnectWalletBtn || !walletAddressSpan) {
    console.log('Wallet UI elements not found, skipping wallet functionality');
    return;
  }

  if (!window.ethereum) {
    alert("MetaMask not detected. Install MetaMask to use on-chain registration.");
    return;
  }
  try {
    // Request accounts - this should trigger MetaMask popup
    const accounts = await window.ethereum.request({ method: "eth_requestAccounts" });
    connectedAccount = accounts && accounts[0];
    if (connectedAccount) {
      const displayAddr = connectedAccount.slice(0, 6) + "..." + connectedAccount.slice(-4);
      walletAddressSpan.textContent = displayAddr;
      connectWalletBtn.style.display = "none";
      disconnectWalletBtn.style.display = "inline-block";
      console.log("Connected to wallet:", connectedAccount);
      // Store wallet connection state
      localStorage.setItem(WALLET_STORAGE_KEY, JSON.stringify({ account: connectedAccount }));
    }
    await fetchRegistryAbi();
    if (lastWatermarkFound) registerBtn.disabled = false;
  } catch (e) {
    console.error("Wallet connect failed:", e);
    if (e.code === 4001) {
      console.log("User rejected the connection request");
    }
  }
}

function disconnectWallet() {
  if (!connectWalletBtn || !disconnectWalletBtn || !walletAddressSpan || !registerBtn || !registerStatus) {
    console.log('Wallet UI elements not found, skipping disconnect');
    return;
  }

  connectedAccount = null;
  walletAddressSpan.textContent = "Not connected";
  connectWalletBtn.style.display = "inline-block";
  disconnectWalletBtn.style.display = "none";
  registerBtn.disabled = true;
  registerStatus.textContent = "Not registered";
  // Clear wallet connection state from storage
  localStorage.removeItem(WALLET_STORAGE_KEY);
  console.log("Wallet disconnected");
}

// =============================
// MetaMask Event Listeners
// Listen for account/chain changes
// =============================
function setupMetaMaskListeners() {
  if (!window.ethereum) return;

  // Listen for account changes
  window.ethereum.on("accountsChanged", (accounts) => {
    console.log("MetaMask accounts changed:", accounts);
    if (accounts && accounts.length > 0) {
      // Account was switched in MetaMask
      connectedAccount = accounts[0];
      const displayAddr = connectedAccount.slice(0, 6) + "..." + connectedAccount.slice(-4);
      walletAddressSpan.textContent = displayAddr;
      connectWalletBtn.style.display = "none";
      disconnectWalletBtn.style.display = "inline-block";
      localStorage.setItem(WALLET_STORAGE_KEY, JSON.stringify({ account: connectedAccount }));
      console.log("Account switched to:", connectedAccount);
    } else {
      // User disconnected from MetaMask
      console.log("MetaMask disconnected by user");
      disconnectWallet();
    }
  });

  // Listen for chain/network changes
  window.ethereum.on("chainChanged", (chainId) => {
    console.log("MetaMask chain changed to:", chainId);
  });
}

setupMetaMaskListeners();

if (connectWalletBtn) {
  connectWalletBtn.addEventListener("click", connectWallet);
}

if (disconnectWalletBtn) {
  disconnectWalletBtn.addEventListener("click", disconnectWallet);
}

// =============================
// Wallet Initialization on Page Load
// Clear any residual wallet data to ensure fresh state
// =============================
function initializeWalletState() {
  if (!connectWalletBtn || !disconnectWalletBtn || !walletAddressSpan || !registerBtn || !registerStatus) {
    console.log('Wallet UI elements not found, skipping wallet initialization');
    return;
  }

  // Always start with wallet disconnected on page load
  // User must explicitly click "Connect Wallet" each time
  localStorage.removeItem(WALLET_STORAGE_KEY);
  connectedAccount = null;
  walletAddressSpan.textContent = "Not connected";
  connectWalletBtn.style.display = "inline-block";
  disconnectWalletBtn.style.display = "none";
  registerBtn.disabled = true;
  registerStatus.textContent = "Not registered";
  console.log("Wallet state initialized: disconnected");
}

// Initialize wallet state when page loads
document.addEventListener("DOMContentLoaded", initializeWalletState);
// Also initialize immediately if DOM is already loaded
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initializeWalletState);
} else {
  initializeWalletState();
}

if (registerBtn) {
  registerBtn.addEventListener("click", async () => {
    if (!connectedAccount) {
      console.log("No account connected, connecting wallet...");
      await connectWallet();
      if (!connectedAccount) return;
    }
    if (!lastWatermarkFound || !lastExtractedText) {
      registerStatus.textContent = "No watermark available to register";
      return;
    }

    registerBtn.disabled = true;
    registerStatus.textContent = "Preparing transaction…";

    try {
      if (!registryAbi || !registryAddress) {
        console.log("Fetching registry ABI...");
        await fetchRegistryAbi();
      }

      if (!registryAbi || !registryAddress) {
        const errMsg = !registryAddress
          ? "⚠️ No CONTRACT_ADDRESS set on server. Deploy OwnershipRegistry.sol and set CONTRACT_ADDRESS env var."
          : "⚠️ Registry ABI not loaded.";
        registerStatus.textContent = errMsg;
        console.error(errMsg);
        registerBtn.disabled = false;
        return;
      }

      console.log("Creating contract instance at", registryAddress);
      const provider = new ethers.providers.Web3Provider(window.ethereum);
      const signer = provider.getSigner();
      const contract = new ethers.Contract(registryAddress, registryAbi, signer);

      // keccak256 of the extracted text (utf8)
      const uuidHash = ethers.utils.keccak256(ethers.utils.toUtf8Bytes(lastExtractedText));
      console.log("UUID:", lastExtractedText, "Hash:", uuidHash);

      registerStatus.textContent = "Sending transaction…";
      const tx = await contract.register(uuidHash);
      console.log("Transaction sent:", tx.hash);
      registerStatus.textContent = `Pending tx ${tx.hash.slice(0, 10)}…`;
      await tx.wait();
      registerStatus.textContent = `✓ Registered (${tx.hash.slice(0, 10)}…)`;
      console.log("Transaction confirmed!");
    } catch (e) {
      console.error("Register error:", e);
      registerStatus.textContent = e && e.message ? e.message.substring(0, 60) : "Registration failed";
    } finally {
      registerBtn.disabled = false;
    }
  });
}

// Initialize verify functionality only if elements exist
function initVerifyFunctionality() {
  const vfDropzone = document.getElementById("vf-dropzone");
  const vfInput = document.getElementById("vf-input");
  const vfBtn = document.getElementById("vf-btn");
  const vfStatus = document.getElementById("vf-status");
  const vfDetected = document.getElementById("vf-detected");
  const vfOwner = document.getElementById("vf-owner");
  const vfConfidence = document.getElementById("vf-confidence");
  const vfBars = document.getElementById("vf-bars");

  // Only proceed if verify elements exist
  if (!vfDropzone || !vfInput || !vfBtn) {
    console.log('Verify elements not found, skipping verify functionality');
    return;
  }

  let currentVfFile = null;

  // Setup drag & drop for verification upload
  setupDropzone(vfDropzone, vfInput, (file) => {
    console.log("Verify file selected:", file.name);
    currentVfFile = file;
    vfStatus.textContent = `Ready: ${file.name}`;
    vfStatus.className = "status-pill status-success";

    // Update dropzone UI to show file
    const inner = vfDropzone.querySelector('.dropzone-inner');
    if (inner) {
      inner.innerHTML = `
            <span class="drop-icon">📄</span>
            <p>${file.name}</p>
            <p class="drop-subtext">Click to change</p>
        `;
    }

    // Show preview
    const vfPreview = document.getElementById("vf-preview");
    if (vfPreview) {
      loadImagePreview(file, vfPreview);
      vfPreview.style.display = "block";
    }
  });

  // Verify action - Real backend verification
  vfBtn.addEventListener("click", async (e) => {
    e.preventDefault();
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

    try {
      // Send to backend for verification
      const formData = new FormData();
      formData.append("file", currentVfFile);

      console.log("Verifying watermark with backend...");
      const response = await fetch("http://127.0.0.1:8000/verify", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error("Backend verification error:", errorText);
        throw new Error(`Verification failed: ${errorText}`);
      }

      const result = await response.json();
      console.log("Backend verification result:", result);

      // Extract values from response
      const watermarkFound = result.watermark_found;
      const ownerID = result.owner_id || "Unknown";
      const extractedText = result.extracted_text || null;
      const matchRatio = result.match_ratio || 0;
      const confidence = result.confidence || 0;

      // Save for on-chain registration
      lastExtractedText = extractedText;
      lastWatermarkFound = !!watermarkFound;

      // Display results
      if (watermarkFound) {
        vfStatus.textContent = "✓ Watermark verified";
        vfStatus.className = "status-pill status-success";
        vfDetected.textContent = "Yes";
        vfOwner.textContent = ownerID !== "Unknown" ? ownerID : extractedText || "Unknown";
        vfConfidence.textContent = `${confidence}%`;
        console.log(`Watermark found - Owner: ${ownerID}, Extracted: ${extractedText}, Match: ${matchRatio}`);
      } else {
        vfStatus.textContent = "✗ No watermark detected";
        vfStatus.className = "status-pill status-error";
        vfDetected.textContent = "No";
        vfOwner.textContent = "None";
        vfConfidence.textContent = `${confidence}%`;
        console.log("No watermark found");
      }

      // Enable register UI only when both watermark exists and wallet is connected
      if (watermarkFound && connectedAccount) {
        registerBtn.disabled = false;
        registerStatus.textContent = "Ready to register";
      } else if (watermarkFound) {
        registerBtn.disabled = true;
        registerStatus.textContent = "Connect wallet to register";
      } else {
        registerBtn.disabled = true;
        registerStatus.textContent = "Not registered";
      }

      // Brief accent animation on bars to emphasize result
      vfBars.classList.add("flash");
      setTimeout(() => vfBars.classList.remove("flash"), 400);

    } catch (error) {
      console.error("Verification error:", error);
      vfStatus.textContent = "✗ Verification failed";
      vfStatus.className = "status-pill status-error";
      vfDetected.textContent = "Error";
      vfOwner.textContent = error.message;
      vfConfidence.textContent = "0%";

      // Show error notification
      const errorDiv = document.createElement("div");
      errorDiv.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      background: rgba(185, 28, 28, 0.95);
      color: #fecaca;
      padding: 16px 20px;
      border-radius: 12px;
      border: 1px solid rgba(248, 113, 113, 0.8);
      box-shadow: 0 0 30px rgba(185, 28, 28, 0.6);
      max-width: 400px;
      z-index: 10000;
      font-size: 0.9rem;
      animation: slideIn 0.3s ease-out;
    `;
      errorDiv.innerHTML = `
      <div style="font-weight: 600; margin-bottom: 4px;">✗ Verification Error</div>
      <div>${error.message}</div>
    `;
      document.body.appendChild(errorDiv);

      setTimeout(() => {
        errorDiv.style.animation = "slideOut 0.3s ease-out";
        setTimeout(() => errorDiv.remove(), 300);
      }, 5000);

    } finally {
      vfBtn.classList.remove("loading");
      vfBtn.disabled = false;
    }
  });

} // End of initVerifyFunctionality

// Call the function to initialize verify functionality
initVerifyFunctionality();

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

// Call the function to initialize verify functionality
// Duplicate call removed


// =============================
// Strip Metadata section logic
// =============================

// Initialize strip metadata functionality only if elements exist
function initStripMetadataFunctionality() {
  const smDropzone = document.getElementById("sm-dropzone");
  const smInput = document.getElementById("sm-input");
  const smBtn = document.getElementById("sm-btn");
  const smStatus = document.getElementById("sm-status");
  const smOriginalSize = document.getElementById("sm-original-size");
  const smCleanedSize = document.getElementById("sm-cleaned-size");
  const smReduction = document.getElementById("sm-reduction");
  const smDownloadBtn = document.getElementById("sm-download-btn");

  // Only proceed if strip metadata elements exist
  if (!smDropzone || !smInput || !smBtn) {
    console.log('Strip metadata elements not found, skipping strip metadata functionality');
    return;
  }

  let currentSmFile = null;
  let cleanedImageBlob = null;

  // Setup drag & drop for metadata stripping upload
  setupDropzone(smDropzone, smInput, (file) => {
    currentSmFile = file;
    smStatus.textContent = "Ready to clean";
    smStatus.className = "status-pill status-idle";
    smOriginalSize.textContent = formatFileSize(file.size);
    smCleanedSize.textContent = "–";
    smReduction.textContent = "–";
    cleanedImageBlob = null;
    smDownloadBtn.disabled = true;
  });

  // Format bytes to human readable size
  function formatFileSize(bytes) {
    if (bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  }

  // Strip metadata action
  smBtn.addEventListener("click", async (e) => {
    e.preventDefault();
    if (!currentSmFile) {
      smDropzone.classList.add("drag-over");
      setTimeout(() => smDropzone.classList.remove("drag-over"), 600);
      return;
    }

    smBtn.classList.add("loading");
    smBtn.disabled = true;

    smStatus.textContent = "Removing metadata…";
    smStatus.className = "status-pill status-idle";

    try {
      // Create FormData and send to backend
      const formData = new FormData();
      formData.append("file", currentSmFile);

      const response = await fetch("http://127.0.0.1:8000/metadata/strip", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }

      // Get the cleaned image as a blob
      cleanedImageBlob = await response.blob();
      const cleanedSize = cleanedImageBlob.size;
      const originalSize = currentSmFile.size;
      const reduction = originalSize - cleanedSize;
      const reductionPercent = ((reduction / originalSize) * 100).toFixed(1);

      // Update UI with results
      smStatus.textContent = "Metadata successfully removed!";
      smStatus.className = "status-pill status-success";
      smCleanedSize.textContent = formatFileSize(cleanedSize);
      smReduction.textContent = `${reductionPercent}%`;

      // Enable download button
      smDownloadBtn.disabled = false;

      // Brief accent animation
      smDownloadBtn.style.transform = "scale(1.05)";
      setTimeout(() => {
        smDownloadBtn.style.transform = "";
      }, 200);
    } catch (error) {
      smStatus.textContent = "Error removing metadata";
      smStatus.className = "status-pill status-error";
      console.error("Metadata stripping error:", error);
    }

    smBtn.classList.remove("loading");
    smBtn.disabled = false;
  });

  // Download cleaned image
  smDownloadBtn.addEventListener("click", () => {
    if (!cleanedImageBlob) return;

    const filename = currentSmFile.name
      ? `cleaned_${currentSmFile.name}`
      : "cleaned_image.png";

    const url = URL.createObjectURL(cleanedImageBlob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  });

} // End of initStripMetadataFunctionality

// Call the function to initialize strip metadata functionality
initStripMetadataFunctionality();

// =============================
// Watermark Tampering Detection
// =============================

function initDetectionFunctionality() {
  // Elements
  const detDropzone = document.getElementById('det-dropzone');
  const detInput = document.getElementById('det-input');
  const detFullBtn = document.getElementById('det-full-btn');
  const detFastBtn = document.getElementById('det-fast-btn');
  const detStatus = document.getElementById('det-status');
  const detConfidenceContainer = document.getElementById('det-confidence-container');
  const detConfidenceValue = document.getElementById('det-confidence-value');
  const detConfidenceFill = document.getElementById('det-confidence-fill');
  const detConfidenceLevel = document.getElementById('det-confidence-level');
  const detVerdictContainer = document.getElementById('det-verdict-container');
  const detVerdictIcon = document.getElementById('det-verdict-icon');
  const detVerdictTitle = document.getElementById('det-verdict-title');
  const detVerdictText = document.getElementById('det-verdict-text');
  const detTechniquesContainer = document.getElementById('det-techniques-container');
  const detTechniquesList = document.getElementById('det-techniques-list');
  const detExplanationContainer = document.getElementById('det-explanation-container');
  const detExplanationText = document.getElementById('det-explanation-text');
  const detTechnicalContainer = document.getElementById('det-technical-container');
  const detTechnicalText = document.getElementById('det-technical-text');
  const detToggleTechnical = document.getElementById('det-toggle-technical');

  let currentDetFile = null;
  let technicalDetailsVisible = false;

  // Dropzone functionality
  detDropzone.addEventListener('click', () => detInput.click());
  detDropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    detDropzone.style.borderColor = 'var(--accent-cyan)';
    detDropzone.style.background = 'rgba(34, 211, 238, 0.05)';
  });
  detDropzone.addEventListener('dragleave', () => {
    detDropzone.style.borderColor = '';
    detDropzone.style.background = '';
  });
  detDropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    detDropzone.style.borderColor = '';
    detDropzone.style.background = '';
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      detInput.files = files;
      handleDetectionFileSelect();
    }
  });

  detInput.addEventListener('change', handleDetectionFileSelect);

  function handleDetectionFileSelect() {
    const file = detInput.files[0];
    if (!file) return;
    if (!file.type.startsWith('image/')) {
      alert('Please select an image file');
      return;
    }
    currentDetFile = file;
    detDropzone.querySelector('.dropzone-inner').innerHTML = `
      <span class="drop-icon">✅</span>
      <p>${file.name}</p>
      <p class="drop-subtext">${formatFileSize(file.size)}</p>
    `;
    detStatus.textContent = 'Ready to analyze';
    detStatus.className = 'status-pill status-idle';
    resetDetectionResults();

    // Show preview
    const detPreview = document.getElementById("det-preview");
    if (detPreview) {
      loadImagePreview(file, detPreview);
      detPreview.style.display = "block";
    }
  }

  function resetDetectionResults() {
    detConfidenceContainer.style.display = 'none';
    detVerdictContainer.style.display = 'none';
    detTechniquesContainer.style.display = 'none';
    detExplanationContainer.style.display = 'none';
    detTechnicalContainer.style.display = 'none';
    detToggleTechnical.style.display = 'none';
    technicalDetailsVisible = false;
    detToggleTechnical.textContent = 'Show Technical Details';
  }

  // Analyze function
  async function analyzeImage(mode) {
    if (!currentDetFile) {
      alert('Please select an image first');
      return;
    }

    const btn = mode === 'full' ? detFullBtn : detFastBtn;
    btn.classList.add('loading');
    btn.disabled = true;

    detStatus.textContent = mode === 'full' ? 'Running full analysis...' : 'Running forensic analysis...';
    detStatus.className = 'status-pill status-processing';
    resetDetectionResults();

    try {
      const formData = new FormData();
      formData.append('file', currentDetFile);

      const endpoint = mode === 'full' ? '/detect/detect' : '/detect/forensics-only';
      const response = await fetch(API_BASE + endpoint, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const result = await response.json();
      displayDetectionResults(result);
    } catch (error) {
      console.error('Detection error:', error);
      detStatus.textContent = 'Error analyzing image: ' + error.message;
      detStatus.className = 'status-pill status-error';
    }

    btn.classList.remove('loading');
    btn.disabled = false;
  }

  function displayDetectionResults(result) {
    const confidence = result.overall_tampering_confidence || 0;
    const confidenceLevel = result.confidence_level || 'Unknown';
    const likelyRemoved = result.likely_removed === true;

    // Update status
    detStatus.textContent = `Analysis complete - ${confidenceLevel} confidence`;
    detStatus.className = confidence > 60 ? 'status-pill status-warning' : 'status-pill status-success';

    // Display confidence score
    detConfidenceContainer.style.display = 'block';
    detConfidenceValue.textContent = `${Math.round(confidence)}%`;
    detConfidenceFill.style.width = `${confidence}%`;

    // Update color based on confidence
    if (confidence >= 70) {
      detConfidenceFill.style.background = 'linear-gradient(90deg, #f97373, #ff6b6b)';
      detConfidenceLevel.textContent = `Likelihood: Very High (${confidenceLevel})`;
    } else if (confidence >= 50) {
      detConfidenceFill.style.background = 'linear-gradient(90deg, #facc15, #fbbf24)';
      detConfidenceLevel.textContent = `Likelihood: Medium (${confidenceLevel})`;
    } else if (confidence >= 30) {
      detConfidenceFill.style.background = 'linear-gradient(90deg, #22d3ee, #06b6d4)';
      detConfidenceLevel.textContent = `Likelihood: Low (${confidenceLevel})`;
    } else {
      detConfidenceFill.style.background = 'linear-gradient(90deg, #22c55e, #16a34a)';
      detConfidenceLevel.textContent = `Likelihood: Minimal (${confidenceLevel})`;
    }

    // Display verdict
    detVerdictContainer.style.display = 'block';
    if (likelyRemoved) {
      detVerdictIcon.textContent = '⚠️';
      detVerdictContainer.style.borderLeftColor = '#f97373';
      detVerdictTitle.textContent = 'Likely Tampering Detected';
      detVerdictText.textContent = 'The image shows signs of watermark removal or significant modification.';
    } else if (confidence > 30) {
      detVerdictIcon.textContent = '⚠️';
      detVerdictContainer.style.borderLeftColor = '#facc15';
      detVerdictTitle.textContent = 'Possible Tampering';
      detVerdictText.textContent = 'The image may have been modified. Manual review recommended.';
    } else {
      detVerdictIcon.textContent = '✅';
      detVerdictContainer.style.borderLeftColor = '#22c55e';
      detVerdictTitle.textContent = 'Image Integrity Intact';
      detVerdictText.textContent = 'No significant signs of watermark tampering detected.';
    }

    // Display techniques
    if (result.detected_techniques && result.detected_techniques.length > 0) {
      detTechniquesContainer.style.display = 'block';
      detTechniquesList.innerHTML = result.detected_techniques
        .map(technique => `
          <div style="display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem 0;">
            <span style="color: #facc15;">◆</span>
            <span style="color: var(--text-soft);">${technique}</span>
          </div>
        `)
        .join('');
    }

    // Display forensic explanation
    if (result.forensic_explanation) {
      detExplanationContainer.style.display = 'block';
      detExplanationText.textContent = result.forensic_explanation;
    }

    // Store technical summary for toggle
    if (result.technical_summary) {
      detTechnicalContainer.style.display = 'none';
      detTechnicalText.textContent = result.technical_summary;
      detToggleTechnical.style.display = 'block';
    }
  }

  // Button event listeners
  detFullBtn.addEventListener('click', (e) => {
    e.preventDefault();
    analyzeImage('full');
  });
  detFastBtn.addEventListener('click', (e) => {
    e.preventDefault();
    analyzeImage('fast');
  });

  // Toggle technical details
  detToggleTechnical.addEventListener('click', () => {
    technicalDetailsVisible = !technicalDetailsVisible;
    detTechnicalContainer.style.display = technicalDetailsVisible ? 'block' : 'none';
    detToggleTechnical.textContent = technicalDetailsVisible ? 'Hide Technical Details' : 'Show Technical Details';
  });
}

// Initialize detection functionality
initDetectionFunctionality();