# FIRDHAN AGENT — AI + Full Windows Assistant 2026

Asisten desktop berbasis **Python/Tkinter** dengan tema cyberpunk (hijau-hacker). Satu file, tanpa dependensi wajib — semua fitur inti berjalan dengan standar library Python. Terhubung ke **OpenRouter** untuk chat AI gratis (rotasi model otomatis), dan bisa **mengendalikan penuh Windows**: buka aplikasi, atur volume/kecerahan, WiFi, power, webcam, screenshot, sampai **menanamkan (embed) jendela aplikasi asli** ke dalam grid multi-tasking.

---

## ✦ Fitur Utama

### 1. AI Assistant (OpenRouter)
- Chat natural language, riwayat tersimpan otomatis (100 pesan terakhir) di `~/.firdhan_agent/chat_history.json`.
- **Rotasi otomatis** API key + model gratis — key 401 di-blacklist, model 403/404/400 di-blacklist, retry sampai 14x.
- Daftar model gratis di-fetch live dari OpenRouter (cache 24 jam) dengan fallback bawaan.
- **Persona editor** + system prompt custom di menu *AI CONFIG*.
- Perintah sistem diteruskan ke Command Engine, lalu AI diberi tahu hasilnya.

### 2. Command Engine (Kontrol Penuh Windows)
| Kategori | Contoh perintah |
|---|---|
| Buka aplikasi | `buka chrome`, `buka vscode`, `buka word`, `buka notepad` (60+ aplikasi terpetakan) |
| File & folder | `buka file D:\\data\\laporan.xlsx`, `buka folder C:\\Projects` |
| Power | `matikan laptop`, `restart`, `sleep`, `hibernate`, `lock`, `logoff` (dengan konfirmasi) |
| Multimedia | `volume 50`, `mute`, `unmute`, `kecerahan 70` |
| Jaringan | `wifi`, `wifi connect ke NamaSSID`, `wifi disconnect`, `ip address` |
| Sistem | `battery`, `tasklist`, `kill notepad`, `kosongkan recycle bin`, `eject E:` |
| Tangkap | `webcam`, `screenshot`, `clipboard` |
| Lainnya | `wsl` (buka cmd langsung masuk WSL home), `jalankan python script.py`, waktu/jam |

### 3. Multi Tasking — App Grid (Embed Engine v3.0)
- Grid 1–8 slot. Setiap slot bisa menampung **jendela aplikasi asli** (bukan screenshot/simulasi) yang di-embed via Win32 `SetParent` + `ctypes` — tanpa dependensi `pywin32`.
- Pilih aplikasi dari dropdown **scrollable + filter** (terdeteksi otomatis dari Start Menu).
- **Klik area slot = langsung fokus** → bisa ngetik & operasikan aplikasi (Notepad, Paint, Chrome, VS Code, dll.) di dalam grid.
- Jendela ikut menyusut/membesar saat slot di-resize (FILL guard berjalan tiap 600 ms).
- Tombol layout **1/2/3/4/6/8** — 1 slot = praktis fullscreen; slot yang disembunyikan dilepas ke desktop (aplikasi **tetap hidup**) dan di-embed ulang otomatis saat ditampilkan lagi.
- Satu slot bisa jadi **Kamera depan** (webcam live).

### 4. Catatan Teknis Embed Console (CMD/PowerShell/WSL)
Console app dilaunch pakai `CREATE_NEW_CONSOLE` dengan judul unik **`FIRDHAN_DEADLINE_XX`** per slot, lalu dideteksi by-title (`find_window_by_title`) — deterministik, tidak tertukar dengan jendela lain. Filter deteksi window hanya melewatkan judul yang diawali `FIRDHAN AGENT` (jendela utama app), sehingga nama `FIRDHAN_DEADLINE_XX` aman dipakai.

---

## ✦ Instalasi

**Requirement:** Windows 10/11 + Python 3.8+.

```bat
:: Dependensi opsional (semua fitur tetap jalan tanpa ini, hanya fitur terkait yang nonaktif)
pip install opencv-python Pillow psutil pyautogui pywin32

:: Jalankan
python firdhan_agent.py
```

| Dependensi opsional | Yang diaktifkan jika ada |
|---|---|
| `opencv-python` | Webcam viewer & slot kamera |
| `Pillow` | Screenshot |
| `psutil` | Status baterai real-time |
| `pyautogui` | Kontrol input lanjutan |

---

## ✦ Struktur Konfigurasi

Semua tersimpan di `%USERPROFILE%\.firdhan_agent\`:

| File | Isi |
|---|---|
| `config.json` | API key, model, system prompt, persona |
| `chat_history.json` | Riwayat chat (maks 100 pesan) |
| `free_models.json` | Cache daftar model gratis OpenRouter (24 jam) |

---

## ✦ Penggunaan

- **ASSISTANT** — chat AI. Ketik perintah Windows biasa (`buka chrome`, `volume 50`, ...) dan akan dieksekusi langsung, atau tanya apa saja ke AI.
- **SYSTEM** — terminal perintah langsung ke Command Engine.
- **AI CONFIG** — atur API key, pilih model, edit system prompt & persona.
- **MULTI TASKING** — grid embed aplikasi. `BUKA SEMUA` menjalankan semua slot berurutan, `REFRESH APPS` memindai ulang aplikasi terinstall.

---

## ✦ Peringatan Keamanan

- Source code berisi daftar API key OpenRouter dalam plaintext. **Jangan bagikan file ini ke publik** — setiap orang yang memegang file bisa memakai key tersebut. Untuk produksi, pindahkan key ke environment variable atau file konfigurasi terpisah.
- Perintah power (`shutdown`, `restart`, dll.) selalu memunculkan dialog konfirmasi.
- Fitur `kill`, `eject`, dan `kosongkan recycle bin` bersifat destruktif — gunakan dengan hati-hati.

---

## ✦ Troubleshooting

| Masalah | Solusi |
|---|---|
| CMD masih "WINDOW TIDUTUP" / tidak masuk kotak | Pastikan menjalankan versi terbaru; console butuh `CREATE_NEW_CONSOLE` + judul `FIRDHAN_DEADLINE_XX`. Jangan ubah filter deteksi window. |
| AI error "semua percobaan gagal" | Koneksi internet, semua key limit, atau semua model gratis sedang down. Tunggu rate-limit reset atau ganti key di AI CONFIG. |
| Webcam/screenshot error | Install dependensi opsional (lihat tabel Instalasi). |
| Model sering di-blacklist | Normal — model gratis OpenRouter sering berubah; daftar di-refresh otomatis tiap 24 jam. |

---

*FIRDHAN AGENT // SYSTEM ONLINE — dibuat untuk mengendalikan Windows dari satu jendela.*
