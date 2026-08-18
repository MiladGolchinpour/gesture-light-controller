import socket
import requests
import time
import threading

DISCOVERY_PORT = 5005

def find_wemos():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.settimeout(2)
    sock.sendto(b"DISCOVER_WEMOS", ("255.255.255.255", DISCOVERY_PORT))

    try:
        data, addr = sock.recvfrom(64)
        if data.startswith(b"WEMOS"):
            return addr[0]
    except socket.timeout:
        pass
    finally:
        sock.close()

    return None

class WemosClient:
    def __init__(self, ip=None):
        self.base_url = None
        self.state = None
        self.running = True
        thread = threading.Thread(target=self.background_search, daemon=True)
        thread.start()

    def background_search(self):
        while self.running:
            if self.base_url:
                if not self.status():
                    print("Wemos disconnected")
                    self.base_url = None
            else:
                print("Searching Wemos...")
                ip = find_wemos()
                if ip:
                    self.connect(ip)

            time.sleep(2)

    def connect(self, ip):
        self.base_url = f"http://{ip}"

        if self.status():
            print("Wemos connected:", ip)
            return True

        self.base_url = None
        return False

    def status(self):
        try:
            r = requests.get(f"{self.base_url}/status", timeout=1)
            if not r.text.startswith("WEMOS"):
                return False

            _, ip, state = r.text.split("|")
            self.state = state

            return True
        except Exception:
            return False

    @property
    def connected(self):
        return self.base_url is not None

    def send(self, command):
        if not self.base_url:
            return None

        try:
            r = requests.get(f"{self.base_url}/{command}", timeout=0.5)
            return r.text
        except requests.RequestException:
            self.base_url = None
            return None