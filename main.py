import machine
import dht
import utime
import ujson
import requests
import time
import ubinascii
from umqtt.simple import MQTTClient
from sim800l import SIM800L  # Assuming you have sim800l.py file for SIM800L communication

CLIENT_ID = ubinascii.hexlify(machine.unique_id())
MQTT_SERVER = "6864ec5da672434b94038fa5f1fbc629.s1.eu.hivemq.cloud"
MQTT_TELEMETRY_TOPIC = f"iot/device/telemetry"
MQTT_CONTROL_TOPIC = f"iot/device/control"

USERNAME = "vivian347"
PASSWORD = "chech!kE123"

EMAIL = "harunnjihia455@gmail.com"
AUTH_PASSWORD = "harun 123"


# DHT22 sensor setup
DHT_PIN = machine.Pin(4)
FLASH_LED = machine.Pin(2, machine.Pin.OUT)

# Initialize SIM800L GSM module
uart = machine.UART(2, baudrate=9600, tx=17, rx=16)  # UART2 on GPIO17 (TX) and GPIO16 (RX)
gsm = SIM800L(uart)

# Function to authenticate with backend
def authenticate_with_backend():
    payload = {"email": EMAIL, "password": AUTH_PASSWORD}
    try:
        response = requests.post("https://anga-ts1r.onrender.com/auth/jwt/create/", json=payload)
        if response.status_code == 200:
            auth_data = response.json()
            access_token = auth_data.get("access_token")
            if access_token:
                return access_token
            else:
                print("Missing access token in response.")
                return None
        else:
            print("Failed to authenticate. Status code:", response.status_code)
            return None
    except Exception as e:
        print("Exception while authenticating:", e)
        return None


def fetch_thresholds_with_token(access_token, retry_attempts=3, retry_delay=1):
    headers = {"Authorization": f"JWT {access_token}"}
    for attempt in range(1, retry_attempts + 1):
        try:
            response = requests.get("https://anga-ts1r.onrender.com/api/threshold/", headers=headers)
            if response.status_code == 200:
                thresholds = response.json()
                return thresholds
            else:
                print("Failed to fetch thresholds. Status code:", response.status_code)
                return None
        except Exception as e:
            print(f"Exception while fetching thresholds (attempt {attempt}):", e)
            if attempt < retry_attempts:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
    return None


# Function to publish data to MQTT broker
def mqtt_client_publish(topic, data):
    print("\nUpdating MQTT Broker...")
    mqtt_client.publish(topic, data)
    print(data)

# Function to read sensor data
def read_sensor_data():
    dht_sensor.measure()
    temperature = dht_sensor.temperature()
    humidity = dht_sensor.humidity()
    return temperature, humidity

# MQTT setup and callbacks
def did_receive_callback(topic, msg):
    print(f"\n\nData received! \ntopic = {topic}, message = {msg}")

    if topic == MQTT_CONTROL_TOPIC.encode():
        command_message = ujson.loads(msg.decode())['command']
        if command_message == 'status':
            print("Status command received!")
            global telemetry_data_old
            mqtt_client_publish(MQTT_TELEMETRY_TOPIC, telemetry_data_old)
        else:
            return

def connect_to_mqtt():
    print("Connecting to MQTT broker...", end="")
    mqtt_client = MQTTClient(
        CLIENT_ID, MQTT_SERVER, user=USERNAME, password=PASSWORD, ssl=True, ssl_params={'server_hostname': MQTT_SERVER})
    mqtt_client.set_callback(did_receive_callback)
    mqtt_client.connect()
    print("Connected!", end="")
    mqtt_client.subscribe(MQTT_CONTROL_TOPIC)
    return mqtt_client

# Main Logic

mqtt_client = connect_to_mqtt()
dht_sensor = dht.DHT22(DHT_PIN)

telemetry_data_old = ""

access_token = authenticate_with_backend()
while True:
    mqtt_client.check_msg()
    print(". ", end="")
    FLASH_LED.on()
    try:
        dht_sensor.measure()
    except OSError as e:
        print(f"Failed to read sensor data: {e}")
        continue
    utime.sleep(5)
    FLASH_LED.off()

    temperature, humidity = read_sensor_data()
    telemetry_data_new = ujson.dumps({
        "device_id": CLIENT_ID,
        "temperature": temperature,
        "humidity": humidity,
        "type": "sensor"
    })

    if telemetry_data_new != telemetry_data_old:
        mqtt_client_publish(MQTT_TELEMETRY_TOPIC, telemetry_data_new)
        telemetry_data_old = telemetry_data_new
    
    # Fetch thresholds from backend and check temperature and humidity
        thresholds = fetch_thresholds_with_token(access_token, retry_attempts=2, retry_delay=1)
        print("Thresholds:::::::::::", thresholds)
        if thresholds:
            if temperature > thresholds["temperature_high"]:
                # Send temperature alert via SMS
                phone_number = "0792386531"  # Replace with recipient's phone number
                message = "Temperature threshold exceeded: {:.1f}°C".format(temperature)
                gsm.send_sms(phone_number, message)
            if humidity > thresholds["humidity_high"]:
                # Send humidity alert via SMS
                phone_number = "0792386531"  # Replace with recipient's phone number
                message = "Humidity threshold exceeded: {:.1f}%".format(humidity)
                gsm.send_sms(phone_number, message)

        utime.sleep(6)