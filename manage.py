from flask import Flask, url_for
from flask.ext.script import Manager, Command, Option
from lablog import config
from lablog.app import App
from lablog import db
from lablog.models.location import Beacon
from lablog.util.gimbal import Gimbal
from slugify import slugify
import humongolus
import requests
import logging
import json
import csv

logging.basicConfig(level=logging.INFO)
app = App()
manager = Manager(app)
MONGO = db.init_mongodb()
humongolus.settings(logging, MONGO)

class RunWorker(Command):

    def run(self):
        logging.info("command!")

class InitApplication(Command):

    def run(self):
        logging.info("Initializing Application...")
        app.configure_dbs()
        from lablog.triggers.node import CO2
        from lablog.triggers.lab import Presence
        from lablog.triggers.energy import InputFrequency
        try:
            c = CO2()
            c.name = 'notify slack c02'#unique
            c.key = 'node.co2'
            c.save()
            logging.info(c.key)
            logging.info(c.name)
        except: pass
        try:
            c = Presence()
            c.name = 'notify slack presence'#unique
            c.key = 'presence'
            c.save()
        except: pass
        try:
            c = InputFrequency()
            c.name = 'check input frequency'#unique
            c.key = 'energy.ups.input_frequency'
            c.save()
        except: pass
        logging.info("Initialization Complete.")


class CreateBeacons(Command):

    def run(self):
        bad = []
        places = {}
        content = [f.strip() for f in open("data/Order4204.csv")]
        logging.info(content)
        count = 0
        for b in Beacon.find({'level':3}):
            b.id = b.id.replace("-", "")
            id = "{}-{}".format(b.id[:4], b.id[4:]).upper()
            logging.info(id)
            if id in content and b.place and b.place.lower() != 'duplicate':
                place_beacons = places.setdefault(slugify(b.place.lower().strip()), [])
                place_beacons.append(id)
                logging.info("Match")
            else:
                bad.append(id)
                logging.info("No Match")

        logging.info(bad)
        logging.info(json.dumps(places))
        gimbal = Gimbal(auth_key=config.GIMBAL_API_KEY)
        for k,v in places.iteritems():
            for b in v:
                name = "{}-{}".format(k, b)
                logging.info("Creating Beacon: {}".format(name))
                gimbal.create_beacon(b, name)
            logging.info("Creating Place: {}".format(k))
            gimbal.create_place(k, v)

class CreateGeofence(Command):

    GOOGLE_GEOCODE_API = "https://maps.googleapis.com/maps/api/geocode/json"
    KEY = "AIzaSyDj7cxNIp2DLWoZUDJblwaGohLah8cLnt4"
    def run(self):
        gimbal = Gimbal(auth_key=config.GIMBAL_API_KEY)
        with open('data/dostuff_venues_021816.tsv', 'rb') as tsvfile:
            venues = csv.reader(tsvfile, delimiter='\t', quotechar='|')
            next(venues)
            for v in venues:
                address = "{}, {}".format(v[5], v[3])
                name = v[1]
                attributes={
                    'address':v[5],
                    'city':v[3]
                }
                logging.info(name)
                logging.info(attributes)
                address = "{}, {}".format(v[5], v[3])
                res = requests.get(self.GOOGLE_GEOCODE_API, params={'components':'country:US', 'address':address, 'key':self.KEY})
                logging.info(json.dumps(res.json()))
                coords = res.json()['results'][0]['geometry']['location']
                logging.info(coords)
                geofence = {
                    "shape": "CIRCLE",
                    "radius": 100,
                    "center": {
                        "latitude": coords['lat'],
                        "longitude": coords['lng']
                    },
                    "points": None
                }
                gimbal.create_place(name=name, geofence=geofence, attributes=attributes)



manager.add_command('command', RunWorker())
manager.add_command('init_app', InitApplication())
manager.add_command('create_beacons', CreateBeacons())
manager.add_command('create_geofence', CreateGeofence())
#python manager.py command

if __name__ == "__main__":
    manager.run()
