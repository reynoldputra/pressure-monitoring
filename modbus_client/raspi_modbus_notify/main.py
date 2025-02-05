import time
import requests
import logging
from pyModbusTCP.client import ModbusClient
import ast
from typing import List
from dotenv import load_dotenv
import os


load_dotenv()

# Configure logging with timestamp
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Telegram configuration
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
RAW_MIN = 30994
RAW_MAX = 34982
PRESSURE_MIN = 0.0  # kPa
PRESSURE_MAX = 50.0  # kPa
NOTIF_INTERVAL = int(os.getenv("NOTIF_INTERVAL", 5))  # seconds
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 1))  # seconds
API_BASE_URL = os.getenv("API_BASE_URL")
API_URL = f"{API_BASE_URL}/entries"

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
        self.client = ModbusClient(host=ip, auto_open=True, timeout=5)
        logging.info(f"Initialized zone '{self.name}' - IP: {ip}, Port: {port}, Register: {reg}, Thresholds: {min_threshold}-{max_threshold} kPa")

    def read_pressure(self):
        try:
            response = self.client.read_holding_registers(self.reg, self.num_reg)
            if response is None:
                logging.error(f"[{self.name}] Failed to read pressure - No response from device")
                return None
            
            response_list = ast.literal_eval(str(response))
            raw_value = response_list[0]
            pressure = self.map_pressure(raw_value)
            logging.debug(f"[{self.name}] Raw value: {raw_value}, Mapped pressure: {pressure:.2f} kPa")
            return pressure
        except Exception as e:
            logging.error(f"[{self.name}] Error reading pressure: {str(e)}")
            return None

    def map_pressure(self, value):
        original_value = value
        value = max(min(value, RAW_MAX), RAW_MIN)
        pressure = PRESSURE_MIN + ((value - RAW_MIN) / (RAW_MAX - RAW_MIN)) * (PRESSURE_MAX - PRESSURE_MIN)
        if original_value != value:
            logging.warning(f"[{self.name}] Raw value {original_value} was clamped to {value}")
        return pressure

def send_telegram_message(message):
    data = {"chat_id": CHAT_ID, "text": message}
    try:
        response = requests.post(TELEGRAM_API_URL, data=data)
        response.raise_for_status()
        logging.info(f"Telegram message sent successfully: {message}")
    except Exception as e:
        logging.error(f"Error sending Telegram message: {str(e)}")

def check_zone_thresholds(zone):
    current_time = time.time()
    pressure = zone.read_pressure()
    
    if pressure is None:
        return
        
    logging.info(f"[{zone.name}] Current Pressure: {pressure:.2f} kPa (Min: {zone.min_threshold} kPa, Max: {zone.max_threshold} kPa)")
    
    should_notify = False
    message = f"[ALERT] {zone.name}\nCurrent Pressure: {pressure:.2f} kPa\n"
    
    # Check max threshold
    if pressure >= zone.max_threshold:
        if not zone.is_above_max or current_time - zone.last_notif_time >= NOTIF_INTERVAL:
            logging.warning(f"[{zone.name}] Pressure above maximum threshold: {pressure:.2f} kPa >= {zone.max_threshold} kPa")
            message += f"Status: ALERT - Above Max Threshold ({zone.max_threshold} kPa)\n"
            should_notify = True
            zone.is_above_max = True
            zone.last_notif_time = current_time
    else:
        if zone.is_above_max:
            logging.info(f"[{zone.name}] Pressure returned below maximum threshold: {pressure:.2f} kPa")
        zone.is_above_max = False

    # Check min threshold
    if pressure <= zone.min_threshold:
        if not zone.is_below_min or current_time - zone.last_notif_time >= NOTIF_INTERVAL:
            logging.warning(f"[{zone.name}] Pressure below minimum threshold: {pressure:.2f} kPa <= {zone.min_threshold} kPa")
            message += f"Status: WARNING - Below Min Threshold ({zone.min_threshold} kPa)\n"
            should_notify = True
            zone.is_below_min = True
            zone.last_notif_time = current_time
    else:
        if zone.is_below_min:
            logging.info(f"[{zone.name}] Pressure returned above minimum threshold: {pressure:.2f} kPa")
        zone.is_below_min = False

    if should_notify:
        send_telegram_message(message)

def load_zones_from_api() -> List[ZoneConfig]:
    """Load zone configurations from the API endpoint"""
    try:
        logging.info(f"Fetching zones from API: {API_URL}")
        response = requests.get(API_URL)
        response.raise_for_status()
        
        entries = response.json()
        logging.info(f"Retrieved {len(entries)} zones from API")
        
        zones = []
        for entry in entries:
            zone = ZoneConfig(
                name=entry['title'],
                ip=entry['ip'],
                port=502,
                reg=0,
                num_reg=1,
                max_threshold=entry['max'],
                min_threshold=entry['min']
            )
            zones.append(zone)
            logging.info(f"Configured zone: {zone.name} (IP: {zone.ip}, Min: {zone.min_threshold} kPa, Max: {zone.max_threshold} kPa)")
            
        return zones
    except requests.RequestException as e:
        logging.error(f"Error fetching zones from API: {str(e)}")
        return []

if __name__ == "__main__":
    logging.info("Starting pressure monitoring system")
    logging.info(f"Configuration: CHECK_INTERVAL={CHECK_INTERVAL}s, NOTIF_INTERVAL={NOTIF_INTERVAL}s")
    
    while True:
        try:
            zones = load_zones_from_api()
            for zone in zones:
                check_zone_thresholds(zone)
            time.sleep(CHECK_INTERVAL)
        except Exception as e:
            logging.error(f"Error in main loop: {str(e)}")
            time.sleep(CHECK_INTERVAL)
