# SAFE Ransomware Simulator (Cross-Platform: Windows + Linux)

This is a **harmless, reversible simulation** of ransomware.
It runs on both **Windows** and **Linux (including Kali)** with Python 3.10+.

<img width="1920" height="1080" alt="ransom" src="https://github.com/user-attachments/assets/07a40a4e-acc6-4262-9912-15e3bfd9e845" />

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
1. Clone the repo from the command and move to intented path.
   ```bash
   git clone https://github.com/binaryguardia/college-content.git
   cd college-content/Case-Study/Ransomware-sim
   ```
2. Install Python 3.10+ and Tkinter if missing:
   ```bash
   sudo apt update && sudo apt install -y python3-tk
   ```
3. Run:
   ```bash
   python3 ransomware_sim.py
   ```
4. In GUI, select your demo directory (e.g., `~/demo_vault`).
5. Click **Simulate Encrypt** → ransom note & GUI appears.
6. Enter unlock code to decrypt and restore.

## Usage (Windows)
Same as Linux, except you can also enable registry simulation for extra Sysmon telemetry.

### You can see the tutorial from here. 
https://youtu.be/FhoPieAxu58

## Safety Notes
- Always point simulator at a throwaway demo folder, never `/` or `C:\`.
- This is a **training/educational tool only**, not real ransomware.
- Reversible by design; unlock code shown in console and GUI title bar.
