# 📄 PDF Direct In-Place Text Editor

A tool and visual web application designed to edit text directly on PDF files while preserving the **exact font family, size, baseline alignment, and color** — optimized for both **Desktop and Mobile devices**.

---

## 🌟 Key Features

- **Exact Typography Matching**: Automatically detects font family, point size, baseline coordinate, and color (`#RRGGBB`).
- **Bundled Fonts**: Includes the official Google `Roboto` font family (`Roboto-Bold`, `Roboto-Medium`, `Roboto-Regular`, `Roboto-Black`, `Roboto-Light`) for airline tickets and modern documents, plus full Windows system font matching (Arial, Calibri, Times New Roman, Segoe UI, etc.).
- **🛡️ PDF Health & Fidelity Audit**: Automatically checks the health and similarity of your edited PDF against the original. Calculates a live fidelity score (e.g. 100% Pristine), verifies zero ghost text leaks, checks font vector embedding, and flags excessive scaling.
- **👁️ "Compare / Peek Original" Mode**: Hold or click the `👁️ Compare` button (or hold the `O` key) to instantaneously toggle between the original and edited document for pixel-perfect comparison.
- **📡 Deep Typography Scanning HUD**: When uploading, scans all vector paths, text spans, and font families with an animated progress radar.
- **📝 Live Modifications Diff**: View all changes side-by-side with original vs edited text and a `[ 🎯 Focus ]` button to highlight edits directly on the canvas.
- **Step-by-Step Undo**: Click the `↩ Undo` button (or press `Ctrl+Z` / `Cmd+Z`) to revert the previous edit one step back.
- **Cancel / Clear Selection**: A dedicated `✕ Cancel` button lets you discard the current edit and view the full document without applying changes.
- **Custom File Naming**: When clicking "Download", a naming dialog lets you choose and preview your custom filename before saving.
- **Mobile Optimized**:
  - **📱 Phone Connectivity**: Access the editor directly from your smartphone over local Wi-Fi.
  - **QR Code Sharing**: Click "Phone Link" on the desktop header to scan a QR code with your phone camera and open the app instantly.
  - **Slide-up Bottom Sheet (Drawer)**: On mobile screens, tapping any text smoothly slides up an app-style bottom inspector with large, tap-friendly buttons.
  - **Touch Hitbox Expansion**: Small PDF lines are easy to tap with fingers without missing.
  - **Pinch & Floating Zoom**: Zoom in/out to view fine details on smaller mobile screens.
- **Two Flexible Modes**:
  1. **Visual Web UI** (Desktop & Mobile browser)
  2. **Command-Line (CLI)** for scripts and automation

---

## 🚀 Quick Start

### 1. Launch the Web UI

```bash
python web_editor.py
```

Then open:
- **On your PC**: [http://127.0.0.1:5000](http://127.0.0.1:5000)
- **On your Mobile** (connected to the same Wi-Fi): `http://<your-local-ip>:5000` (or click **📱 Phone Link** on the desktop web header to scan the QR code).

---

### 2. Command-Line (CLI)

```bash
# Inspect PDF text & typography
python pdf_editor.py inspect input.pdf

# In-place find and replace
python pdf_editor.py replace input.pdf --find "BOM" --replace "BOB" -o output.pdf
```
