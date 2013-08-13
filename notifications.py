import time
import os
import signal
import dbus
import dbus.service
import gobject
import json
from HTMLParser import HTMLParser
from dbus.mainloop.glib import DBusGMainLoop

DBusGMainLoop(set_as_default=True)
session_bus = dbus.SessionBus()

class Test(dbus.service.Object):
    def __init__(self, interface, *args, **kwargs):
        self.message = None
        self.interface = interface
        self.id = 0
        dbus.service.Object.__init__(self, *args, **kwargs)

    @dbus.service.method(dbus_interface='org.freedesktop.Notifications', out_signature='ssss')
    def GetServerInformation(self):
        return ["i3et", "alistair@popple.id.au", "0.1", "1.2"]

    @dbus.service.method(dbus_interface='org.freedesktop.Notifications', out_signature='as')
    def GetCapabilities(self):
        return ['']

    @dbus.service.method(dbus_interface='org.freedesktop.Notifications', out_signature='u', \
                             in_signature='susssasvi')
    def Notify(self, app_name, replaces_id, app_icon, summary, body, actions, hints, expire_timeout):
        h = HTMLParser()
        summary = h.unescape(summary)
        body = h.unescape(body)

        self.message = str(summary)
        if len(body):
            self.message += ": " + body

        self.color = "#ffffff"
        self.bg_color = "#ff0000"
        self.interface.data_updated(self)
        gobject.timeout_add(200, self.change_bg_color)
        gobject.timeout_add(4000, self.change_color)
        
        if replaces_id != 0:
            return replaces_id
        else:
            self.id += 1
            return self.id

    def change_color(self):
        self.color = "#777777"
        self.interface.data_updated(self)
        return False

    def change_bg_color(self):
        self.bg_color = None
        self.interface.data_updated(self)
        return False

    def get_data(self):
        result = {'_id': 'Test', 'full_text': self.message, 'color': self.color}

        if self.bg_color is not None:
            result['bg_color'] = self.bg_color
            
        return result

class Main(object):
    def __init__(self):
        self.fifo = os.open("/tmp/i3et", os.O_WRONLY)

    def run(self):
        name = dbus.service.BusName("org.freedesktop.Notifications", session_bus)
        self.test = Test(self, session_bus, '/org/freedesktop/Notifications')
        gobject.MainLoop().run()

    def data_updated(self, module):
        data = [{'module': 'notify'}, module.get_data()]
        os.write(self.fifo, json.dumps(data))

if __name__ == "__main__":
    x = Main()
    x.run()
