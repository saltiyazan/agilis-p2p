from p2p.Sensor import Sensor
from p2p.StorageServer import StorageServer
from p2p.config import NUM_REPLICAS


def test_replicas():
    h="""
    Masolatok keszitesenek ellenorzese
    Letrehozunk 4 db szervert, az egyikhez hozzaadunk 1 szenzort.
    A szenzor altal alkuldott adatnak a sajat szervere mellett ket masik szerveren kell megjelennie
    """

    print(h)

    server1 = StorageServer(alive=True, id=1001)
    server2 = StorageServer(alive=True, id=1002)
    server3 = StorageServer(alive=True, id=1003)
    server4 = StorageServer(alive=True, id=1004)
    sensor1 = Sensor(9001, servers=[])

    # most nincs full mesh, csak server1 van mindenkivel osszekotve
    server1.add_neighbour_server(server2)
    server2.add_neighbour_server(server1)
    server1.add_neighbour_server(server3)
    server3.add_neighbour_server(server1)
    server1.add_neighbour_server(server4)
    server4.add_neighbour_server(server1)

    server1.add_sensor(sensor1)
    #sensor1.redefine_servers([server1, server2, server3, server4])

    assert(len(sensor1.servers) == 4 and sensor1.servers[0] == server1)

    data = 'simple_test_data'
    sensor1.send_data(data)

    print('Server1 data:', server1.data)
    assert (len(server1.data) == 1)

    print('Server2 replicas:', server2.other_data)
    assert (server2.other_data == {1001: {9001: ['simple_test_data']}})

    print('Server3 replicas:', server3.other_data)
    assert (server3.other_data == {1001: {9001: ['simple_test_data']}})

    print('Server4 replicas:', server4.other_data)
    assert (server4.other_data == {} or NUM_REPLICAS != 2)

    print('Test ok')
