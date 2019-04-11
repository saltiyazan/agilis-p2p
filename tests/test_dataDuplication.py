from p2p.Sensor import Sensor
from p2p.StorageServer import StorageServer

def test_dataDuplication():
    h="""
    Egy szerveren nem szabad ketszer ugyanazt az adatot tarolni.
    Egy adatot ketszer kuldunk el a szervernek.
    Elvart viselkedes: csak egyszer jelenjen meg a szerveren
    """

    print(h)

    server = StorageServer(alive=True, id=1)
    s_id = 10
    sensor = Sensor(id=s_id, servers=[server])
    data_ = "test_data"

    sensor.send_data(data=data_)
    sensor.send_data(data=data_)

    assert(server.data[s_id].count(data_) == 1)


