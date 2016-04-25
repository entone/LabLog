from lablog.interfaces import Interface
from lablog import messages
import humongolus.field as field
import logging
import socket

UDP_IP = "192.168.1.6"
UDP_PORT = 5683;
MESSAGE = "ON"



class DoorBuzzer(Interface):
    exchange = messages.Exchanges.node
    measurement_key = 'actuator.door'

    buzzer_url = field.Char()

    def data(self, data=None): pass

    def parse_data(self, data): pass

    def open(self):
        logging.info("OPEN")
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))
