from p2p.Message import Message
from p2p.config import NUM_REPLICAS, LOGGING_ENABLED
import rpyc
import rpyc.utils.registry
import netifaces as ni
import logging
import sys
import threading


class StorageServerService(rpyc.Service):

    def __init__(self, alive):
        self.alive = alive
        self.id = ni.gateways()['default'][ni.AF_INET][0]
        self.data = {}
        self.other_data = {}
        self.sensors = []
        self.neighbour_servers = []
        self.dead_servers_data = {}

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
        c = rpyc.connect(sensor_id, 9600)
        c.root.redefine_servers(self.id + self.neighbour_servers)

    #még csak egyszerűen hozzáadjuk a szomszédok listájához
    def exposed_add_neighbour_server(self, server_id):
        if server_id not in self.neighbour_servers:
            self.log('Neighbour server added:', server_id)
            self.neighbour_servers.append(server_id)
            for sensor_id in self.sensors:
                c = rpyc.connect(sensor_id, 9600)
                c.root.redefine_servers(self.id + self.neighbour_servers)

    #megkapja az adatot és eltárolja a megfelelő listában
    def exposed_receive_data(self, msg):
        #tud-e adatot fogadni
        if self.alive:
            #saját szenzortól jön az adat
            if msg.parent_server_id == self.id:
                self.log('Received own data', msg)
                if msg.sensor_id not in self.data:
                    self.data[msg.sensor_id] = []
                if msg.content not in self.data[msg.sensor_id]:
                    self.data[msg.sensor_id].append(msg.content)
                    self.create_replicas(msg)
                return True

            #nem saját senzortól jön
            else:
                #a szenzőr szülő szervere él akkor azért kapja ez a szerver az adatot hogy duplikáltan tároljuk el az adatot
                if msg.is_replica == True:
                    self.log('Received other data', msg)
                    if msg.parent_server_id not in self.other_data:
                        self.other_data[msg.parent_server_id]={}
                    if msg.sensor_id not in self.other_data[msg.parent_server_id]:
                        self.other_data[msg.parent_server_id][msg.sensor_id]=[]
                    if msg.content not in self.other_data[msg.parent_server_id]:
                        self.other_data[msg.parent_server_id][msg.sensor_id].append(msg.content)
                    return True
                #a szenzor szülő szervere leállt és ezért kapja ez a szerver az adatot
                else:
                    self.log('Received dead data', msg)
                    if msg.parent_server_id not in self.dead_servers_data:
                        self.dead_servers_data[msg.parent_server_id]={}
                    if msg.sensor_id not in self.dead_servers_data[msg.parent_server_id]:
                        self.dead_servers_data[msg.parent_server_id][msg.sensor_id]=[]
                    if msg.content not in self.dead_servers_data[msg.parent_server_id]:
                        self.dead_servers_data[msg.parent_server_id][msg.sensor_id].append(msg.content)
                    self.create_replicas(msg)
                    return True
        else:
            return False

    def send_msg(self, server_id, msg):
        for nei_server_id in self.neighbour_servers:
            if nei_server_id == server_id:
                c = rpyc.connect(server_id, 9600)
                res = c.root.receive_data(msg)
                if not res:
                    raise Exception(server_id + 'server is dead')
                break
        else:
            raise Exception('Could not find server with id ' + str(server_id))

    #ezzel tudja a saját szenzorainak az adatait elküldeni hogy azok duplikálva tárolódjanak
    def send_data_to_duplicate(self, msg):
        for server_id in self.neighbour_servers:
            for sensor_id in self.data.keys():
                msg = Message(sensor_id, self.id, self.data[sensor_id], self.alive)
                self.send_msg(server_id, msg)

    #ezzel szólunk hogy egy szerver megint él vagy új szerver lépett be
    def exposed_receive_new_server_is_alive(self, server_id):
        if server_id not in self.neighbour_servers:
            self.neighbour_servers.append(server_id)
        if server_id in self.dead_servers_data:
            self.repair_dead_server(server_id)

    #ezzel kap értesítést hogy az egyik szerver leállt
    def receive_server_is_dead(self, server_id):
        self.neighbour_servers.remove(server_id)

    def repair_dead_server(self, server_id):
        for sensor_id in self.dead_servers_data[server_id]:
            while self.dead_servers_data[server_id][sensor_id]:
                data = self.dead_servers_data[server_id][sensor_id].pop()
                msg = Message(sensor_id, server_id, data, False)
                self.send_msg(server_id, msg)
        self.dead_servers_data.pop(server_id)

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
            c = rpyc.connect(server_id, 9600)
            if c.root.receive_data(msg):
                n_replicas_created += 1
            if n_replicas_created == NUM_REPLICAS:
                break

    def change_alive_state(self, alive):
        self.log('Alive state changed to ', alive)
        if not alive:
            self.alive = False
        else:
            self.alive = True
            # collect missed data
            for server_id in self.neighbour_servers:
                c = rpyc.connect(server_id, 9600)
                c.root.receive_new_server_is_alive(self.id)


def rpyc_start():
    #regisztralas
    from rpyc.utils.registry import TCPRegistryClient
    registrar = TCPRegistryClient("10.10.10.1")
    this.log('Registering service, servers so far: ', registrar.discover("StorageServer"))
    #rpyc szerver inditasa
    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(this, port=9600, listener_timeout=600, registrar=registrar, logger=logging.getLogger())
    t.start()


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    this = StorageServerService(alive=True)
    x = threading.Thread(target=rpyc_start, daemon=True)
    x.start()
    this.log('Server started: ', this.id)

