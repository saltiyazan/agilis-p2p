from p2p.Sensor import Sensor
from p2p.StorageServer import StorageServer


def test_dataSending():
    h="""
    Adatkuldes ellenorzese.
    Letrehozunk egy szervert es hozzaadunk egy szenzort.
    A szenzor elkuld egy adatot; ellenorizzuk, hogy a szerverre megerkezett-e.
    """

    print(h)

    server1 = StorageServer(alive=True, id=1001)
    sensor1 = Sensor(9001, servers=[])

    server1.add_sensor(sensor1)
    sensor1.redefine_servers([server1])

    data = 'simple_test_data'
    #server1.receive_data('testdata', sensor1.id)
    sensor1.send_data(data)
    print('Server1 data:', server1.data)
    assert(len(server1.data) == 1)

    print('Test ok')

