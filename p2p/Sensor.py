from p2p.Message import Message
from p2p.config import LOGGING_ENABLED
import rpyc
import netifaces as ni
import logging
import sys
import threading


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
        c = rpyc.connect(server_id, 9600)
        msg = Message(self.id, self.servers[0], data)
        result = c.root.receive_data(msg)
        return result

    #sorban megpróbál küldeni az összes szervernek
    def send_data(self, data):
        for server_id in self.servers:
            self.log('Sending data', data, 'to', server_id)
            success = self.try_to_send_data(server_id, data)
            if not success:
                self.log('Sending was unsuccessful.')
            if success:
                break
        else:
            self.log('Could not send data to any server.')
            raise Exception("Could not send data to any server.")
    
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
    

def rpyc_start():
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(this, port=9600, listener_timeout=600, logger=logging.getLogger())
    t.start()

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    this = SensorService()
    x = threading.Thread(target=rpyc_start, daemon=True)
    x.start()
    default_server = ni.gateways()['default'][ni.AF_INET][0]
    c = rpyc.connect(default_server, 9600)
    c.root.addSensor(this.id)
    this.log('Sensor started: ', this.id)
    this.log('With default server: ', default_server)
