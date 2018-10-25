#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import getopt
import paho.mqtt.client as mqtt
##Indicator
import signal
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, AppIndicator3
import threading
from threading import Thread, Lock
from gi.repository import GObject
gi.require_version('Notify', '0.7')
from gi.repository import Notify

APP_NAME = 'mqtt-appindicator'

class Indicator():
    def __init__(self):
        self.app = APP_NAME
        defaultIcon = "yd-ind-idle"


        self.testindicator = AppIndicator3.Indicator.new(
            self.app, defaultIcon,
            AppIndicator3.IndicatorCategory.OTHER)
        self.testindicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)       
        self.testindicator.set_menu(self.create_menu())

        self.mqttc = MyMQTTClass("Python Client")

    def main(self):
        self.mqttc.start()
        Gtk.main()

    def create_menu(self):
        self.menu = Gtk.Menu()
        
        item_quit = Gtk.MenuItem('Quit')
        item_quit.connect('activate', self.stop)
       
        kapiButton = Gtk.MenuItem('Kapıyı Aç')
        kapiButton.connect('activate', self.kapiAc)
        
        ##item_purple = Gtk.MenuItem('Purple')
        ##item_purple.connect('activate', self.purple)
        
        separator = Gtk.SeparatorMenuItem()
        separator.show()

        self.status = Gtk.MenuItem('')
        #status.show()

        self.menu.append(kapiButton)
        ##self.menu.append(item_purple)
        self.menu.append(separator)
        self.menu.append(self.status)
        self.menu.append(item_quit)
        self.menu.show_all()
        return self.menu

    def stop(self, source):
        self.mqttc.killConnection()
        Gtk.main_quit()
        
    def set_icon(self, icon):
        self.testindicator.set_icon(icon)
    
    def update_status(self, msg):
        self.status.get_child().set_text(msg)

    def kapiAc(self, source):
        self.mqttc.publishTopic("/melih/deneme", "ON")

class MyMQTTClass(threading.Thread):
    def __init__(self, clientid=None):
        threading.Thread.__init__(self)
        self._mqttc = mqtt.Client(clientid)
        self._mqttc.on_message = self.mqtt_on_message
        self._mqttc.on_connect = self.mqtt_on_connect
        self._mqttc.on_publish = self.mqtt_on_publish
        self._mqttc.on_subscribe = self.mqtt_on_subscribe
        self._mqttc.on_disconnect = self.mqtt_on_disconnect

    def publishTopic(self, topic, msg):
        self._mqttc.publish(topic, msg)

    def killConnection(self):
        self._mqttc.disconnect()

    def mqtt_on_disconnect(self, mqttc, userdata, rc):
        # define what happens after disconnect
        show_notify("test")

    #def mqtt_on_connect(self, mqttc, obj, flags, rc):
       # print("rc: "+str(rc))

    def mqtt_on_connect(self, mqttc, obj, flags, rc):
        if rc == 0:
            msg = 'Connected.'
            self._mqttc.subscribe("/melih/deneme", 0)
            self._mqttc.subscribe("/melih/led", 0)
            set_icon("yd-ind-error")
        else:
            msg = 'Connection unsuccessful.'
        update_status(msg)

    def mqtt_on_message(self, mqttc, obj, msg):
        print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))
        show_notify(("Konu: "+msg.topic+" Mesaj: "+str(msg.payload, "utf-8")), True)

    def mqtt_on_publish(self, mqttc, obj, mid):
        print("mid: "+str(mid))
    def mqtt_on_subscribe(self, mqttc, obj, mid, granted_qos):
        print("Subscribed: "+str(mid)+" "+str(granted_qos))
    def mqtt_on_log(self, mqttc, obj, level, string):
        print(string)
   
    def run(self):
        # try to connect
        try:
            update_status("Connecting...")
            self._mqttc.connect_async("iotmelih.duckdns.org", 1883, 60)
            # keep connected to broker
            self._mqttc.loop_forever()
        except getopt.GetoptError as e:
            update_status("Error")

def update_status(msg):
    #GObject.idle_add(ind.update_status, msg)
    ind.update_status(msg)

def set_icon(icon):
    #GObject.idle_add(ind.update_status, msg)
    ind.set_icon(icon)

def show_notify(msg, beeps=False):
    if beeps is True:
        beep()
        
    bildiriMesaj=Notify.Notification.new("Mqtt Notification", msg, "yd-ind-idle")
    bildiriMesaj.show()
    
def beep():
    print ("\a")

Notify.init(APP_NAME)
ind = Indicator()
ind.main()
##signal.signal(signal.SIGINT, signal.SIG_DFL)