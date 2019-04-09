h="""
Szerver leallas ellenorzese.
Egy szenzornak megadunk ket szervert.
Ha a main szerver leall, akkor a szenzor a backup szervernek kuldi az adatot.
"""

from p2p.Sensor import Sensor
from p2p.StorageServer import StorageServer

print(h)

mainServer = StorageServer(alive=True, id=1)
backupServer = StorageServer(alive=True, id=2)

s_id = 10
sensor = Sensor(id=s_id, servers=[mainServer, backupServer])

#adat kuldese a fo szervernek
data_1 = "data_1 to mainServer"
sensor.send_data(data=data_1)
assert(data_1 in mainServer.data[s_id])
assert(backupServer.data == {})

#mainServer leallitasa
data_2 = "data_2 to backupServer"
mainServer.alive = False
sensor.send_data(data=data_2)
assert(data_2 not in mainServer.data[s_id])
assert(data_2 in backupServer.dead_servers_data[1][s_id])

#mainServer feleled
data_3 = "data_3 to mainServer"
mainServer.alive = True
sensor.send_data(data=data_3)
assert(data_3 in mainServer.data[s_id])
assert(data_3 not in backupServer.dead_servers_data[1][s_id])

#ha egyik szerver sem kapja meg akkor kivetelt dob
mainServer.alive = False
backupServer.alive = False
data_4 = "data_cannot_be_sent"
ok = False
try:
    sensor.send_data(data_4)
except:
    ok = True
assert(ok)

print("Test ok")
