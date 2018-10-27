#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
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
import configparser
import json

##Json Config
with open('menu_entries.json', 'r') as f:
    menuEntries = json.load(f)

with open('notification_entries.json', 'r') as f:
    notificationEntries = json.load(f)

##Ini Config
config = configparser.ConfigParser()
config.read('CONFIG.INI')

##App Name
APP_NAME = config['DEFAULT']['AppName']

class Indicator():
    def __init__(self):
        self.app = APP_NAME
        defaultIcon = os.path.abspath('icons/baseline-cloud_queue-24px.svg')
        ##defaultIcon = config['DEFAULT']['DefaultIcon']
        print(defaultIcon)

        self.testindicator = AppIndicator3.Indicator.new(
            self.app, defaultIcon,
            AppIndicator3.IndicatorCategory.OTHER)
        self.testindicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)       
        self.testindicator.set_menu(self.create_menu())

        self.mqttc = MyMQTTClass(config['mqtt']['mqtt_client_name'])

    def main(self):
        self.mqttc.start()
        Gtk.main()

    def create_menu(self):
        self.menu = Gtk.Menu()
        
        item_quit = Gtk.MenuItem('Quit')
        item_quit.connect('activate', self.stop)

        ##item_purple = Gtk.MenuItem('Purple')
        ##item_purple.connect('activate', self.purple)
        
        separator = Gtk.SeparatorMenuItem()
        separator.show()

        self.status = Gtk.MenuItem('')
        #status.show()

        for entry in menuEntries:
            menuItemDynamic = Gtk.MenuItem(entry['showName'])
            menuItemDynamic.connect('activate', self.buttonConnector, entry['publishChannelName'], entry['publishMessage'])
            self.menu.append(menuItemDynamic)

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
    
    def buttonConnector(self, *data):
        self.mqttc.publishTopic(data[1], data[2])

    def kapiAc(self, source, testId):
        self.mqttc.publishTopic("/melih/deneme", testId)

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
        show_notify("uyarı", "test")

    #def mqtt_on_connect(self, mqttc, obj, flags, rc):
       # print("rc: "+str(rc))

    def mqtt_on_connect(self, mqttc, obj, flags, rc):
        if rc == 0:
            msg = 'Connected.'
            
            for entry in notificationEntries:
                self._mqttc.subscribe(entry['subscribeChannel'], 0)

            set_icon("yd-ind-error")
        else:
            msg = 'Connection unsuccessful.'
        update_status(msg)

    def mqtt_on_message(self, mqttc, obj, msg):
        print(msg.topic+" "+str(msg.qos)+" "+str(msg.payload))

        for entry in notificationEntries:
                if(entry['subscribeChannel'] == msg.topic and entry['notificationEnable']):
                    show_notify(entry['notificationTitle'], ("Konu: "+msg.topic+" Mesaj: "+str(msg.payload, "utf-8")), True)

        

    def mqtt_on_publish(self, mqttc, obj, mid):
        print("Published: : "+str(mid))
    def mqtt_on_subscribe(self, mqttc, obj, mid, granted_qos):
        print("Subscribed: "+str(mid)+" "+str(granted_qos))
    def mqtt_on_log(self, mqttc, obj, level, string):
        print(string)
   
    def run(self):
        # try to connect
        try:
            update_status("Connecting...")
            self._mqttc.connect_async(config['mqtt']['broker_host_name'], config.getint('mqtt', 'broker_host_port'), 60)
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

def show_notify(title, msg, beeps=False):
    if beeps is True:
        beep()
        
    bildiriMesaj=Notify.Notification.new(title, msg, "yd-ind-idle")
    bildiriMesaj.show()
    
def beep():
    print ("\a")

Notify.init(APP_NAME)
ind = Indicator()
ind.main()
##signal.signal(signal.SIGINT, signal.SIG_DFL)
