// Add this to the beginning of initWatermarkFunctionality to debug

console.log("=== WATERMARK INITIALIZATION DEBUG ===");
console.log("All elements:");

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

console.log({
  wmDropzone: !!wmDropzone,
  wmInput: !!wmInput,
  wmOwnerInput: !!wmOwnerInput,
  wmStrengthInput: !!wmStrengthInput,
  wmStrengthLabel: !!wmStrengthLabel,
  wmApplyBtn: !!wmApplyBtn,
  wmPreviewPlaceholder: !!wmPreviewPlaceholder,
  wmPreviewOriginal: !!wmPreviewOriginal,
  wmPreviewWatermarked: !!wmPreviewWatermarked,
  wmDownloadBtn: !!wmDownloadBtn,
});

if (!wmDropzone || !wmInput || !wmApplyBtn) {
  console.error("CRITICAL: Missing required elements!");
  console.log("wmDropzone:", wmDropzone);
  console.log("wmInput:", wmInput);
  console.log("wmApplyBtn:", wmApplyBtn);
  return;
}

console.log("✓ All required elements found!");
console.log("Setting up event listeners...");

// Test setupDropzone function
console.log("Testing setupDropzone...");
setupDropzone(wmDropzone, wmInput, (file) => {
  console.log("File selected:", file.name);
});

console.log("✓ Watermark functionality initialized!");
