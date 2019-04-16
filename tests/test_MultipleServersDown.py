from p2p.Sensor import Sensor
from p2p.StorageServer import StorageServer
from p2p.Data import Data


def test_MultipleServersDown():
    h="""
    A fo es az egyik backup szerver is inaktivva valik.
    A fo szerver feleledese utan igy is meg kell kapnia a kiesett adatokat.
    """

    print(h)

    mainServer = StorageServer(alive=True, id=1001)
    backupServer1 = StorageServer(alive=True, id=1002)
    backupServer2 = StorageServer(alive=True, id=1003)

    mainServer.add_neighbour_server(backupServer1)
    backupServer1.add_neighbour_server(mainServer)

    mainServer.add_neighbour_server(backupServer2)
    backupServer2.add_neighbour_server(mainServer)

    backupServer1.add_neighbour_server(backupServer2)
    backupServer2.add_neighbour_server(backupServer1)

    s_id = 9001
    sensor = Sensor(id=s_id, servers=[])
    mainServer.add_sensor(sensor)

    data_1 = Data("data_1")
    sensor.send_data(data=data_1)
    assert(data_1 in mainServer.data[s_id])
    assert(backupServer1.data == {})

    #mainServer leallitasa
    mainServer.change_alive_state(False)
    data_2 = Data("data_2 during main down")
    sensor.send_data(data=data_2)
    print('BS1 dead:', backupServer1.dead_servers_data)
    print('BS2 other:', backupServer2.other_data)
    assert(data_2 not in mainServer.data[s_id])
    assert(data_2 in backupServer1.dead_servers_data[1001][s_id])
    assert(data_2 in backupServer2.other_data[1001][s_id])

    # backup1 szerver leall
    backupServer1.change_alive_state(False)
    data_3 = Data('data_3 two servers down')
    sensor.send_data(data_3)

    assert (data_3 not in mainServer.data[s_id])
    assert (data_3 not in backupServer1.dead_servers_data[1001][s_id])
    assert (data_3 in backupServer2.dead_servers_data[1001][s_id])

    #main  es backup feleled
    mainServer.change_alive_state(True)
    backupServer1.change_alive_state(True)
    assert (data_2 in mainServer.data[s_id])
    assert (data_3 in mainServer.data[s_id])

if __name__ == '__main__':
    test_MultipleServersDown()