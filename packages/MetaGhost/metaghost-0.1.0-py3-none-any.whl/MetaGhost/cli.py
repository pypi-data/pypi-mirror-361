import argparse
import sys
import time
import random
import socket
import hashlib
from datetime import datetime, timedelta

version = "3.2.1"
session_id = hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]

class NetworkUtils:
    @staticmethod
    def generate_random_ip():
        return f"{random.randint(10,199)}.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(1,254)}"
    
    @staticmethod
    def generate_random_mac():
        return ":".join(f"{random.randint(0x00, 0xff):02x}" for _ in range(6))
    
    @staticmethod
    def get_local_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return NetworkUtils.generate_random_ip()

class TargetProfile:
    def __init__(self, platform, link):
        self.platform = platform
        self.link = link
        self.session_start = datetime.now()
        self.geoip = self._generate_geoip()
        self.device_info = self._generate_device_info()
        self.browser_info = self._generate_browser_info()
        
    def _generate_geoip(self):
        cities = ["New York", "London", "Tokyo", "Singapore", "Berlin", "Moscow"]
        isps = ["Comcast", "Verizon", "Deutsche Telekom", "NTT", "China Telecom"]
        return {
            "IP": NetworkUtils.generate_random_ip(),
            "Country": random.choice(["US", "UK", "JP", "DE", "CN"]),
            "City": random.choice(cities),
            "ISP": random.choice(isps),
            "ASN": f"AS{random.randint(1000,9999)}"
        }
    
    def _generate_device_info(self):
        devices = {
            "mobile": ["iPhone 14 Pro", "Samsung Galaxy S23", "Google Pixel 7"],
            "desktop": ["MacBook Pro M2", "Dell XPS 15", "HP Spectre x360"]
        }
        device_type = random.choice(["mobile", "desktop"])
        return {
            "Type": device_type,
            "Model": random.choice(devices[device_type]),
            "OS": "iOS 16" if "iPhone" in device_type else "Android 13" if device_type == "mobile" else random.choice(["Windows 11", "macOS Ventura"]),
            "MAC": NetworkUtils.generate_random_mac()
        }
    
    def _generate_browser_info(self):
        browsers = [
            ("Chrome", f"{random.randint(100,115)}.0.{random.randint(1000,9999)}.{random.randint(10,99)}"),
            ("Firefox", f"{random.randint(100,115)}.0"),
            ("Safari", f"{random.randint(14,16)}.{random.randint(0,3)}")
        ]
        browser, version = random.choice(browsers)
        return {
            "Browser": browser,
            "Version": version,
            "UserAgent": f"Mozilla/5.0 ({'iPhone' if self.device_info['Type'] == 'mobile' else 'Windows NT 10.0; Win64; x64'}) AppleWebKit/537.36 (KHTML, like Gecko) {browser}/{version} {'Mobile' if self.device_info['Type'] == 'mobile' else ''} Safari/537.36"
        }

