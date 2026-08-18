import network, socket, utime
from machine import Pin, PWM
from tm1637 import TM1637
from config import SSID, PASSWORD

RELAY_PIN = 5 # D1
CLK_PIN = 14 # D5
DIO_PIN = 12 # D6
BUZZER_PIN = 13 # D7
RED_LED_PIN = 4 # D2
GREEN_LED_PIN = 15 # D8
DISCOVERY_PORT = 5005

relay = Pin(RELAY_PIN, Pin.OUT, value=1)
display = TM1637(Pin(CLK_PIN), Pin(DIO_PIN))
red = Pin(RED_LED_PIN, Pin.OUT, value=0)
green = Pin(GREEN_LED_PIN, Pin.OUT, value=0)

light_state = False
wifi_ok = False

def beep(times=1, freq=2500, delay=50):
    buzzer = PWM(Pin(BUZZER_PIN))
    for _ in range(times):
        buzzer.freq(freq)
        buzzer.duty(512)
        utime.sleep_ms(delay)
        buzzer.duty(0)
        utime.sleep_ms(delay)
        
    buzzer.deinit()  

def leds(red_state=False, green_state=False):
    red.value(red_state)
    green.value(green_state)

def status(state):
    if state == "boot":
        leds(False, False)
        display.text("BOOT")

    elif state == "wifi":
        leds(True, False)
        display.text("WIFI")

    elif state == "ready":
        leds(False, True)
        display.text("RDY")

    elif state == "on":
        display.text("ON")

    elif state == "off":
        display.text("OFF")

    elif state == "error":
        leds(True, False)
        display.text("ERR")

def set_light(state):
    global light_state
    light_state = state

    relay.value(0 if state else 1)
    status("on" if state else "off")

    beep(2 if state else 1, 1500 if state else 500)

def toggle_light():
    set_light(not light_state)

def create_discovery():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0)
    sock.bind(("0.0.0.0", DISCOVERY_PORT))
    return sock

def connect_wifi():
    global wifi_ok
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect(SSID, PASSWORD)
    timeout = 20

    while not wifi.isconnected() and timeout:
        status("wifi")
        utime.sleep(1)
        timeout -= 1

    if not wifi.isconnected():
        status("error")
        beep(3, 300, 100)
        return None

    wifi_ok = True
    return wifi

# boot
status("boot")
beep(1, 300, 150)

wifi = connect_wifi()

if not wifi:
    while True:
        status("error")
        utime.sleep(5)

ip = wifi.ifconfig()[0]

print("Connected:", ip)

discovery = create_discovery()
server = socket.socket()
server.bind(("0.0.0.0", 80))
server.listen(1)
server.settimeout(0.1)

status("ready")

beep(1, 8000, 150)
print("Server ready")

# loop
while True:
    # wifi monitor
    if not wifi.isconnected():
        status("error")
        display.text("ERR")

        utime.sleep(2)
        continue

    # udp discovery
    try:
        data, addr = discovery.recvfrom(64)
        if data == b"DISCOVER_WEMOS":
            discovery.sendto(f"WEMOS|{ip}".encode(), addr)
    except:
        pass

    # http
    try:
        conn, addr = server.accept()
        request = conn.recv(512).decode()

        if "GET /on" in request:
            set_light(True)

        elif "GET /off" in request:
            set_light(False)

        elif "GET /toggle" in request:
            toggle_light()

        elif "GET /status" in request:
            response = (f"WEMOS | {ip} | {'ON' if light_state else 'OFF'}")

        else:
            response = "OK"

        conn.send(
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/plain\r\n"
            "\r\n"
            + response
        )
        conn.close()
    except:
        pass