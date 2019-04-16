from p2p.Sensor import Sensor
from p2p.StorageServer import  StorageServer
from p2p.Data import Data
import random
from random import randint


def test_complexMessaging():
    h="""
    Masolatok keszitesenek ellenorzese
    Sok szerver es szenzor letrehozasa, sok adat elkuldese, majd ezek megletenek ellenorzese
    """

    print(h)

    random.seed(42)

    def create_network(num_servers, num_sensors):
        """
        num_servers darab szerverbol allo halozat letrehozasa, melyekhez kapcsolodo
        szenzorok szamat a num_sensors lista adja meg
        :param num_servers: szerverek szama
        :param num_sensors: szenzorok szama szerverenkent (lista vagy egy szam)
        :return: szerverek listaja, szenorok listainak listaja szerverenkent
        """
        if type(num_sensors) is int:
            num_sensors = [num_sensors] * num_servers
        # create servers
        servers = [StorageServer(alive=True, id=1001+i) for i in range(num_servers)]
        # create sensors
        sensors = []
        for i in range(num_servers):
            ss = []
            for j in range(num_sensors[i]):
                sensor = Sensor(9001+100*i+j, [servers[i]])
                servers[i].add_sensor(sensor)
                ss.append(sensor)
            sensors.append(ss)
        # szerverek kozotti teljes halozat letrehozasa
        for i in range(num_servers):
            for j in range(num_servers):
                servers[i].add_neighbour_server(servers[(i+j+1) % num_servers])
        return servers, sensors

    servers, sensors = create_network(5, 2)

    for sensor_list in sensors:
        for sensor in sensor_list:
            sensor.send_data(Data(randint(0,255)))
            sensor.send_data(Data(randint(1000, 1255)))

    for server in servers:
        print('Server', server.id)
        print('Own data:', server.data)
        print('Replicas', server.other_data)
        print('Temporal data:', server.dead_servers_data)
        print()

    for server in servers:
        assert (len(server.data) == 2 and len(server.other_data) == 2 and len(server.dead_servers_data) == 0)
        for od in server.other_data:
            assert (len(server.other_data[od]) == 2)
            for d in server.other_data[od].items():
                assert (len(d) == 2)

if __name__ == '__main__':
    test_complexMessaging()