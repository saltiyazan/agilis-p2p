from p2p.Sensor import Sensor
from p2p.StorageServer import StorageServer
from p2p.Data import Data


def test_MultipleServersDown():
    h="""
    A fo szerver mellett, mar mukodes kozben megjelenik egy masik szerver.
    A fo szerver ezutan meghal, ekkor a masiknak kell atvennie a helyet.
    A fo szerver feleledese utan meg kell kapnia az adatokat az uj szervertol.
    Ezutan az uj szerver all le, ekkor a fonek kell begyujtenie a keletkezett adatokat.
    """

    print(h)

    mainServer = StorageServer(alive=True, id=1001)


    s_id = 9001
    s2_id = 9002
    sensor = Sensor(id=s_id, servers=[])
    mainServer.add_sensor(sensor)

    data_1 = Data("data_1")
    sensor.send_data(data=data_1)
    assert(data_1 in mainServer.data[s_id])

    newServer = StorageServer(alive=True, id=1002)

    newServer.add_neighbour_server(mainServer)
    mainServer.add_neighbour_server(newServer)



    # mainServer leallitasa
    mainServer.change_alive_state(False)
    data_2 = Data("data_2 during main down")
    sensor.send_data(data=data_2)
    assert(data_2 not in mainServer.data[s_id])
    assert(data_2 in newServer.dead_servers_data[1001][s_id])

    # main feleled
    mainServer.change_alive_state(True)
    assert (data_2 in mainServer.data[s_id])

    # uj szerver is kap szenzort
    sensor2 = Sensor(s2_id, servers=[])
    newServer.add_sensor(sensor2)
    data_3 = Data('data for new server')
    sensor2.send_data(data_3)
    assert (data_3 in newServer.data[s2_id])
    assert (data_3 in mainServer.other_data[1002][s2_id])

    # uj szerver is leall
    newServer.change_alive_state(False)
    data_4 = Data('data during new sever dead')
    sensor2.send_data(data_4)
    assert (data_4 not in newServer.data[s2_id])
    assert (data_4 in mainServer.dead_servers_data[1002][s2_id])

    # uj szerver feleled
    newServer.change_alive_state(True)
    assert (data_4 in newServer.data[s2_id])




if __name__ == '__main__':
    test_MultipleServersDown()