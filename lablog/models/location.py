import humongolus as orm
import humongolus.field as field

class LocationInterface(orm.EmbeddedDocument):

    interface = field.DynamicDocument()

class Location(orm.Document):
    _db = 'lablog'
    _collection = 'locations'

    name = field.Char()
    description = field.Char()
    geo = field.Geo()
    property_id = field.Char()
    interfaces = orm.List(type=LocationInterface)
    zipcode = field.Char()

    def get_interface_data(self, db, _from="2d"):
        vals = {}
        for i in self.interfaces:
            inter = i.interface
            vals[inter.__class__.__name__] = inter.get_values(db, _from)

        return vals

    def get_interface(self, interface):
        inte = None
        for i in self.interfaces:
            inter = i._get('interface')._value.get('cls').split(".")[-1]
            self.logger.info(inter)
            if inter == interface:
                inte = i.interface
                break
        return inte
