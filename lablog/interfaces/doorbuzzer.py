from lablog.interfaces import Interface
from lablog import messages
import humongolus.field as field
import requests

class DoorBuzzer(Interface):
    exchange = messages.Exchanges.node
    measurement_key = 'actuator.door'

    buzzer_url = field.Char()

    def data(self, data=None): pass

    def parse_data(self, data): pass

    def open(self):
        res = requests.post(self.buzzer_url, data="ON", timeout=100)
