from p2p.Message import Message
from p2p.config import LOGGING_ENABLED
import rpyc
import netifaces as ni
import logging
import sys
import threading
import random
import string
import time


class SensorService(rpyc.Service):
    def __init__(self):
        self.id = ni.ifaddresses('eth0')[ni.AF_INET][0]['addr']
        self.servers = []
        self.new_data = []
        self.has_new_data = False
        self.received_messages = []
        self.message_to_send = ""

    def __str__(self):
        """
        Stringge alakitas, kiiratashoz kell
        """
        return f'Sensor_{self.id}'

    def log(self, *args, **kwargs):
        """
        Fontosabb esemenyek logolasa konzolra, ha a config-ban LOGGING_ENABLED engedelyezve van.
        Hivas szintaxisa: print-tel megegyezoen
        :param args: kiirando dolgok felsorolasa
        :param kwargs: elvalaszto karakter megadhato sep=' ' formaban, alapertelmezes: szokoz
        """
        if LOGGING_ENABLED:
            if 'sep' in kwargs:
                sep = kwargs.get('sep')
            else:
                sep = ' '
            msg = sep.join(map(str, args))
            print('Sensor ', self.id, ': ', msg, sep='')

    #szerverek tömbjének újramegadása
    def exposed_redefine_servers(self, servers_array):
        self.log('New server list:', servers_array)
        self.servers = servers_array
    
    #kikeresi a küldendő adatot a meglévő még nem küldött adatok kozül
    def search_data_to_send(self, data):
        for d in self.new_data:
            if data == d:
                data_to_send = data
                break
        else:
            raise Exception(data + " sensor has not the excepted data in new data.")
        return data_to_send
    
    #megpróbál küldeni a szervernek
    def try_to_send_data(self, server_id, data):
        try:
            c = rpyc.connect(server_id, 9600)
            msg = Message(self.id, self.servers[0], data)
            result = c.root.receive_data(msg)
        except Exception as ex:
            self.log('RPC failed:', ex)
            result = False
        return result

    #sorban megpróbál küldeni az összes szervernek
    def send_data(self, data):
        success = False
        while not success:
            for server_id in self.servers:
                self.log('Sending data ', data, ' to ', server_id)
                success = self.try_to_send_data(server_id, data)
                if not success:
                    self.log('Sending was unsuccessful.')
                if success:
                    break
            else:
                self.log('Could not send data to any server.')
                time.sleep(10)
    
    def receive_msg(self, message):
        self.log('Received message', message)
        self.received_messages.__add__(message)

    #üzenetküldés próbája az összes szerver felé
    def send_message(self, message):
        for server_id in self.servers:
            self.log('Sending message ', message, ' to ', server_id)
            success = self.try_to_send_data(server_id, message)
            if success:
                break
        else:
            raise Exception("Could not send message to any server.")

    def random_data(self):
        """Generate a random string of letters and digits """
        #while True:
        #    time.sleep(10)
        chars = string.ascii_letters + string.digits
        data = ''.join(random.choice(chars) for i in range(20))
        print(data)
        self.send_data(data)
            #threading.Timer(10, random_data, sensor_instance).start()
    

def generate_data():
    this.random_data()
    threading.Timer(10.0, generate_data).start()


def rpyc_start(sensor_instance):
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(sensor_instance, port=9600, listener_timeout=600, logger=logging.getLogger())
    t.start()


if __name__ == "__main__":
    #fo peldany letrehozasa es szal inditasa az rpyc szervernek
    this = SensorService()
    x = threading.Thread(target=rpyc_start, args=(this,), daemon=True)
    x.start()
    default_gateway = ni.gateways()['default'][ni.AF_INET][0]
    this.log('Default server: ', default_gateway)
    c = rpyc.connect(default_gateway, 9600)
    c.root.add_sensor(this.id)
    this.log('Sensor started!')
    #y = threading.Thread(target=random_data, args=(this,), daemon=True)
    #y.start()
    generate_data()
    x.join()
