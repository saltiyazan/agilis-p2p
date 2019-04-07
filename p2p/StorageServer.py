from p2p.Message import Message
from p2p.config import NUM_REPLICAS
class StorageServer:

    def __init__(self, alive, id):
        self.alive = alive
        self.id = id
        self.data = {}
        self.other_data = {}
        self.sensors=[]
        self.neighbour_servers=[]
        self.dead_servers_data={}

    #még csak egyszerűen hozzáadjuk a szenzor listához
    def add_sensor(self,sensor):
        self.sensors.append(sensor)
        sensor.redefine_servers([self] + self.neighbour_servers)

    #még csak egyszerűen hozzáadjuk a szomszédok listájához
    def add_neighbour_server(self,server_id):
        self.neighbour_servers.append(server_id)
        for sensor in self.sensors:
            sensor.redefine_servers([self] + self.neighbour_servers)

    #megkapja az adatot és eltárolja a megfelelő listában
    def receive_data(self, msg):
        #tud-e adatot fogadni
        if self.alive:
            #saját szenzortól jön az adat
            if msg.parent_server_id==self.id:
                if msg.sensor_id not in self.data:
                    self.data[msg.sensor_id] = []
                self.data[msg.sensor_id].append(msg.content)
                self.create_replicas(msg)
                return True

            #nem saját senzortól jön
            else:
                #a szenzőr szülő szervere él akkor azért kapja ez a szerver az adatot hogy duplikáltan tároljuk el az adatot
                if msg.is_parent_alive == True:
                    if msg.parent_server_id not in self.other_data:
                        self.other_data[msg.parent_server_id]={}
                    if msg.sensor_id not in self.other_data[msg.parent_server_id]:
                        self.other_data[msg.parent_server_id][msg.sensor_id]=[]
                    self.other_data[msg.parent_server_id][msg.sensor_id].append(msg.content)
                    return True
                #a szenzor szülő szervere leállt és ezért kapja ez a szerver az adatot
                else:
                    if msg.parent_server_id not in self.dead_servers_data:
                        self.dead_servers_data[msg.parent_server_id]={}
                    if msg.sensor_id not in self.dead_servers_data[msg.parent_server_id]:
                        self.dead_servers_data[msg.parent_server_id][msg.sensor_id]=[]
                    self.dead_servers_data[msg.parent_server_id][msg.sensor_id].append(msg.content)
                    self.create_replicas(msg)
                    return True
        else:
            return False


    def send_msg(self,server_id,msg):
        res=self.neighbour_servers[server_id].receive_duplicated_data(msg)
        if not res:
            raise Exception(server_id+ 'szerver is dead')
    #ezzel tudja a saját szenzorainak az adatait elküldeni hogy azok duplikálva tárolódjanak

    def send_data_to_duplicate(self,msg):
        for szerver in self.neighbour_servers:
            for sensor in self.data.keys():
                msg=Message(sensor,self.id,self.data[sensor],self.alive)
                self.send_msg(szerver,msg)


    #ezzel szólunk hogy egy szerver megint él vagy új szerver lépett be
    def receive_new_server_is_alive(self,server_id):
        self.neighbour_servers.append(server_id)
        if server_id in self.dead_servers_data:
           self.repair_dead_server(server_id)

    #ezzel kap értesítést hogy az egyik szerver leállt
    def receive_server_is_dead(self,server_id):
        self.neighbour_servers.remove(server_id)

    def repair_dead_server(self,server_id):
        for sensor in self.dead_servers_data[server_id]:
            while self.dead_servers_data[server_id][sensor]:
                data=self.dead_servers_data[server_id][sensor].pop()
                msg=Message(sensor,server_id,data,False)
                self.send_msg(server_id,msg)
        self.dead_servers_data.pop(server_id)

    def create_replicas(self, msg):
        """
        Masolatok keszitese a kapott adatrol a szomszedos szerverekre
        :param msg: a kapott uzenet
        :return: None
        """
        n_replicas_created = 0
        # ha nem nekunk jott az adat eredetileg, akkor a sajat szerver nem aktiv
        msg.is_parent_alive = (msg.parent_server_id == self.id)
        for server in self.neighbour_servers:
            if server.receive_data(msg):
                n_replicas_created += 1
            if n_replicas_created == NUM_REPLICAS:
                break
