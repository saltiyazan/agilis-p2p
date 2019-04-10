h="""
Egy szerverhez csatlakozik 20 szenzor.
A szenzorok folyamatosan kuldik az adatokat.
Minden adatnak meg kell erkezni.
"""

from p2p.Sensor import Sensor
from p2p.StorageServer import StorageServer

print(h)

server = StorageServer(alive=True, id=1)
sensor_number = 20
sensors = [Sensor(id=100+i, servers=[server]) for i in range(sensor_number)]

data_num = 100
for n in range(data_num):
    for sensor in sensors:
        sensor.send_data("data_from_sensor" + str(sensor.id) + "_data" + str(n))

for m in range(data_num):
    for sensor in sensors:
        assert("data_from_sensor" + str(sensor.id) + "_data" + str(m) in server.data[sensor.id])

print("Test ok")
