import time
import requests
from pyModbusTCP.client import ModbusClient
import ast

# Telegram configuration
BOT_TOKEN = "7594584104:AAG-COojfNwNe5APYXN3vLYy7qJ00G63dUY"
CHAT_ID = "-1002414792856"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

RAW_MIN = 30994
RAW_MAX = 34982
PRESSURE_MIN = 0.0  # kPa
PRESSURE_MAX = 50.0  # kPa

NOTIF_INTERVAL = 5  # seconds

class ZoneConfig:
    def __init__(self, name, ip, port, reg, num_reg, max_threshold, min_threshold):
        self.name = name
        self.ip = ip
        self.port = port
        self.reg = reg
        self.num_reg = num_reg
        self.max_threshold = max_threshold
        self.min_threshold = min_threshold
        self.is_above_max = False
        self.is_below_min = False
        self.last_notif_time = 0
        self.client = ModbusClient(host=ip,auto_open=True)

    def read_pressure(self):
        try:
            response = self.client.read_holding_registers(self.reg, self.num_reg)
            response_list = ast.literal_eval(str(response))
            return self.map_pressure(response_list[0])
        except Exception as e:
            print(f"Error reading {self.name}: {e}")
        return None

    def map_pressure(self, value):
        value = max(min(value, RAW_MAX), RAW_MIN)
        return PRESSURE_MIN + ((value - RAW_MIN) / (RAW_MAX - RAW_MIN)) * (PRESSURE_MAX - PRESSURE_MIN)

zones = [
    ZoneConfig("Zone A", "0.0.0.0", 502 , 0, 1, 15, 5)
]

def send_telegram_message(message):
    data = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(TELEGRAM_API_URL, data=data)
        print("Message sent:", message)
    except Exception as e:
        print("Error sending message:", e)

def check_zone_thresholds(zone):
    current_time = time.time()
    pressure = zone.read_pressure()
    if pressure is None:
        return

    should_notify = False
    message = f"[ALERT] {zone.name}\nCurrent Pressure: {pressure:.2f} kPa\n"
    print(message)

    if pressure >= zone.max_threshold and (not zone.is_above_max or current_time - zone.last_notif_time >= NOTIF_INTERVAL):
        message += f"Status: ALERT - Above Max Threshold ({zone.max_threshold} kPa)\n"
        should_notify = True
        zone.is_above_max = True
        zone.last_notif_time = current_time
    else:
        zone.is_above_max = False

    if pressure <= zone.min_threshold and (not zone.is_below_min or current_time - zone.last_notif_time >= NOTIF_INTERVAL):
        message += f"Status: WARNING - Below Min Threshold ({zone.min_threshold} kPa)\n"
        should_notify = True
        zone.is_below_min = True
        zone.last_notif_time = current_time
    else:
        zone.is_below_min = False

    if should_notify:
        send_telegram_message(message)

if __name__ == "__main__":
    while True:
        for zone in zones:
            check_zone_thresholds(zone)
        time.sleep(1)
