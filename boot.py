# boot.py -- run on boot-up
# boot.py -- run on boot-up
import network, utime, machine
import ubinascii
from umqtt.simple import MQTTClient

SSID = "RIZZY"
SSID_PASSWORD = "njihia2002"

def do_connect():
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        sta_if.connect(SSID, SSID_PASSWORD)
        while not sta_if.isconnected():
            print("Attempting to connect to network...")
            utime.sleep(1)
    print ('Connected! Network config:', sta_if.ifconfig())

print ("Connecting to your WIFI network....")
do_connect()