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
const wmDownloadBtn = document.getElementById("wm-download-btn");

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
  if (wmDownloadBtn) {
    wmDownloadBtn.disabled = true;
    delete wmDownloadBtn.dataset.filename;
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

  try {
    // First, compute file hash to check against localStorage store
    const fileHash = await hashFile(currentWMFile);
    
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

    // Also check with backend for additional validation
    const formDataDetect = new FormData();
    formDataDetect.append("file", currentWMFile);

    console.log("Checking watermark detection with backend...");
    const detectResponse = await fetch("http://localhost:8000/verify/detect", {
      method: "POST",
      body: formDataDetect,
    });

    if (!detectResponse.ok) {
      const errorText = await detectResponse.text();
      console.error("Backend detection error:", errorText);
      throw new Error(`Failed to check for existing watermark: ${errorText}`);
    }

    const detection = await detectResponse.json();
    console.log("Backend detection result:", detection);

    // If backend also detects a watermark, show error and stop
    if (detection.has_watermark) {
      console.warn("Watermark detected - blocking re-watermarking");
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
        <div>${detection.message}</div>
      `;
      document.body.appendChild(errorDiv);

      // Auto-remove after 5 seconds
      setTimeout(() => {
        errorDiv.style.animation = "slideOut 0.3s ease-out";
        setTimeout(() => errorDiv.remove(), 300);
      }, 5000);

      return;
    }
    
    console.log("No watermark detected - proceeding with watermarking");

    // Now send to backend to actually embed the watermark
    const strength = Number(wmStrengthInput.value);
    // Map strength slider (1-100) to watermark strength (1-10)
    const watermarkStrength = Math.max(1, Math.min(10, Math.ceil(strength / 10)));
    
    const formDataEmbed = new FormData();
    formDataEmbed.append("file", currentWMFile);
    formDataEmbed.append("owner_id", ownerId);
    formDataEmbed.append("strength", String(watermarkStrength));

    const embedResponse = await fetch("http://localhost:8000/watermark/embed", {
      method: "POST",
      body: formDataEmbed,
    });

    if (!embedResponse.ok) {
      const errorText = await embedResponse.text();
      throw new Error(`Failed to embed watermark into image: ${errorText}`);
    }

    // Get the watermarked image blob
    const watermarkedBlob = await embedResponse.blob();

    // Display the watermarked preview
    const watermarkedUrl = URL.createObjectURL(watermarkedBlob);
    wmPreviewWatermarked.src = watermarkedUrl;

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

const connectWalletBtn = document.getElementById("connect-wallet-btn");
const disconnectWalletBtn = document.getElementById("disconnect-wallet-btn");
const walletAddressSpan = document.getElementById("wallet-address");
const registerBtn = document.getElementById("register-onchain-btn");
const registerStatus = document.getElementById("register-status");

async function fetchRegistryAbi() {
  try {
    const res = await fetch("http://localhost:8000/registry/abi");
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

// Verify action - Real backend verification
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

  try {
    // Send to backend for verification
    const formData = new FormData();
    formData.append("file", currentVfFile);

    console.log("Verifying watermark with backend...");
    const response = await fetch("http://localhost:8000/verify", {
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
// =============================
// Strip Metadata section logic
// =============================

const smDropzone = document.getElementById("sm-dropzone");
const smInput = document.getElementById("sm-input");
const smBtn = document.getElementById("sm-btn");
const smStatus = document.getElementById("sm-status");
const smOriginalSize = document.getElementById("sm-original-size");
const smCleanedSize = document.getElementById("sm-cleaned-size");
const smReduction = document.getElementById("sm-reduction");
const smDownloadBtn = document.getElementById("sm-download-btn");

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
smBtn.addEventListener("click", async () => {
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

    const response = await fetch("http://localhost:8000/metadata/strip", {
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