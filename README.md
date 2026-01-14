# PNGProtect 🛡️  
**Invisible Watermarking & Integrity Protection for PNG Images**

Protect PNG images from unauthorized reuse by embedding invisible, resilient watermarks and verifying image integrity through perceptual hashing. PNGProtect is designed for creators, developers, and researchers who want lightweight yet powerful image ownership protection.

[🌐 Live Demo](#) • [📦 GitHub Repository](#) • [📄 Research-Inspired](https://arxiv.org/abs/2003.06158)

<br>

## Overview

**PNGProtect** is a security-focused image protection tool that embeds **invisible watermarks** into PNG images and verifies ownership using **perceptual hashing** techniques. The watermark survives common image transformations while remaining visually imperceptible.

Unlike visible watermarks that degrade aesthetics, PNGProtect ensures **silent attribution** and **tamper detection** without affecting image quality.

<br>

## Core Principles

- **Invisible by Design**  
  Watermarks are embedded in the frequency domain and are not visible to the human eye.

- **Resilient Protection**  
  Designed to survive compression, resizing, minor edits, and format-preserving transformations.

- **Ownership Verification**  
  Detects whether an image has been modified or reused using perceptual hash comparison.

- **Lightweight & Developer-Friendly**  
  Simple CLI / script-based workflow with minimal dependencies.

<br>

## Features

### 1. Invisible Watermark Embedding
- Embeds a unique signature into PNG images
- Does not affect visual quality
- Resistant to:
  - Resizing
  - Minor cropping
  - Compression artifacts

### 2. Watermark Extraction & Verification
- Extracts embedded watermark from protected images
- Confirms whether an image belongs to the original owner
- Detects tampering attempts

### 3. Perceptual Hashing (pHash)
- Generates perceptual hashes for images
- Identifies visually similar or modified copies
- Useful for duplicate and infringement detection

### 4. Integrity Validation
- Compares original and modified images
- Flags unauthorized edits or distribution
- Supports forensic-style analysis workflows

<br>

## Usage Guide

### Step 1 — Embed Watermark
```bash
python embed.py --input image.png --output protected.png --key "your_secret_key"
```

### Step 2 - Verify Image
```bash
python verify.py --input protected.png --key "your_secret_key"
```

### Step 3 - Similarity Check
```bash
python phash_compare.py image1.png image2.png
```

## 🔧 API Endpoints

- **Authentication**: `/auth/login`, `/auth/register`, `/auth/me`
- **Watermarking**: `/watermark/embed`, `/watermark/{id}`
- **Verification**: `/verify/detect`, `/verify/extract`
- **Dashboard**: `/dashboard/stats`, `/dashboard/analytics`
- **Metadata**: `/metadata/strip`
- **Blockchain Registry**: `/registry/abi` (smart contract integration)

## � Blockchain Features

### Wallet Integration
- **MetaMask Connection** - Seamless wallet linking
- **Account Management** - Automatic account switching detection
- **Network Support** - Ethereum mainnet and testnets

### On-Chain Registration
- **Ownership Registry** - Register watermark ownership on blockchain
- **Smart Contract** - Ethereum-based ownership verification
- **Immutable Records** - Permanent ownership proof

### Usage Flow
1. **Watermark** your image using the invisible watermarking system
2. **Verify** the watermark is properly embedded
3. **Connect Wallet** using MetaMask
4. **Register Ownership** on-chain for permanent proof

## 🎨 Tech Stack

- **Backend**: FastAPI, SQLite, Python
- **Frontend**: Vanilla JavaScript, CSS Grid, HTML5
- **Authentication**: JWT-like tokens, password hashing
- **Blockchain**: ethers.js, MetaMask integration, Solidity smart contracts
- **Styling**: Glassmorphism design, responsive layout

## 🔒 Security Features

- **Password Hashing** with SHA-256
- **Session Management** with secure tokens
- **CORS Protection** properly configured
- **Input Validation** on all endpoints
- **Blockchain Security** - Immutable ownership records

## 📝 License

## Architecture
        ┌──────────── Input PNG ─────────────┐
                        │
               ┌────────▼────────┐
               │ Watermark Engine│  ◄─ Frequency-domain embedding
               └────────┬────────┘
                        │
               ┌────────▼────────┐
               │ PNG Encoder     │
               └────────┬────────┘
                        │
               ┌────────▼────────┐
               │ pHash Generator │ ◄─ Visual similarity detection
               └────────┬────────┘
                        │
               ┌────────▼────────┐
               │ Verification    │ ◄─ Ownership & tamper check
               └─────────────────┘

## Tech Stack
| Layer        | Tools / Libraries           |
| ------------ | --------------------------- |
| Language     | Python                      |
| Image Ops    | Pillow, OpenCV              |
| Watermarking | Frequency-domain algorithms |
| Hashing      | pHash (Perceptual Hashing)  |
| Utilities    | NumPy, argparse             |

## Security Considerations
- Invisible Watermarks
Embedded at a signal-processing level, not pixel overlays.

- Tamper Detection
Any destructive modification alters the watermark or perceptual hash.

- False Positive Resistance
Threshold-based pHash comparison avoids accidental matches.

- Offline & Private
No external servers, APIs, or cloud dependencies.

## Folder Structure
```bash
.
├── embed.py              # Watermark embedding logic
├── verify.py             # Watermark extraction & verification
├── phash_compare.py      # Perceptual hash comparison
├── utils/                # Helper functions
├── samples/              # Test images
└── README.md
```

## Use Cases
- 🎨 Digital artists protecting original artwork

- 📸 Photographers tracking image reuse

- 🧑‍💻 Developers building DRM or content verification tools

- 🧪 Academic research on image watermarking

- 🛡️ Copyright and IP protection workflows

 ## Limitations
 - Extremely aggressive cropping may reduce watermark recoverability
 - Not designed to resist full re-drawing or AI regeneration
 - PNG-focused (JPEG support may be added later)

 ## Roadmap
  - JPEG support

  - Batch processing

  - GUI interface

  - Stronger multi-key watermarking

  - Web-based verification demo

 ## Refrences
   - Invisible Watermarking Survey
   - pHash–Perceptual Hashing
   - [Digital Image Watermarking – Cox et al.]

 ## License
 MIT License © 2026
 
 Built with ❤️ for creators and open-source contributors.
 
