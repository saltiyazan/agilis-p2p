from io import StringIO
import sys
from p2p.config import LOGGING_ENABLED
from p2p.StorageServer import StorageServer
from p2p.Sensor import Sensor
from p2p.Message import Message


def test_log():
    h="""
    Szerverek es szenzorok logolasanak tesztelese
    """
    print(h)

    if not LOGGING_ENABLED:
        print("Logolas ki van kapcsolva a config file-ban, a teszt futtatasahoz be kell kapcsolni")
    assert (LOGGING_ENABLED)

    # stdout atallitasa
    captureOutput = StringIO()
    sys.stdout = captureOutput
    expected = []

    # logolas:
    mainServerID = 1000
    mainServer = StorageServer(alive=True, id=mainServerID)
    sensorID = mainServerID + 1
    sensor = Sensor(id=sensorID, servers=[])
    mainServer.add_sensor(sensor=sensor)
    expected.append("Server " + str(mainServerID) + ": Sensor added: " + str(sensor))

    neighbourServerID = 2000
    neighbourServer = StorageServer(alive=True, id=neighbourServerID)
    mainServer.add_neighbour_server(neighbourServer)
    expected.append("Sensor " + str(sensorID) + ": New server list: " + str(sensor.servers))
    expected.append("Server " + str(mainServerID) + ": Neighbour server added: " + str(neighbourServer))

    data_ = "Data sent from sensor to own server"
    msg = Message(sensor_id=sensorID, server_id=mainServerID, content=data_, is_replica=None)
    sensor.send_data(data=data_)
    expected.append("Sensor " + str(sensorID) + ": Sending data " + data_ + " to " + str(mainServer))
    expected.append("Server " + str(mainServerID) + ": Received own data " + str(msg))
    msg.is_replica = True
    expected.append("Server " + str(neighbourServerID) + ": Received other data " + str(msg))

    mainServer.change_alive_state(alive=False)
    expected.append("Server " + str(mainServerID) + ": Alive state changed to False")
    data_dead = "sending data to dead server"
    sensor.send_data(data_dead)
    msg_dead = Message(sensor_id=sensorID, server_id=mainServerID, content=data_dead, is_replica=None)
    expected.append("Server " + str(neighbourServerID) + ": Received dead data " + str(msg_dead))

    mainServer.change_alive_state(False)
    neighbourServer.change_alive_state(False)
    data_notsent = "Data is unable to send"
    try:
        sensor.send_data(data_notsent)
    except:
        print("exception")
    expected.append("Sensor " + str(sensorID) + ": Sending was unsuccessful.")
    expected.append("Sensor " + str(sensorID) + ": Could not send data to any server.")

    # stdout visszaallitas
    sys.stdout = sys.__stdout__

    for expect in expected:
        if(expect not in captureOutput.getvalue()):
            print(expect)
        assert(expect in captureOutput.getvalue())



if __name__ == '__main__':
    test_log()