class ExploitEngine:
    def __init__(self, target):
        self.target = target
        self.session_id = session_id
        self.local_ip = NetworkUtils.get_local_ip()
        self.vulnerabilities = self._scan_vulnerabilities()
        
    def _scan_vulnerabilities(self):
        vulns = []
        if random.random() > 0.3:
            vulns.append(("CVE-2023-{}{}".format(random.randint(2000,3999), random.randint(100,999)), "Remote Code Execution", "High"))
        if random.random() > 0.5:
            vulns.append(("CVE-2023-{}{}".format(random.randint(4000,5999), "CSRF Token Bypass", "Medium")))
        if random.random() > 0.7:
            vulns.append(("CVE-2023-{}{}".format(random.randint(6000,7999), "Session Fixation", "Low")))
        return vulns
    
    def execute(self):
        print(f"\n\033[1m[+] Session ID: {self.session_id}\033[0m")
        print(f"[+] Local IP: {self.local_ip}")
        print(f"[+] Target Platform: {self.target.platform.upper()}")
        print(f"[+] Target URL: \033[34m{self.target.link}\033[0m\n")
        
        self._show_target_info()
        self._network_recon()
        self._exploit_chain()
        return self._extract_credentials()
    
    def _show_target_info(self):
        print("\n\033[1m[>] Target Profile Analysis\033[0m")
        print(f"  Device: {self.target.device_info['Model']} ({self.target.device_info['Type']})")
        print(f"  OS: {self.target.device_info['OS']}")
        print(f"  Browser: {self.target.browser_info['Browser']} {self.target.browser_info['Version']}")
        print(f"  Location: {self.target.geoip['City']}, {self.target.geoip['Country']}")
        print(f"  Network: {self.target.geoip['ISP']} ({self.target.geoip['ASN']})\n")
    
    def _network_recon(self):
        print("\033[1m[>] Network Reconnaissance\033[0m")
        steps = [
            ("Initializing packet sniffer", 1.2, True),
            ("Mapping network topology", 1.5, random.random() > 0.2),
            ("Identifying open ports", 1.8, True),
            ("Fingerprinting services", 1.3, True),
            ("Analyzing traffic patterns", 2.0, random.random() > 0.3)
        ]
        self._simulate_steps(steps)
        
        if self.vulnerabilities:
            print("\n\033[1m[+] Discovered Vulnerabilities:\033[0m")
            for vuln in self.vulnerabilities:
                print(f"  {vuln[0]:<15} {vuln[1]:<25} \033[33m{vuln[2]}\033[0m")
        else:
            print("\n\033[31m[!] No critical vulnerabilities found - switching to social engineering vector\033[0m")
    
    def _exploit_chain(self):
        print("\n\033[1m[>] Exploit Chain Execution\033[0m")
        
        if self.vulnerabilities:
            steps = [
                ("Preparing exploit payload", 1.5, True),
                ("Bypassing ASLR", 2.0, random.random() > 0.4),
                ("Exploiting memory corruption", 2.5, random.random() > 0.6),
                ("Establishing ROP chain", 1.8, True),
                ("Escalating privileges", 2.2, random.random() > 0.5)
            ]
        else:
            steps = [
                ("Generating phishing template", 1.2, True),
                ("Spoofing login page", 1.5, True),
                ("Setting up reverse proxy", 1.8, random.random() > 0.3),
                ("Sending targeted message", 2.0, True),
                ("Capturing credentials", 1.5, True)
            ]
        
        self._simulate_steps(steps)
    
    def _extract_credentials(self):
        print("\n\033[1m[>] Extracting Sensitive Data\033[0m")
        
        steps = [
            ("Dumping memory contents", 2.0, True),
            ("Locating credential store", 1.8, random.random() > 0.4),
            ("Decrypting password hashes", 2.5, random.random() > 0.6),
            ("Extracting session cookies", 1.5, True),
            ("Harvesting auth tokens", 1.8, True)
        ]
        self._simulate_steps(steps)
        
        return self._generate_credentials()
    
    def _generate_credentials(self):
        domains = {
            "ig": "instagram.com",
            "fb": "facebook.com",
            "tt": "tiktok.com",
            "tw": "twitter.com"
        }
        domain = domains.get(self.target.platform, "example.com")
        
        return {
            "Username": f"louey lahwel",
            "Phone Number": f"+216 58335744",
            "Password": f"loueyLLL123",
            "Last Login": (datetime.now() - timedelta(days=random.randint(0,30), 
                          hours=random.randint(0,23))).strftime("%Y-%m-%d %H:%M"),
            "2FA Status": random.choice(["Disabled", "Enabled (SMS)", "Enabled (Authenticator)"]),
            "IP Address": self.target.geoip['IP'],
            "MAC Address": self.target.device_info['MAC'],
            "Session Token": f"xoxb-{random.randint(100000000,999999999)}-{random.randint(100000000,999999999)}",
            "Cookies": "; ".join([f"{k}={random.getrandbits(128):x}" for k in ["sessionid", "csrftoken", "ds_user_id"]]),
            "Auth Token": f"EAAC{random.getrandbits(128):x}",
            "Account ID": str(random.randint(100000000000, 999999999999)),
            "Recovery Email": f"none",
            "Email": f"loueylahwel@gmail.com"
        }
    
    def _simulate_steps(self, steps):
        for i, (step, delay, success) in enumerate(steps):
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {step}", end="")
            sys.stdout.flush()
            
            for _ in range(random.randint(3,6)):
                time.sleep(delay/5)
                print(".", end="")
                sys.stdout.flush()
            
            if not success:
                print(f" \033[31mFAILED\033[0m (retrying)")
                time.sleep(1)
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Retrying {step}", end="")
                for _ in range(3):
                    time.sleep(0.3)
                    print(".", end="")
                    sys.stdout.flush()
                print(" \033[32mSUCCESS\033[0m")
            else:
                print(" \033[32mSUCCESS\033[0m")
            
            progress = int((i + 1) / len(steps) * 100)
            sys.stdout.write(f"\r\033[KProgress: {progress}%")
            sys.stdout.flush()
            time.sleep(random.uniform(0.1, 0.3))

