# SAFE Ransomware Simulator (Cross-Platform: Windows + Linux)

This is a **harmless, reversible simulation** of ransomware behavior for educational demos.
It runs on both **Windows** and **Linux (including Kali)** with Python 3.10+.

## Features
- Choose a **Demo Directory** — simulator will only operate there (never touches system dirs).
- Encrypts files using reversible XOR stream, renames with `.locked`.
- Creates a ransom-note style file `README_DECRYPT.txt`.
- Full-screen ransom GUI (press Ctrl+Shift+Q to exit at any time).
- Enter unlock code to restore files.
- Generates benign telemetry:
  - File modifications (Sysmon on Windows, `inotify`/auditd on Linux).
  - Harmless HTTP requests to `http://example.com`.
  - Optional registry write (Windows only; skipped on Linux).

## Usage (Linux / Kali)
1. Install Python 3.10+ and Tkinter if missing:
   ```bash
   sudo apt update && sudo apt install -y python3-tk
   ```
2. Run:
   ```bash
   python3 ransomware_sim.py
   ```
3. In GUI, select your demo directory (e.g., `~/demo_vault`).
4. Click **Simulate Encrypt** → ransom note & GUI appears.
5. Enter unlock code to decrypt and restore.

## Usage (Windows)
Same as Linux, except you can also enable registry simulation for extra Sysmon telemetry.

## Safety Notes
- Always point simulator at a throwaway demo folder, never `/` or `C:\`.
- This is a **training/educational tool only**, not real ransomware.
- Reversible by design; unlock code shown in console and GUI title bar.
