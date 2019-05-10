from p2p.Message import Message
from p2p.config import NUM_REPLICAS, LOGGING_ENABLED
import rpyc
import rpyc.utils.registry
import netifaces as ni
import logging
import sys
import threading


class StorageServerService(rpyc.Service):

    def __init__(self):
        self.id = ni.gateways()['default'][ni.AF_INET][0]
        self.default_gateway = ni.gateways()['default'][ni.AF_INET][0]
        self.data = {}
        self.backup_data = {}
        self.recovery_data = {}
        self.sensors = []
        self.neighbour_servers = []

    def __str__(self):
        """
        Stringge alakitas, kiiratashoz kell
        """
        return f'Server_{self.id}'

    def __repr__(self):
        return f'Server_{self.id}'

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
            print('Server ', self.id, ': ', msg, sep='')

    #még csak egyszerűen hozzáadjuk a szenzor listához
    def exposed_add_sensor(self, sensor_id):
        self.log('Sensor added:', sensor_id)
        self.sensors.append(sensor_id)

    #még csak egyszerűen hozzáadjuk a szomszédok listájához
    def exposed_refresh_neighbour_list(self, new_neighbour_list):
        self.neighbour_servers = []
        for server_id in new_neighbour_list:
            if server_id != self.default_gateway:
                self.neighbour_servers.append(server_id)
        self.log('Refreshed neighbour server list:', self.neighbour_servers)

    #sajat id-vel kiegeszitett lista kuldese a szenzornak
    def send_neighbour_list(self):
        for sensor_id in self.sensors:
            neighbour_list = self.neighbour_servers
            neighbour_list.insert(0, self.id)
            try:
                self.log('Sending neighbour list to:', sensor_id)
                c = rpyc.connect(sensor_id, 9600)
                c.root.redefine_servers(neighbour_list)
            except Exception as ex:
                self.log('Neighbour list sending failed to:', sensor_id)
            threading.Timer(10.0, self.send_neighbour_list).start()

    #megkapja az adatot és eltárolja a megfelelő listában
    def exposed_receive_data(self, msg):
        #saját szenzortól jön az adat
        if msg.parent_server_id == self.id:
            self.log('Received own data:', msg)
            if msg.sensor_id not in self.data:
                self.data[msg.sensor_id] = []
            if msg.content not in self.data[msg.sensor_id]:
                self.data[msg.sensor_id].append(msg.content)
                #self.create_replicas(msg)
            return True
        #nem saját senzortól jön
        else:
            #a szenzőr szülő szervere él akkor azért kapja ez a szerver az adatot hogy duplikáltan tároljuk el az adatot
            if msg.is_replica:
                self.log('Received backup data:', msg)
                if msg.parent_server_id not in self.backup_data:
                    self.backup_data[msg.parent_server_id] = {}
                if msg.sensor_id not in self.backup_data[msg.parent_server_id]:
                    self.backup_data[msg.parent_server_id][msg.sensor_id] = []
                if msg.content not in self.backup_data[msg.parent_server_id]:
                    self.backup_data[msg.parent_server_id][msg.sensor_id].append(msg.content)
                return True
            #a szenzor szülő szervere leállt és ezért kapja ez a szerver az adatot
            else:
                self.log('Received recovery data:', msg)
                if msg.parent_server_id not in self.recovery_data:
                    self.recovery_data[msg.parent_server_id] = {}
                if msg.sensor_id not in self.recovery_data[msg.parent_server_id]:
                    self.recovery_data[msg.parent_server_id][msg.sensor_id] = []
                if msg.content not in self.recovery_data[msg.parent_server_id]:
                    self.recovery_data[msg.parent_server_id][msg.sensor_id].append(msg.content)
                self.create_replicas(msg)
                return True

    #uzenet kuldese masik szervernek
    def send_message(self, server_id, msg):
        try:
            c = rpyc.connect(server_id, 9600)
            return c.root.receive_data(msg)
        except Exception:
            self.log('RPC failed, server is dead:', server_id)

    #ezzel tudja a saját szenzorainak az adatait elküldeni hogy azok duplikálva tárolódjanak
    def send_replicas(self):
        for server_id in self.neighbour_servers:
            for sensor_id in self.data.keys():
                msg = Message(sensor_id, self.id, self.data[sensor_id], True)
                self.send_message(server_id, msg)
        threading.Timer(30.0, self.send_replicas).start()

    def send_recoveries(self):
        for server_id in self.neighbour_servers:
            if server_id in self.recovery_data:
                for sensor_id in self.recovery_data[server_id]:
                    while self.recovery_data[server_id][sensor_id]:
                        data = self.recovery_data[server_id][sensor_id].pop()
                        msg = Message(sensor_id, server_id, data, False)
                        self.send_message(server_id, msg)
                self.recovery_data.pop(server_id)
        threading.Timer(30.0, self.send_recoveries).start()

    def create_replicas(self, msg):
        """
        Masolatok keszitese a kapott adatrol a szomszedos szerverekre
        :param msg: a kapott uzenet
        :return: None
        """
        n_replicas_created = 0
        # ha nem nekunk jott az adat eredetileg, akkor a sajat szerver nem aktiv
        msg.is_replica = True
        for server_id in self.neighbour_servers:
            if self.send_message(server_id, msg):
                n_replicas_created += 1
            if n_replicas_created == NUM_REPLICAS:
                break


def rpyc_start(server_instance):
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    #regisztralas
    from rpyc.utils.registry import TCPRegistryClient
    registrar = TCPRegistryClient(ip=server_instance.default_gateway)
    this.log('Registering service')
    #rpyc szerver inditasa
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(server_instance, port=9600, listener_timeout=60, registrar=registrar, logger=logging.getLogger())
    t.start()


if __name__ == "__main__":
    this = StorageServerService()
    x = threading.Thread(target=rpyc_start, args=(this,), daemon=True)
    x.start()
    this.log('Server started!')
    this.send_neighbour_list()
    this.send_replicas()
    x.join()