def show_banner():
    print(f"""
\033[34m
 ██████   ██████ ██████████ ███████████   █████████        █████████  █████   █████    ███████     █████████  ███████████
░░██████ ██████ ░░███░░░░░█░█░░░███░░░█  ███░░░░░███      ███░░░░░███░░███   ░░███   ███░░░░░███  ███░░░░░███░█░░░███░░░█
 ░███░█████░███  ░███  █ ░ ░   ░███  ░  ░███    ░███     ███     ░░░  ░███    ░███  ███     ░░███░███    ░░░ ░   ░███  ░ 
 ░███░░███ ░███  ░██████       ░███     ░███████████    ░███          ░███████████ ░███      ░███░░█████████     ░███    
 ░███ ░░░  ░███  ░███░░█       ░███     ░███░░░░░███    ░███    █████ ░███░░░░░███ ░███      ░███ ░░░░░░░░███    ░███    
 ░███      ░███  ░███ ░   █    ░███     ░███    ░███    ░░███  ░░███  ░███    ░███ ░░███     ███  ███    ░███    ░███    
 █████     █████ ██████████    █████    █████   █████    ░░█████████  █████   █████ ░░░███████░  ░░█████████     █████   
░░░░░     ░░░░░ ░░░░░░░░░░    ░░░░░    ░░░░░   ░░░░░      ░░░░░░░░░  ░░░░░   ░░░░░    ░░░░░░░     ░░░░░░░░░     ░░░░░    
\033[0m
                          Advanced Social Engineering Framework
                                Version {version}
""")


def show_help():
    print("""
\033[1mMetaGhost Command Reference\033[0m

Core Commands:
  exploit -l <url> -p <platform>    Launch targeted exploitation
  recon   -l <url> -p <platform>    Perform reconnaissance only
  help                              Show this help menu
  exit                              Exit the framework

Platform Options:
  ig      Instagram
  fb      Facebook
  tt      TikTok
  tw      Twitter

Example:
  exploit -l https://instagram.com/target_profile -p ig
""")

def parse_args(arg_str):
    parser = argparse.ArgumentParser(prog='exploit', description='MetaGhost Exploit Module', add_help=False)
    parser.add_argument('-l', '--link', required=True, help='target profile link')
    parser.add_argument('-p', '--platform', required=True, choices=['ig', 'fb', 'tt', 'tw'], help='platform code')
    return parser.parse_args(arg_str.split())

def display_results(credentials, target):
    print(f"\n\033[1m[✓] Operation completed successfully at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\033[0m")
    print(f"[+] Session ID: {session_id}")
    print(f"[+] Target: {target.link}")
    print(f"[+] Platform: {target.platform.upper()}")
    print(f"[+] Access Level: \033[33m{'ADMIN' if random.random() > 0.7 else 'USER'}\033[0m")
    
    print("\n\033[1m[+] Retrieved Credentials:\033[0m")
    max_key_len = max(len(key) for key in credentials.keys())
    for key, value in credentials.items():
        print(f"  \033[36m{key.ljust(max_key_len)}\033[0m : {value}")
    
    print("\n\033[1m[+] Post-Exploitation Options:\033[0m")
    print("  1. Maintain persistent access")
    print("  2. Dump friend list/connections")
    print("  3. Clone session to remote server")
    print("  4. Cleanup traces\n")
    
    print(f"[*] Session will auto-terminate in {random.randint(10,60)} minutes")

def main():
    show_banner()
    
    while True:
        try:
            command_line = input("\033[35mghost@framework~\033[0m ").strip()
            if not command_line:
                continue
            
            parts = command_line.split(maxsplit=1)
            command = parts[0]
            arg_str = parts[1] if len(parts) > 1 else ""
            
            if command == "exit":
                print("\033[36m[+] Terminating session and cleaning up...\033[0m")
                time.sleep(1)
                print("[+] All traces erased")
                sys.exit(0)
            
            elif command == "help":
                show_help()
            
            elif command in ["exploit", "recon"]:
                try:
                    args = parse_args(arg_str)
                    target = TargetProfile(args.platform, args.link)
                    engine = ExploitEngine(target)
                    
                    if command == "recon":
                        print("\n\033[1m[+] Starting reconnaissance only mode\033[0m")
                        engine._network_recon()
                        engine._show_target_info()
                    else:
                        credentials = engine.execute()
                        display_results(credentials, target)
                        
                except SystemExit:
                    print("\033[31m[!] Invalid syntax. Try: exploit -l <url> -p <platform>\033[0m")
            
            else:
                print(f"\033[31m[!] Unknown command: '{command}'. Type 'help' for available commands.\033[0m")
        
        except (EOFError, KeyboardInterrupt):
            print("\n\033[36m[+] Interrupt received - terminating session\033[0m")
            sys.exit(0)
        except Exception as e:
            print(f"\033[31m[!] Critical error in module: {e}\033[0m")

if __name__ == "__main__":
    main()