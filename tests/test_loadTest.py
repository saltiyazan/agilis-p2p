from p2p.Data import Data
from p2p.Sensor import Sensor
from p2p.StorageServer import StorageServer


def test_loadTest():
    h="""
    Egy szerverhez csatlakozik 20 szenzor.
    A szenzorok folyamatosan kuldik az adatokat.
    Minden adatnak meg kell erkezni.
    """

    print(h)

    server = StorageServer(alive=True, id=1)
    sensor_number = 20
    sensors = [Sensor(id=100+i, servers=[server]) for i in range(sensor_number)]

    data_num = 100
    for n in range(data_num):
        for sensor in sensors:
            sensor.send_data(Data("data_from_sensor" + str(sensor.id) + "_data" + str(n)))

    for m in range(data_num):
        for sensor in sensors:
            # itt csak a datak ertekevel hasonlitjuk ossze, az idoket nem nezzuk
            assert("data_from_sensor" + str(sensor.id) + "_data" + str(m) in [d.data[1] for d in server.data[sensor.id]])

    print("Test ok")

if __name__ == '__main__':
    test_loadTest()