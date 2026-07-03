# SpyNetScan

A local network IP and Port scanner (Port Scanner) built in Python/Flet, designed for Android and Desktop (Linux).

---

## 🚀 Features
- **Auto-Discovery of Local IP & Subnet**: Automatically detects the active IP of your device and suggests the matching CIDR subnet (e.g. `192.168.1.0/24`).
- **High-Speed Concurrent Scanning**: Uses Python `threading` and `asyncio` for concurrent Ping tests (ICMP) and port connection probes (TCP).
- **Customizable Ports (Port Scanning)**: Support for custom port lists (e.g., `22,80,443,3389,8080`) or leave blank to scan the most common network services.
- **Bilingual Interface**: Seamless, instant switching between English and Greek at the click of a button.
- **Responsive Toolbar Layout**: Mobile-first design that hides input settings during active scans and utilizes Material 3 tabs to maximize results display area.
- **Report Export**: Easily copy the results to clipboard or export to a local JSON report file.
- **Notch / Status Bar Safety**: Dynamic safe-area padding on Android to prevent UI elements from overlapping with status bar icons or front camera notch overlays.

