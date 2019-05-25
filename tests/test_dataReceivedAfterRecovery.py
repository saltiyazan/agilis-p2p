from p2p.Sensor import Sensor
from p2p.StorageServer import StorageServer
from p2p.Data import Data


def test_dataReceivedAfterRecovery():
    h="""
    Egy szerver ujraeledese utan ra kell tolteni a kihagyott adatokat
    Egy szenzornak megadunk ket szervert.
    A main szerver leallasa utan a szenzor a backup szervernek kuldi az adatokat.
    A main szerver feleledese utan meg kell kapnia a kimaradt adatokat.
    """

    print(h)

    mainServer = StorageServer(alive=True, id=1)
    backupServer = StorageServer(alive=True, id=2)
    mainServer.add_neighbour_server(backupServer)
    backupServer.add_neighbour_server(mainServer)

    s_id = 10
    sensor = Sensor(id=s_id, servers=[mainServer, backupServer])

    data_1 = Data("data_1 to mainServer")
    sensor.send_data(data=data_1)
    assert(data_1 in mainServer.data[s_id])
    assert(backupServer.data == {})

    #mainServer leallitasa
    mainServer.change_alive_state(False)
    data_2 = Data("data_2 during main down")
    sensor.send_data(data=data_2)
    assert(data_2 not in mainServer.data[s_id])
    assert(data_2 in backupServer.dead_servers_data[1][s_id])

    #main feleled
    mainServer.change_alive_state(True)
    assert(data_2 in mainServer.data[s_id])

if __name__ == '__main__':
    test_dataReceivedAfterRecovery()