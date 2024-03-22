# import machine
# import time


# # Initialize UART for SIM800L communication
# uart = machine.UART(2, baudrate=9600, tx=17, rx=16)  # UART2 on GPIO17 (TX) and GPIO16 (RX)

# class SIM800L:
#     def __init__(self, uart):
#         self.uart = uart

#     def send_sms(self, phone_number, message):
#         # Command to set SMS mode
#         self.uart.write("AT+CMGF=1\r\n")
#         response = self.uart.readline()
#         if b'OK' not in response:
#             print("Failed to set SMS mode")
#             return False

#         # Command to set phone number
#         self.uart.write("AT+CMGS=\"{}\"\r\n".format(phone_number))
#         response = self.uart.readline()
#         if b'>' not in response:
#             print("Failed to set phone number")
#             return False

#         # Sending SMS message
#         self.uart.write("{}\r\n".format(message))
#         self.uart.write("\x1A")
#         print("Sending SMS...")
#         time.sleep(3)  # Adjust sleep time based on your module's responsiveness
#         response = self.uart.read(100)
#         if b'OK' not in response:
#             print("Failed to send SMS")
#             return False

#         print("SMS sent successfully")
#         return True


class SIM800L:
    def __init__(self, uart):
        self.uart = uart

    def send_sms(self, phone_number, message):
        # Command to set SMS mode
        self.uart.write("AT+CMGF=1\r\n")
        response = self.uart.readline()
        if b'OK' not in response:
            print("Failed to set SMS mode")
            return False

        # Command to set phone number
        self.uart.write("AT+CMGS=\"{}\"\r\n".format(phone_number))
        response = self.uart.readline()
        if b'>' not in response:
            print("Failed to set phone number")
            return False

        # Sending SMS message
        self.uart.write("{}\r\n".format(message))
        self.uart.write("\x1A")
        print("Sending SMS...")
        time.sleep(5)  # Adjust sleep time based on your module's responsiveness
        response = self.uart.read(100)
        if b'OK' not in response:
            print("Failed to send SMS")
            return False

        print("SMS sent successfully")
        return True


