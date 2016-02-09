import requests
import logging

GIMBAL_URL = "https://manager.gimbal.com/api"
API_VERSION = "v2"


class Gimbal(object):

    def __init__(self, auth_key):
        self.auth_key = auth_key

    def create_place(self, name, beacons):
        beacons = [b.replace("-", "") for b in beacons]
        beacons = [{'factoryId':"{}-{}".format(id[:4], id[4:]).upper()} for id in beacons]
        logging.info(beacons)
        res = self.post("places", {'name':name, 'beacons':beacons}, version=API_VERSION)
        logging.info(res)

    def create_beacon(self, id, name):
        id = id.replace("-", "").upper()
        id = "{}-{}".format(id[:4], id[4:])
        logging.info(id)
        res = self.post("beacons", {'name':name, 'factory_id':id})
        logging.info(res)

    def post(self, endpoint, payload, version=False):
        url = "{}/{}".format(GIMBAL_URL, endpoint)
        if version: url = "{}/{}/{}".format(GIMBAL_URL, version, endpoint)

        logging.info("Sending Request: {}".format(url))
        logging.info("Payload: {}".format(payload))
        res = requests.post(
            url,
            json=payload,
            headers={'Authorization': "Token token={}".format(self.auth_key)}
        )
        logging.info(res.text)
        return res.json()
