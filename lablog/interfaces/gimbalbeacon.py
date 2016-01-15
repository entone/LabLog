from lablog.interfaces import Interface
from lablog.util import aes
from lablog import config
from lablog import messages
from datetime import datetime
import humongolus.field as field
import logging
import json

class GimbalBeacon(Interface):
    exchange = messages.Exchanges.presence
    measurement_key = "beacon"

    name = field.Char()

    def data(self, data=None):
        return data

    def parse_data(self, data):
        points = []
        points.append(dict(
            measurement="{}.{}".format(self.measurement_key, data.get("triggering_event").lower()),
            tags=dict(
                interface=str(self._id),
                receiver_name=data.get("receiver_name"),
                receiver_id=data.get("receiver_id"),
                transmitter_name=data.get("transmitter_name"),
                transmitter_id=data.get("transmitter_id"),
                signal_strength=int(data.get("signal_strength")),
                latitude=float(data.get("latitude", 0)),
                longitude=float(data.get("longitude", 0)),
                location_accuracy=data.get("location_accuracy"),
                location_fix_time=data.get("location_fix_time"),
                battery_level=int(data.get("battery_level", 0)),
                temperature=float(data.get("temperature", 0)),
                receiver_owner_organization=data.get("receiver_owner_organization"),
                transmitter_owner_organization=data.get("transmitter_owner_organization"),
            ),
            time=data.get("time", datetime.utcnow()),
            fields=dict(
                value=int(data.get("dwell_time", 0))
            )
        ))
        logging.info(points)
        return points
