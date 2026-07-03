import flet as ft
import threading
import time
import os
import json
from pathlib import Path
import scanner

VERSION = "1.1.4"

# Localization strings
TRANSLATIONS = {
    "en": {
        "desc": "Network IP & Port Scanner",
        "net_info": "Network Adapter Info",
        "local_ip": "Local IP: ",
        "detected_subnet": "Subnet: ",
        "use_subnet_tooltip": "Use subnet range",
        "scan_settings": "Scan Settings",
        "start_ip_label": "From IP",
        "start_ip_hint": "e.g. 192.168.1.1",
        "end_ip_label": "To IP",
        "end_ip_hint": "e.g. 192.168.1.254",
        "ports_label": "Ports to Scan",
        "ports_hint": "e.g. 80,443 or blank",
        "scan_mode": "Mode:",
        "mode_ping": "Ping",
        "mode_port": "Ports",
        "mode_full": "Full",
        "timeout": "Timeout (s):",
        "slider_label": "{}s",
        "btn_start": "Start Scan",
        "btn_cancel": "Cancel",
        "status_idle": "Status: Idle",
        "status_init": "Status: Initializing scan for {} hosts...",
        "status_scanning": "Scanning ({}/{}): {}",
        "status_cancelled": "Status: Scan cancelled. Found {} active devices.",
        "status_completed": "Status: Scan completed in {:.1f}s. Found {} active devices.",
        "snack_finished": "Scan finished! Discovered {} active devices.",
        "snack_cancelled": "Scan cancelled by user.",
        "snack_invalid_ip": "Invalid IP Range or Subnet format!",
        "discovered_title": "Discovered Devices ({})",
        "filter_label": "Filter devices",
        "filter_hint": "Type IP or Hostname to filter...",
        "export_tooltip": "Export Report",
        "no_ports": "No open ports detected",
        "hostname": "Hostname:",
        "open_ports": "Open Ports:",
        "snack_export": "Report copied to clipboard!{}",
        "save_success": "\nReport saved to: {}",
        "save_fail": "\nCould not write file: {}",
        "use_subnet_snack": "Set IP range to: {}",
        "about_title": "About SpyNetScan",
        "about_content": "SpyNetScan v{}\n\nA modern, fast, concurrent local network scanner.\n\nHow to use:\n• The 'Local IP' section shows your interface details. Use the copy button to set the target range.\n• 'From IP' / 'To IP': Enter the IP range boundaries. If you leave 'To IP' blank, you can enter a CIDR subnet (like 192.168.1.0/24) in the first field.\n• 'Ports to Scan': Specify TCP ports (e.g. 22,80,443) or leave blank for all common ports.\n• 'Scan Mode': Choose Ping (ICMP sweep), Ports (TCP socket sweeps), or Full (both).\n• 'Timeout': Drag to adjust connection time limits.\n\nResults:\n• Live list updates showing active hosts, latency (RTT), hostnames, and discovered open ports.\n• Filter results instantaneously via the search bar.\n• Export reports to clipboard or local JSON file.",
        "about_close": "Close",
        "about_tooltip": "Help & Info",
        "tab_scan": "Scan Settings",
        "tab_results": "Results",
        "about_creator": "Creator: "
    },
    "el": {
        "desc": "Ανιχνευτής IP & Θυρών Δικτύου",
        "net_info": "Πληροφορίες Προσαρμογέα Δικτύου",
        "local_ip": "Τοπική IP: ",
        "detected_subnet": "Υποδίκτυο: ",
        "use_subnet_tooltip": "Χρήση εύρους υποδικτύου",
        "scan_settings": "Ρυθμίσεις Σάρωσης",
        "start_ip_label": "Από IP",
        "start_ip_hint": "π.χ. 192.168.1.1",
        "end_ip_label": "Έως IP",
        "end_ip_hint": "π.χ. 192.168.1.254",
        "ports_label": "Θύρες για Σάρωση",
        "ports_hint": "π.χ. 80,443 ή κενό",
        "scan_mode": "Λειτουργία:",
        "mode_ping": "Ping",
        "mode_port": "Θύρες",
        "mode_full": "Πλήρης",
        "timeout": "Όριο (s):",
        "slider_label": "όριο {}s",
        "btn_start": "Έναρξη Σάρωσης",
        "btn_cancel": "Ακύρωση",
        "status_idle": "Κατάσταση: Αδρανής",
        "status_init": "Κατάσταση: Προετοιμασία σάρωσης για {} συσκευές...",
        "status_scanning": "Σάρωση ({}/{}): {}",
        "status_cancelled": "Κατάσταση: Η σάρωση ακυρώθηκε. Βρέθηκαν {} ενεργές συσκευές.",
        "status_completed": "Κατάσταση: Η σάρωση ολοκληρώθηκε σε {:.1f}s. Βρέθηκαν {} ενεργές συσκευές.",
        "snack_finished": "Η σάρωση τελείωσε! Ανακαλύφθηκαν {} ενεργές συσκευές.",
        "snack_cancelled": "Η σάρωση ακυρώθηκε από τον χρήστη.",
        "snack_invalid_ip": "Μη έγκυρη μορφή εύρους IP ή υποδικτύου!",
        "discovered_title": "Εντοπισμένες Συσκευές ({})",
        "filter_label": "Φιλτράρισμα συσκευών",
        "filter_hint": "Πληκτρολογήστε IP ή Όνομα για φιλτράρισμα...",
        "export_tooltip": "Εξαγωγή Αναφοράς",
        "no_ports": "Δεν εντοπίστηκαν ανοιχτές θύρες",
        "hostname": "Όνομα Συσκευής:",
        "open_ports": "Ανοιχτές Θύρες:",
        "snack_export": "Η αναφορά αντιγράφηκε στο πρόχειρο!{}",
        "save_success": "\nΗ αναφορά αποθηκεύτηκε στο: {}",
        "save_fail": "\nΑδυναμία εγγραφής αρχείου: {}",
        "use_subnet_snack": "Το εύρος IP ορίστηκε σε: {}",
        "about_title": "Σχετικά με το SpyNetScan",
        "about_content": "SpyNetScan v{}\n\nΈνας σύγχρονος, γρήγορος και παράλληλος ανιχνευτής τοπικού δικτύου.\n\nΟδηγίες Χρήσης:\n• Η ενότητα 'Τοπική IP' δείχνει τις λεπτομέρειες του προσαρμογέα σας. Πατήστε το κουμπί αντιγραφής για αυτόματη συμπλήρωση.\n• 'Από IP' / 'Έως IP': Ορίστε τα όρια σάρωσης. Αν το 'Έως IP' μείνει κενό, μπορείτε να εισάγετε ένα υποδίκτυο CIDR (π.χ. 192.168.1.0/24) στο πρώτο πεδίο.\n• 'Θύρες για Σάρωση': Ορίστε TCP θύρες (π.χ. 80,443) ή αφήστε κενό για τις πιο δημοφιλείς.\n• 'Λειτουργία': Επιλέξτε Ping (σάρωση ICMP), Θύρες (σάρωση TCP), ή Πλήρη (συνδυασμό και των δύο).\n• 'Όριο': Σύρετε για να ρυθμίσετε την καθυστέρηση (timeout) ανά δοκιμή.\n\nΑποτελέσματα:\n• Ζωντανή εμφάνιση ενεργών συσκευών, latency (RTT), hostname και ανοιχτών θυρών.\n• Φιλτράρισμα αποτελεσμάτων σε πραγματικό χρόνο από το πεδίο αναζήτησης.\n• Εξαγωγή αναφοράς στο πρόχειρο ή σε τοπικό αρχείο JSON.",
        "about_close": "Κλείσιμο",
        "about_tooltip": "Βοήθεια & Πληροφορίες",
        "tab_scan": "Ρυθμίσεις",
        "tab_results": "Αποτελέσματα",
        "about_creator": "Δημιουργός: "
    }
}

class SpyNetScanApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.lang = "en"  # Default language
        self.scanner_backend = scanner.NetworkScanner()
        self.discovered_hosts = []  # List of discovered host dicts
        self.all_ips_to_scan = []
        self.scan_thread = None
        
        # UI controls references
        self.header_subtitle = None
        self.lang_btn = None
        self.about_btn = None
        
        self.local_ip_lbl = None
        self.detected_subnet_lbl = None
        self.use_subnet_btn = None
        
        self.start_ip_input = None
        self.end_ip_input = None
        self.ports_input = None
        self.scan_mode_title = None
        self.scan_mode_radio = None
        self.radio_ping = None
        self.radio_port = None
        self.radio_full = None
        self.timeout_title = None
        self.timeout_input = None
        
        self.start_btn = None
        self.cancel_btn = None
        
        self.progress_bar = None
        self.status_text = None
        self.results_title = None
        self.results_list = None
        self.search_filter = None
        self.export_btn = None
        
        # Auto-discovered local info
        self.local_ip = scanner.get_local_ip()
        self.suggested_subnet = scanner.get_suggested_subnet(self.local_ip)
        
        # Guessed start/end default IPs
        try:
            parts = self.local_ip.split('.')
            if len(parts) == 4:
                self.default_start_ip = f"{parts[0]}.{parts[1]}.{parts[2]}.1"
                self.default_end_ip = f"{parts[0]}.{parts[1]}.{parts[2]}.254"
            else:
                self.default_start_ip = "192.168.1.1"
                self.default_end_ip = "192.168.1.254"
        except Exception:
            self.default_start_ip = "192.168.1.1"
            self.default_end_ip = "192.168.1.254"
            
        # Non-deprecated Clipboard service mounting
        self.clipboard = ft.Clipboard()
        page.services.append(self.clipboard)
        
        # Load persisted settings
        self.load_settings()

    def get_settings_filepath(self) -> Path:
        try:
            out_dir = Path.home() / "spynetscan_files"
            out_dir.mkdir(parents=True, exist_ok=True)
            return out_dir / "settings.json"
        except Exception:
            return Path(".") / "settings.json"

    def load_settings(self):
        filepath = self.get_settings_filepath()
        if filepath.exists():
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.lang = data.get("lang", "en")
                    if self.lang not in ["en", "el"]:
                        self.lang = "en"
                    self.saved_start_ip = data.get("start_ip", self.default_start_ip)
                    self.saved_end_ip = data.get("end_ip", self.default_end_ip)
                    self.saved_ports = data.get("ports", "22,80,443,3389,8080")
                    self.saved_scan_mode = data.get("scan_mode", "full")
                    self.saved_timeout = float(data.get("timeout", 1.0))
                    return
            except Exception:
                pass
        # Defaults
        self.lang = "en"
        self.saved_start_ip = self.default_start_ip
        self.saved_end_ip = self.default_end_ip
        self.saved_ports = "22,80,443,3389,8080"
        self.saved_scan_mode = "full"
        self.saved_timeout = 1.0
    @property
    def is_mobile(self) -> bool:
        if not self.page or not self.page.platform:
            return False
        # Platform check
        plat = str(self.page.platform).lower()
        return "android" in plat or "ios" in plat

    def save_settings(self):
        try:
            filepath = self.get_settings_filepath()
            data = {
                "lang": self.lang,
                "start_ip": self.start_ip_input.value,
                "end_ip": self.end_ip_input.value,
                "ports": self.ports_input.value,
                "scan_mode": self.scan_mode_radio.value,
                "timeout": self.timeout_input.value,
            }
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def t(self, key: str, *args) -> str:
        """Helper to get translated text with formatting."""
        template = TRANSLATIONS[self.lang].get(key, key)
        if args:
            return template.format(*args)
        return template

    def build(self):
        is_mobile = self.is_mobile

        # 1. Header with Title & Action Buttons (Shortened on mobile to fit screen safely)
        subtitle_text = f"v{VERSION}" if is_mobile else f"v{VERSION} - {self.t('desc')}"
        self.header_subtitle = ft.Text(subtitle_text, size=11 if is_mobile else 12, color=ft.Colors.GREY_400)
        
        self.lang_btn = ft.IconButton(
            icon=ft.Icons.TRANSLATE if self.lang == "en" else ft.Icons.LANGUAGE,
            tooltip="Ελληνικά" if self.lang == "en" else "English",
            icon_color=ft.Colors.GREEN_ACCENT_400,
            icon_size=20,
            on_click=self.toggle_language
        )
        
        self.about_btn = ft.IconButton(
            icon=ft.Icons.INFO_OUTLINE,
            tooltip=self.t("about_tooltip"),
            icon_color=ft.Colors.GREEN_ACCENT_400,
            icon_size=20,
            on_click=self.show_about_dialog
        )
        
        header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Icon(icon=ft.Icons.RADAR, color=ft.Colors.GREEN_ACCENT_400, size=28),
                            ft.Column(
                                controls=[
                                    ft.Text("SpyNetScan", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                    self.header_subtitle,
                                ],
                                spacing=0,
                            ),
                        ],
                        spacing=8,
                    ),
                    ft.Row(
                        controls=[
                            self.lang_btn,
                            self.about_btn,
                        ],
                        spacing=4,
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.Padding.only(left=5, right=10, bottom=5),
            border=ft.Border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_800)),
        )

        is_mobile = self.is_mobile

        # 2. Local Info Row (Ultra Slim Toolbar / Responsive)
        self.local_ip_lbl = ft.Text(self.t("local_ip"), color=ft.Colors.GREY_400, size=11)
        self.detected_subnet_lbl = ft.Text(self.t("detected_subnet"), color=ft.Colors.GREY_400, size=11)
        
        self.use_subnet_btn = ft.IconButton(
            icon=ft.Icons.COPY,
            icon_size=12,
            tooltip=self.t("use_subnet_tooltip"),
            icon_color=ft.Colors.GREY_400,
            width=24,
            height=24,
            padding=0,
            on_click=self.use_detected_subnet,
        )

        local_info_content = [
            ft.Row(
                controls=[
                    ft.Icon(icon=ft.Icons.NETWORK_CHECK, color=ft.Colors.CYAN_400, size=14),
                    self.local_ip_lbl,
                    ft.Text(self.local_ip, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD, size=11),
                ],
                spacing=4,
            ),
            ft.Row(
                controls=[
                    ft.Icon(icon=ft.Icons.SETTINGS_ETHERNET, color=ft.Colors.CYAN_400, size=14),
                    self.detected_subnet_lbl,
                    ft.Text(self.suggested_subnet, color=ft.Colors.CYAN_300, weight=ft.FontWeight.BOLD, size=11),
                    self.use_subnet_btn
                ],
                spacing=4,
            )
        ]

        local_info_row = ft.Container(
            content=ft.Column(controls=local_info_content, spacing=4) if is_mobile else ft.Row(
                controls=local_info_content,
                alignment=ft.MainAxisAlignment.START,
                spacing=20,
            ),
            padding=ft.Padding.symmetric(vertical=2, horizontal=5),
        )

        # 3. Compact Scan Settings Form
        self.start_ip_input = ft.TextField(
            label=self.t("start_ip_label"),
            value=self.saved_start_ip,
            hint_text=self.t("start_ip_hint"),
            border_color=ft.Colors.GREY_700,
            focused_border_color=ft.Colors.GREEN_ACCENT_400,
            text_size=11,
            height=36,
            content_padding=ft.Padding.symmetric(vertical=2, horizontal=8),
            expand=True if is_mobile else 3,
        )

        self.end_ip_input = ft.TextField(
            label=self.t("end_ip_label"),
            value=self.saved_end_ip,
            hint_text=self.t("end_ip_hint"),
            border_color=ft.Colors.GREY_700,
            focused_border_color=ft.Colors.GREEN_ACCENT_400,
            text_size=11,
            height=36,
            content_padding=ft.Padding.symmetric(vertical=2, horizontal=8),
            expand=True if is_mobile else 3,
        )

        self.ports_input = ft.TextField(
            label=self.t("ports_label"),
            value=self.saved_ports,
            hint_text=self.t("ports_hint"),
            border_color=ft.Colors.GREY_700,
            focused_border_color=ft.Colors.GREEN_ACCENT_400,
            text_size=11,
            height=36,
            content_padding=ft.Padding.symmetric(vertical=2, horizontal=8),
            expand=True if is_mobile else 3,
        )

        self.timeout_title = ft.Text(self.t("timeout"), size=10, color=ft.Colors.GREY_400)
        self.timeout_input = ft.Slider(
            min=0.2,
            max=3.0,
            divisions=14,
            value=self.saved_timeout,
            label=self.t("slider_label").replace("{}", "{value}"),
        )
        
        timeout_column = ft.Column(
            controls=[
                self.timeout_title,
                self.timeout_input,
            ],
            spacing=0,
            alignment=ft.MainAxisAlignment.CENTER,
            expand=True if is_mobile else 3,
        )

        # Mode Selection & Action Buttons
        self.radio_ping = ft.Radio(value="ping", label=self.t("mode_ping"))
        self.radio_port = ft.Radio(value="port_probe", label=self.t("mode_port"))
        self.radio_full = ft.Radio(value="full", label=self.t("mode_full"))

        self.scan_mode_radio = ft.RadioGroup(
            content=ft.Row(
                controls=[
                    self.radio_ping,
                    self.radio_port,
                    self.radio_full,
                ],
                spacing=10,
            ),
            value=self.saved_scan_mode,
        )

        self.scan_mode_title = ft.Text(self.t("scan_mode"), size=11, color=ft.Colors.GREY_400)
        
        mode_select_row = ft.Row(
            controls=[
                self.scan_mode_title,
                self.scan_mode_radio,
            ],
            spacing=5,
        )

        self.start_btn_text = ft.Text(self.t("btn_start"), color=ft.Colors.BLACK, weight=ft.FontWeight.BOLD)
        self.start_btn = ft.Button(
            content=self.start_btn_text,
            icon=ft.Icons.PLAY_ARROW,
            color=ft.Colors.BLACK,
            bgcolor=ft.Colors.GREEN_ACCENT_400,
            height=32,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=4),
            ),
            expand=True if is_mobile else False,
            on_click=self.start_scan,
        )

        self.cancel_btn_text = ft.Text(self.t("btn_cancel"), color=ft.Colors.WHITE)
        self.cancel_btn = ft.Button(
            content=self.cancel_btn_text,
            icon=ft.Icons.STOP,
            color=ft.Colors.WHITE,
            bgcolor=ft.Colors.RED_ACCENT_700,
            height=32,
            style=ft.ButtonStyle(
                shape=ft.RoundedRectangleBorder(radius=4),
            ),
            disabled=True,
            expand=True if is_mobile else False,
            on_click=self.cancel_scan,
        )

        # Assemble settings layout depending on platform
        if is_mobile:
            self.ports_input.expand = False
            timeout_column.expand = False
            
            row_ips = ft.Row(controls=[self.start_ip_input, self.end_ip_input], spacing=10)
            row_mode = ft.Row(controls=[self.scan_mode_title, self.scan_mode_radio], spacing=5, wrap=True)
            row_actions = ft.Row(controls=[self.start_btn, self.cancel_btn], spacing=8)
            
            settings_layout = ft.Column(
                controls=[
                    local_info_row,
                    row_ips,
                    self.ports_input,
                    timeout_column,
                    row_mode,
                    row_actions,
                ],
                spacing=10,
            )
            self.settings_hide_on_scan = []
        else:
            settings_row_1 = ft.Row(
                controls=[
                    self.start_ip_input,
                    self.end_ip_input,
                    self.ports_input,
                    timeout_column,
                ],
                spacing=10,
            )
            settings_row_2 = ft.Row(
                controls=[
                    mode_select_row,
                    ft.Row(controls=[self.start_btn, self.cancel_btn], spacing=8),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            )
            settings_layout = ft.Column(
                controls=[
                    local_info_row,
                    settings_row_1,
                    settings_row_2,
                ],
                spacing=8,
            )
            self.settings_hide_on_scan = []

        # Pack all configuration in a thin layout
        config_container = ft.Container(
            content=settings_layout,
            padding=10 if is_mobile else 8,
            bgcolor=ft.Colors.BLUE_GREY_900,
            border_radius=8,
        )

        # 4. Progress Section
        self.progress_bar = ft.ProgressBar(value=0, visible=False, color=ft.Colors.GREEN_ACCENT_400, bgcolor=ft.Colors.GREY_800)
        self.status_text = ft.Text(self.t("status_idle"), size=11, italic=True, color=ft.Colors.GREY_400)

        # 5. Results Header & Filter
        self.results_title = ft.Text(self.t("discovered_title", 0), size=14, weight=ft.FontWeight.BOLD)
        
        self.search_filter = ft.TextField(
            label=self.t("filter_label"),
            hint_text=self.t("filter_hint"),
            prefix_icon=ft.Icons.SEARCH,
            border_color=ft.Colors.GREY_700,
            focused_border_color=ft.Colors.CYAN_400,
            text_size=11,
            height=34,
            content_padding=ft.Padding.symmetric(vertical=4, horizontal=10),
            on_change=self.apply_filter,
            expand=True,
        )

        self.export_btn = ft.IconButton(
            icon=ft.Icons.FILE_DOWNLOAD,
            tooltip=self.t("export_tooltip"),
            icon_color=ft.Colors.CYAN_400,
            disabled=True,
            on_click=self.export_results,
        )

        if is_mobile:
            results_header_row = ft.Column(
                controls=[
                    ft.Row(
                        controls=[self.results_title, self.export_btn],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    self.search_filter,
                ],
                spacing=6,
            )
        else:
            results_header_row = ft.Row(
                controls=[
                    self.results_title,
                    ft.Row(
                        controls=[
                            self.search_filter,
                            self.export_btn,
                        ],
                        expand=True,
                        alignment=ft.MainAxisAlignment.END,
                    )
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            )

        # Scrollable list for hosts
        self.results_list = ft.ListView(
            expand=True,
            spacing=8,
            padding=ft.Padding.only(top=2, bottom=10),
        )

        # Master layout container
        if is_mobile:
            self.tab_bar = ft.TabBar(
                tabs=[
                    ft.Tab(
                        label=self.t("tab_scan"),
                        icon=ft.Icons.SETTINGS,
                    ),
                    ft.Tab(
                        label=self.t("tab_results"),
                        icon=ft.Icons.LIST_ALT,
                    ),
                ]
            )
            self.tab_view = ft.TabBarView(
                expand=True,
                controls=[
                    ft.Container(
                        content=config_container,
                        padding=5,
                    ),
                    ft.Column(
                        controls=[
                            self.progress_bar,
                            self.status_text,
                            results_header_row,
                            self.results_list,
                        ],
                        spacing=10,
                        expand=True,
                    ),
                ],
            )
            self.tabs = ft.Tabs(
                selected_index=0,
                length=2,
                expand=True,
                content=ft.Column(
                    expand=True,
                    controls=[
                        self.tab_bar,
                        self.tab_view,
                    ],
                ),
            )
            content_controls = [
                header,
                self.tabs,
            ]
        else:
            content_controls = [
                header,
                config_container,
                ft.Column(
                    controls=[
                        self.progress_bar,
                        self.status_text,
                    ],
                    spacing=2,
                ),
                ft.Divider(height=1, color=ft.Colors.GREY_800),
                results_header_row,
                self.results_list,
            ]

        layout = ft.Container(
            content=ft.Column(
                controls=content_controls,
                spacing=8,
                expand=True,
            ),
            padding=ft.Padding(left=10, right=10, top=45, bottom=10) if is_mobile else 15,
            expand=True,
        )

        return layout

    def toggle_language(self, e):
        """Switches UI language instantly."""
        self.lang = "el" if self.lang == "en" else "en"
        
        # Toggle icon & tooltip
        self.lang_btn.icon = ft.Icons.TRANSLATE if self.lang == "en" else ft.Icons.LANGUAGE
        self.lang_btn.tooltip = "Ελληνικά" if self.lang == "en" else "English"
        self.about_btn.tooltip = self.t("about_tooltip")
        
        # Subtitle (Shortened on mobile to fit screen safely)
        is_mobile = self.is_mobile
        self.header_subtitle.value = f"v{VERSION}" if is_mobile else f"v{VERSION} - {self.t('desc')}"
        
        # Tabs on mobile
        if hasattr(self, "tab_bar"):
            self.tab_bar.tabs[0].label = self.t("tab_scan")
            self.tab_bar.tabs[1].label = self.t("tab_results")
            self.tab_bar.update()
        
        # Info row
        self.local_ip_lbl.value = self.t("local_ip")
        self.detected_subnet_lbl.value = self.t("detected_subnet")
        self.use_subnet_btn.tooltip = self.t("use_subnet_tooltip")
        
        # Settings Inputs
        self.start_ip_input.label = self.t("start_ip_label")
        self.start_ip_input.hint_text = self.t("start_ip_hint")
        self.end_ip_input.label = self.t("end_ip_label")
        self.end_ip_input.hint_text = self.t("end_ip_hint")
        self.ports_input.label = self.t("ports_label")
        self.ports_input.hint_text = self.t("ports_hint")
        self.scan_mode_title.value = self.t("scan_mode")
        self.radio_ping.label = self.t("mode_ping")
        self.radio_port.label = self.t("mode_port")
        self.radio_full.label = self.t("mode_full")
        self.timeout_title.value = self.t("timeout")
        self.timeout_input.label = self.t("slider_label").replace("{}", "{value}")
        
        # Buttons
        self.start_btn_text.value = self.t("btn_start")
        self.cancel_btn_text.value = self.t("btn_cancel")
        
        # Status
        if not self.scanner_backend.is_running:
            self.status_text.value = self.t("status_idle")
            
        # Filter & Export Tooltip
        self.search_filter.label = self.t("filter_label")
        self.search_filter.hint_text = self.t("filter_hint")
        self.export_btn.tooltip = self.t("export_tooltip")
        
        # Update results list labels
        self.refresh_results_ui()
        
        self.save_settings()
        self.page.update()

    def show_about_dialog(self, e):
        """Shows Help & About information dialog."""
        creator_row = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text(self.t("about_creator"), size=12),
                    ft.TextButton(
                        "spyalekos",
                        on_click=lambda e: self.page.launch_url("https://github.com/spyalekos"),
                        style=ft.ButtonStyle(padding=0),
                    )
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),
            margin=ft.margin.Margin(top=15),
        )
        dlg = ft.AlertDialog(
            title=ft.Text(self.t("about_title"), weight=ft.FontWeight.BOLD),
            content=ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Text(self.t("about_content", VERSION), size=13),
                        creator_row,
                    ],
                    scroll=ft.ScrollMode.AUTO,
                ),
                height=380,
                width=300,
            ),
            actions=[
                ft.TextButton(
                    self.t("about_close"),
                    on_click=lambda e: self.page.pop_dialog()
                )
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        self.page.show_dialog(dlg)
        self.page.update()

    def use_detected_subnet(self, e):
        try:
            parts = self.local_ip.split('.')
            if len(parts) == 4:
                start_ip = f"{parts[0]}.{parts[1]}.{parts[2]}.1"
                end_ip = f"{parts[0]}.{parts[1]}.{parts[2]}.254"
                self.start_ip_input.value = start_ip
                self.end_ip_input.value = end_ip
                self.start_ip_input.update()
                self.end_ip_input.update()
                self.show_snackbar(self.t("use_subnet_snack", f"{start_ip} - {end_ip}"))
        except Exception:
            pass

    def show_snackbar(self, message: str, color=None):
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text(message, color=ft.Colors.WHITE),
            bgcolor=color or ft.Colors.BLUE_GREY_800
        )
        self.page.snack_bar.open = True
        self.page.update()

    async def update_progress_async(self, current, total, current_ip):
        pct = current / total
        self.progress_bar.value = pct
        self.status_text.value = self.t("status_scanning", current, total, current_ip)
        self.page.update()

    async def host_found_async(self, host_info):
        self.discovered_hosts.append(host_info)
        # Sort hosts by last octet for neat display
        try:
            self.discovered_hosts.sort(key=lambda h: list(map(int, h['ip'].split('.'))))
        except Exception:
            pass
        self.refresh_results_ui()

    async def scan_completed_async(self, elapsed):
        self.start_btn.disabled = False
        self.cancel_btn.disabled = True
        self.progress_bar.visible = False
        
        # Restore settings fields visibility has been removed in favor of Tabs layout
        
        if self.scanner_backend.cancel_requested:
            self.status_text.value = self.t("status_cancelled", len(self.discovered_hosts))
            self.show_snackbar(self.t("snack_cancelled"))
        else:
            self.status_text.value = self.t("status_completed", elapsed, len(self.discovered_hosts))
            self.show_snackbar(self.t("snack_finished", len(self.discovered_hosts)), ft.Colors.GREEN_800)
            
        if len(self.discovered_hosts) > 0:
            self.export_btn.disabled = False
            
        self.page.update()

    def start_scan(self, e):
        # Reset previous data
        self.discovered_hosts.clear()
        self.results_list.controls.clear()
        self.results_title.value = self.t("discovered_title", 0)
        self.export_btn.disabled = True
        
        # Get and parse inputs
        start_ip_str = self.start_ip_input.value.strip()
        end_ip_str = self.end_ip_input.value.strip()
        ports_str = self.ports_input.value.strip()
        scan_mode = self.scan_mode_radio.value
        timeout = float(self.timeout_input.value)
        
        # Resolve target IPs
        if not end_ip_str:
            self.all_ips_to_scan = scanner.parse_ip_range(start_ip_str)
        else:
            self.all_ips_to_scan = scanner.parse_ip_start_end(start_ip_str, end_ip_str)
            
        if not self.all_ips_to_scan:
            self.show_snackbar(self.t("snack_invalid_ip"), ft.Colors.RED_ACCENT_700)
            return
            
        target_ports = scanner.parse_ports(ports_str)
        
        # Update UI state
        self.start_btn.disabled = True
        self.cancel_btn.disabled = False
        self.progress_bar.value = 0
        self.progress_bar.visible = True
        self.status_text.value = self.t("status_init", len(self.all_ips_to_scan))
        
        # Switch to Results tab on mobile
        if hasattr(self, "tabs"):
            self.tabs.selected_index = 1
            self.tabs.update()
        
        self.save_settings()
        self.page.update()
        
        # Define background task worker
        def worker():
            start_time = time.time()
            
            def progress_cb(current, total, current_ip):
                self.page.run_task(self.update_progress_async, current, total, current_ip)
                
            def host_found_cb(host_info):
                self.page.run_task(self.host_found_async, host_info)
                
            # Run scan
            self.scanner_backend.scan_network(
                ips=self.all_ips_to_scan,
                ports_to_scan=target_ports,
                scan_mode=scan_mode,
                progress_callback=progress_cb,
                host_found_callback=host_found_cb
            )
            
            # Scan completed or cancelled
            elapsed = time.time() - start_time
            self.page.run_task(self.scan_completed_async, elapsed)

        # Start thread
        self.scan_thread = threading.Thread(target=worker, daemon=True)
        self.scan_thread.start()

    def cancel_scan(self, e):
        self.status_text.value = self.t("status_cancelled", len(self.discovered_hosts))
        self.scanner_backend.cancel()
        self.cancel_btn.disabled = True
        self.page.update()

    def refresh_results_ui(self):
        # Clear list
        self.results_list.controls.clear()
        
        filter_text = self.search_filter.value.lower().strip()
        visible_count = 0
        
        for host in self.discovered_hosts:
            ip = host.get("ip", "")
            hostname = host.get("hostname", "Unknown")
            rtt = host.get("rtt")
            ports = host.get("ports", [])
            
            # Check filter
            if filter_text:
                match = (
                    filter_text in ip.lower() or 
                    filter_text in hostname.lower() or
                    any(filter_text in str(p.get("port")) or filter_text in p.get("service").lower() for p in ports)
                )
                if not match:
                    continue
                    
            visible_count += 1
            
            # Build chips for open ports
            port_chips = []
            for p in ports:
                port_num = p.get("port")
                service = p.get("service")
                port_chips.append(
                    ft.Container(
                        content=ft.Text(f"{port_num}/{service}", size=11, color=ft.Colors.CYAN_100),
                        bgcolor="#041D24",
                        border=ft.Border.all(1, ft.Colors.CYAN_700),
                        border_radius=5,
                        padding=ft.Padding.symmetric(horizontal=6, vertical=2),
                    )
                )
                
            ports_row = ft.Row(
                controls=port_chips if port_chips else [
                    ft.Text(self.t("no_ports"), size=12, color=ft.Colors.GREY_500, italic=True)
                ],
                wrap=True,
                spacing=5,
            )

            latency_str = f"{rtt} ms" if rtt else "N/A"
            
            # Create host card
            card = ft.Card(
                content=ft.Container(
                    content=ft.Column(
                        controls=[
                            ft.Row(
                                controls=[
                                    ft.Row(
                                        controls=[
                                            ft.Container(width=10, height=10, bgcolor=ft.Colors.GREEN_ACCENT_400, shape=ft.BoxShape.CIRCLE),
                                            ft.Text(ip, size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                                        ],
                                        spacing=6,
                                    ),
                                    ft.Row(
                                        controls=[
                                            ft.Icon(icon=ft.Icons.SPEED, size=12, color=ft.Colors.GREY_400),
                                            ft.Text(latency_str, size=11, color=ft.Colors.GREY_400),
                                        ],
                                        spacing=2,
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            ft.Row(
                                controls=[
                                    ft.Text(self.t("hostname"), size=11, color=ft.Colors.GREY_400),
                                    ft.Text(hostname, size=11, color=ft.Colors.CYAN_300, weight=ft.FontWeight.W_500),
                                ],
                                spacing=4,
                            ),
                            ft.Divider(height=1, color=ft.Colors.GREY_800),
                            ft.Text(self.t("open_ports"), size=10, color=ft.Colors.GREY_400),
                            ports_row,
                        ],
                        spacing=6,
                    ),
                    padding=10,
                ),
                bgcolor="#10161A",
            )
            self.results_list.controls.append(card)
            
        self.results_title.value = self.t("discovered_title", visible_count)
        self.results_list.update()
        self.page.update()

    def apply_filter(self, e):
        self.refresh_results_ui()

    def export_results(self, e):
        if not self.discovered_hosts:
            return
            
        # Compile report
        report_data = {
            "scan_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "target_subnet": f"{self.start_ip_input.value} - {self.end_ip_input.value}",
            "hosts_discovered": len(self.discovered_hosts),
            "hosts": self.discovered_hosts
        }
        
        report_str = json.dumps(report_data, indent=2)
        
        # 1. Copy to clipboard
        self.page.run_task(self.clipboard.set, report_str)
        
        # 2. Try to write to Desktop storage if not Android
        is_android = os.environ.get("FLET_PLATFORM") == "android" or os.path.exists("/system/bin/app_process")
        
        saved_file_msg = ""
        if not is_android:
            try:
                out_dir = Path.home() / "spynetscan_files"
                out_dir.mkdir(parents=True, exist_ok=True)
                filename = f"scan_report_{time.strftime('%Y%m%d_%H%M%S')}.json"
                filepath = out_dir / filename
                filepath.write_text(report_str, encoding="utf-8")
                saved_file_msg = self.t("save_success", filepath)
            except Exception as ex:
                saved_file_msg = self.t("save_fail", str(ex))
                
        self.show_snackbar(self.t("snack_export", saved_file_msg), ft.Colors.GREEN_800)


def main(page: ft.Page):
    # Close PyInstaller splash screen if running as a bundle
    try:
        import pyi_splash
        pyi_splash.close()
    except ImportError:
        pass

    # Enable nice theme properties
    page.title = "SpyNetScan"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = ft.Colors.BLACK
    
    # Configure desktop window dimensions
    page.window_width = 750
    page.window_height = 850
    page.window_min_width = 600
    page.window_min_height = 700
    
    # Early render safety
    app_loading = ft.Container(
        content=ft.Column(
            controls=[
                ft.ProgressRing(color=ft.Colors.GREEN_ACCENT_400),
                ft.Text("Initializing SpyNetScan...", color=ft.Colors.GREY_400),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
        ),
        alignment=ft.Alignment(0, 0),
        expand=True,
    )
    page.add(app_loading)
    page.update()
    
    try:
        # Build the main interface
        app = SpyNetScanApp(page)
        main_layout = app.build()
        
        # Replace loader with main interface
        page.controls.clear()
        page.add(main_layout)
        page.update()
    except Exception as e:
        # Prevent Android Black Screen by showing error
        page.controls.clear()
        page.add(
            ft.Container(
                content=ft.Column(
                    controls=[
                        ft.Icon(icon=ft.Icons.ERROR_OUTLINE, color=ft.Colors.RED_ACCENT_400, size=50),
                        ft.Text("Startup Error Occurred:", weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.Text(str(e), color=ft.Colors.RED_ACCENT_200, selectable=True),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER,
                ),
                alignment=ft.Alignment(0, 0),
                expand=True,
            )
        )
        page.update()

if __name__ == "__main__":
    ft.run(main, assets_dir="assets")
