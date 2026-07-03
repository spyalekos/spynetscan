import socket
import subprocess
import platform
import ipaddress
import concurrent.futures
from typing import List, Dict, Tuple, Callable

IS_WINDOWS = platform.system() == "Windows"

COMMON_PORTS = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    115: "SFTP",
    123: "NTP",
    135: "RPC",
    139: "NetBIOS",
    143: "IMAP",
    161: "SNMP",
    194: "IRC",
    443: "HTTPS",
    445: "SMB",
    1433: "MSSQL",
    1521: "Oracle",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    5900: "VNC",
    8000: "HTTP-Alt",
    8080: "HTTP-Proxy",
    8443: "HTTPS-Alt",
}

def get_local_ip() -> str:
    """Returns the local IP address of the interface used to connect to the internet."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't need to be reachable, just triggers the routing lookups
        s.connect(('8.8.8.8', 1))
        ip = s.getsockname()[0]
    except Exception:
        # Fallback to local hostname lookup
        try:
            ip = socket.gethostbyname(socket.gethostname())
        except Exception:
            ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def get_suggested_subnet(ip: str) -> str:
    """Returns a suggested /24 CIDR network block from a given IP address."""
    try:
        parts = ip.split('.')
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.{parts[2]}.0/24"
    except Exception:
        pass
    return "192.168.1.0/24"

def parse_ip_range(ip_range_str: str) -> List[str]:
    """Parses CIDR, hyphenated range, or single IP into a list of individual IP strings."""
    ip_range_str = ip_range_str.strip()
    if not ip_range_str:
        return []
    
    if '/' in ip_range_str:
        try:
            net = ipaddress.ip_network(ip_range_str, strict=False)
            if net.num_addresses > 2:
                return [str(ip) for ip in net.hosts()]
            else:
                return [str(ip) for ip in net]
        except Exception:
            return []
    elif '-' in ip_range_str:
        try:
            parts = ip_range_str.split('-')
            start_str = parts[0].strip()
            end_str = parts[1].strip()
            if '.' in end_str:
                # Full range: e.g. 192.168.1.50-192.168.1.100
                start_ip = ipaddress.ip_address(start_str)
                end_ip = ipaddress.ip_address(end_str)
            else:
                # Partial range: e.g. 192.168.1.50-100
                start_ip = ipaddress.ip_address(start_str)
                ip_parts = start_str.split('.')
                ip_parts[-1] = end_str
                end_ip = ipaddress.ip_address('.'.join(ip_parts))
                
            start_int = int(start_ip)
            end_int = int(end_ip)
            if start_int > end_int:
                start_int, end_int = end_int, start_int
            # Limit IP range to at most 1024 IPs to prevent memory exhaustion / locking UI
            total_ips = end_int - start_int + 1
            if total_ips > 1024:
                end_int = start_int + 1023
            return [str(ipaddress.ip_address(ip_int)) for ip_int in range(start_int, end_int + 1)]
        except Exception:
            return []
    else:
        try:
            return [str(ipaddress.ip_address(ip_range_str))]
        except Exception:
            return []

def parse_ip_start_end(start_str: str, end_str: str) -> List[str]:
    """Generates a list of IP addresses between start_str and end_str inclusive."""
    try:
        start_ip = ipaddress.ip_address(start_str.strip())
        end_ip = ipaddress.ip_address(end_str.strip())
        start_int = int(start_ip)
        end_int = int(end_ip)
        if start_int > end_int:
            start_int, end_int = end_int, start_int
        # Limit to 1024 IPs to prevent resource exhaustion
        total_ips = end_int - start_int + 1
        if total_ips > 1024:
            end_int = start_int + 1023
        return [str(ipaddress.ip_address(ip_int)) for ip_int in range(start_int, end_int + 1)]
    except Exception:
        return []

def parse_ports(ports_str: str) -> List[int]:
    """Parses port ranges (e.g. 80,443,8000-8080) into a sorted list of integer ports."""
    ports = []
    ports_str = ports_str.strip()
    if not ports_str:
        return list(COMMON_PORTS.keys())
        
    for part in ports_str.split(','):
        part = part.strip()
        if not part:
            continue
        if '-' in part:
            try:
                start_str, end_str = part.split('-')
                start = int(start_str.strip())
                end = int(end_str.strip())
                if start > end:
                    start, end = end, start
                # Clamp within valid bounds
                start = max(1, start)
                end = min(65535, end)
                # Safeguard: limit range size to prevent stalling
                if end - start > 500:
                    end = start + 500
                ports.extend(range(start, end + 1))
            except Exception:
                pass
        else:
            try:
                port = int(part)
                if 1 <= port <= 65535:
                    ports.append(port)
            except Exception:
                pass
    return sorted(list(set(ports)))

def ping_ip(ip: str, timeout: float = 1.0) -> Tuple[bool, float]:
    """Pings a single IP. Returns (is_active, round_trip_time_ms)."""
    # Windows vs Linux ping flags
    if IS_WINDOWS:
        timeout_ms = int(timeout * 1000)
        cmd = ["ping", "-n", "1", "-w", str(timeout_ms), ip]
    else:
        # -c 1: 1 packet, -W 1: 1 sec timeout (or max(1, int(timeout)))
        timeout_sec = max(1, int(timeout))
        cmd = ["ping", "-c", "1", "-W", str(timeout_sec), ip]
        
    try:
        startupinfo = None
        if IS_WINDOWS:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
        import time
        start_time = time.perf_counter()
        
        res = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout + 1.0,
            startupinfo=startupinfo
        )
        duration_ms = (time.perf_counter() - start_time) * 1000.0
        
        return (res.returncode == 0, round(duration_ms, 1))
    except Exception:
        # Fallback if ping fails (e.g. binary not found)
        return (False, 0.0)

def scan_port(ip: str, port: int, timeout: float = 0.5) -> bool:
    """Attempts to connect to a TCP port. Returns True if open."""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        res = s.connect_ex((ip, port))
        return res == 0
    except Exception:
        return False
    finally:
        s.close()

def resolve_hostname(ip: str) -> str:
    """Performs a reverse DNS lookup to get the hostname of the IP."""
    try:
        # Wait up to 1 second using socket timeout for DNS resolving
        socket.setdefaulttimeout(1.0)
        name, _, _ = socket.gethostbyaddr(ip)
        return name
    except Exception:
        return "Unknown"

class NetworkScanner:
    """Handles concurrent network scanning of IPs and ports."""
    
    def __init__(self):
        self.is_running = False
        self.cancel_requested = False
        
    def cancel(self):
        self.cancel_requested = True
        
    def scan_network(
        self,
        ips: List[str],
        ports_to_scan: List[int],
        scan_mode: str,  # "ping", "port_probe", "full"
        progress_callback: Callable[[int, int, str], None],  # (current, total, current_ip)
        host_found_callback: Callable[[dict], None]  # dict containing host info
    ):
        """Runs the scan loop, scanning IPs concurrently using a thread pool."""
        self.is_running = True
        self.cancel_requested = False
        
        total_ips = len(ips)
        if total_ips == 0:
            self.is_running = False
            return
            
        # Determine concurrency based on mode and total IPs
        # A thread pool works great for I/O bound ping/sockets
        max_workers = min(50, total_ips)
        
        # Helper to scan a single host
        def scan_host(ip: str) -> dict:
            if self.cancel_requested:
                return {"ip": ip, "active": False, "skipped": True}
                
            active = False
            rtt = 0.0
            open_ports = []
            
            # 1. Check IP active state
            if scan_mode == "ping" or scan_mode == "full":
                active, rtt = ping_ip(ip, timeout=1.0)
                
            # If ping was not requested or ping failed, probe common ports to see if host is alive
            if not active and (scan_mode == "port_probe" or scan_mode == "full"):
                # Probe a small subset of highly common ports to determine if host is alive
                probe_ports = [80, 443, 22, 445, 3389]
                for p in probe_ports:
                    if self.cancel_requested:
                        break
                    if scan_port(ip, p, timeout=0.3):
                        active = True
                        open_ports.append(p)
                        break
            
            # 2. If host is active, scan all selected ports
            if active and not self.cancel_requested:
                hostname = resolve_hostname(ip)
                
                # Scan remaining ports
                ports_to_check = [p for p in ports_to_scan if p not in open_ports]
                
                # Scan ports concurrently for this host if there are many ports
                if len(ports_to_check) > 10:
                    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as port_executor:
                        port_futures = {
                            port_executor.submit(scan_port, ip, p, 0.4): p 
                            for p in ports_to_check
                        }
                        for future in concurrent.futures.as_completed(port_futures):
                            if self.cancel_requested:
                                break
                            p = port_futures[future]
                            try:
                                if future.result():
                                    open_ports.append(p)
                            except Exception:
                                pass
                else:
                    for p in ports_to_check:
                        if self.cancel_requested:
                            break
                        if scan_port(ip, p, timeout=0.4):
                            open_ports.append(p)
                
                # Sort open ports list
                open_ports.sort()
                
                # Map open ports to names
                ports_info = [
                    {"port": p, "service": COMMON_PORTS.get(p, "Unknown")} 
                    for p in open_ports
                ]
                
                return {
                    "ip": ip,
                    "active": True,
                    "hostname": hostname,
                    "rtt": rtt if rtt > 0 else None,
                    "ports": ports_info
                }
            
            return {"ip": ip, "active": False}

        completed = 0
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(scan_host, ip): ip for ip in ips}
            
            for future in concurrent.futures.as_completed(futures):
                if self.cancel_requested:
                    # Cancel remaining futures
                    for f in futures:
                        f.cancel()
                    break
                    
                completed += 1
                ip = futures[future]
                try:
                    result = future.result()
                    if result.get("active"):
                        host_found_callback(result)
                except Exception:
                    pass
                
                progress_callback(completed, total_ips, ip)
                
        self.is_running = False
