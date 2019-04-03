from numpy import *
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

    #még csak egyszerűen hozzáadjuk a szomszédok listájához
    def add_neighbour_server(self,server):
        self.neighbour_servers.append(server)

    #megkapja az adatot és eltárolja a megfelelő szenzorhoz tartozó listába
    def receive_data(self, message, sensor_id ):
        if sensor_id not in self.data:
            self.data[sensor_id] = []
        self.data[sensor_id].append(message)
        if self.alive is True:
            return "received"
        else:
            return None

    #megkapja az adatot és a megelelő helyre beteszi
    def receive_duplicated_data(self,server_id,sensor_id,message):
        self.other_data[server_id][sensor_id].append(message)
        if self.alive is True:
            return "received"
        else:
            return None

    #ezzel tudja a saját szenzorainak az adatait elküldeni hogy azok duplikálva tárolódjanak
    def send_data(self,server_id):
        for key in self.data.keys():
            res=self.neighbour_servers[server_id].receive_duplicated_data(self.id,key,self.data[key])
            if res != "received" :
                raise Exception(server_id+ 'server is dead')

    #ezt kell meghívni amikor a szenzorok nem tudják a saját szerverüknek elküldeni az adatot hanem elküldik egy másik szervernek
    def receive_data_of_dead_server(self, server_id, sensor_id,message):
        self.dead_servers_data[server_id][sensor_id].append(message)
        if self.alive is True:
            return "received"
        else:
            return None

    #ezzel szólunk hogy egy szerver megint él vagy új szerver lépett be
    def receive_new_server_is_alive(self,server_id):
        self.neighbour_servers.append(server_id)
        if server_id in self.dead_servers_data:
           self.repair_dead_server(server_id)

    #ezzel kap értesítést hogy az egyik szerver leállt
    def receive_server_is_dead(self,server_id):
        self.neighbour_servers.remove(server_id)

    def repair_dead_server(self,server_id):
        return 0