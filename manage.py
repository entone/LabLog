from flask import Flask, url_for
from flask.ext.script import Manager, Command, Option
from lablog import config
from lablog.app import App
from lablog import db
from lablog.models.location import Beacon
from slugify import slugify
import humongolus
import logging
import json

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


class CompareBeacons(Command):

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




manager.add_command('command', RunWorker())
manager.add_command('init_app', InitApplication())
manager.add_command('compare_beacons', CompareBeacons())
#python manager.py command

if __name__ == "__main__":
    manager.run()
