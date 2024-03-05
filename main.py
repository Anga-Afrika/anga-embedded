import machine
import dht
from umqtt.simple import MQTTClient
import ubinascii
import ujson
import utime

CLIENT_ID = ubinascii.hexlify(machine.unique_id())
MQTT_SERVER = "6864ec5da672434b94038fa5f1fbc629.s1.eu.hivemq.cloud"
MQTT_TELEMETRY_TOPIC = f"iot/device/telemetry"
MQTT_CONTROL_TOPIC = f"iot/device/control"

USERNAME = "vivian347"
PASSWORD = "chech!kE123"

#DHT22 sensor setup
DHT_PIN = machine.Pin(4)
FLASH_LED = machine.Pin(2, machine.Pin.OUT)

# Methods
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
    CLIENT_ID, MQTT_SERVER, user=USERNAME, password=PASSWORD, ssl = True, ssl_params={'server_hostname': MQTT_SERVER})
    mqtt_client.set_callback(did_receive_callback)
    mqtt_client.connect()
    print("Connected!", end="")
    mqtt_client.subscribe(MQTT_CONTROL_TOPIC)
    return mqtt_client

def create_control_json_data(command, command_id):
    data = ujson.dumps({
        "device_id": CLIENT_ID,
        "command_id": command_id,
        "command": command,
    })
    return data

def create_json_data(temperature, humidity):
    data = ujson.dumps({
        "device_id": CLIENT_ID,
        "temperature": temperature,
        "humidity": humidity,
        "type": "sensor"
    })
    return data

def mqtt_client_publish(topic, data):
    print("\nUpdating MQTT Broker...")
    mqtt_client.publish(topic, data)
    print(data)


# Main Logic

mqtt_client = connect_to_mqtt()
dht_sensor = dht.DHT22(DHT_PIN)

telemetry_data_old = ""

while True:
    mqtt_client.check_msg()
    print(". ", end="")
    FLASH_LED.on()
    try:
        dht_sensor.measure()
    except OSError as e:
        print(f"Failed to read sensor data: {e}")
        continue
    utime.sleep(0.2)
    FLASH_LED.off()

    temperature = dht_sensor.temperature()
    humidity = dht_sensor.humidity()
    telemetry_data_new = create_json_data(temperature, humidity)

    if telemetry_data_new != telemetry_data_old:
        mqtt_client_publish(MQTT_TELEMETRY_TOPIC, telemetry_data_new)
        telemetry_data_old = telemetry_data_new
    
    utime.sleep(0.1)

