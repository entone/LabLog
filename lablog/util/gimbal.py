import requests
import logging

GIMBAL_URL = "https://manager.gimbal.com/api"
API_VERSION = "v2"


class Gimbal(object):

    def __init__(self, auth_key):
        self.auth_key = auth_key

    def create_place(self, name, beacons):
        res = self.post("places", {'name':name, 'beacons':[{'factoryId':i} for i in beacons]})
        logging.debug(res)

    def create_beacon(self, id, name):
        res = self.post("beacons", {'name':name, 'factory_id':id})
        logging.debug(res)

    def post(self, endpoint, payload):
        url = "{}/{}/{}".format(GIMBAL_URL, API_VERSION, endpoint)
        logging.info("Sending Request: {}".format(url))
        res = requests.post(
            url,
            json=payload,
            headers={'Authorization', self.auth_key}
        )
        return res.json()
