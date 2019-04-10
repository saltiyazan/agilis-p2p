from p2p.Message import Message

class Sensor:
    def __init__(self, id, servers):
        self.id = id
        self.servers = servers
        self.new_datas=[]
        self.has_new_data=False
        self.recieved_messages=[]
        self.message_to_send=""

    #szerverek tömbjének újramegadása
    def redefine_servers(self, servers_array):
        self.servers=servers_array
    
    #kikeresi a küldendő adatot a meglévő még nem küldött adatok kozül
    def search_data_to_send(self, data):
        for d in self.new_datas:
            if (data == d):
                data_to_send=data
                break
        else:
            raise Exception(data + " sensor has not the excepted data in new datas.")
        return data_to_send
    
    #megpróbál küldeni a szervernek
    def try_to_send_data(self, server, data):
        msg = Message(self.id, self.servers[0].id, data)
        result = server.receive_data(msg)
        return  result

    #sorban megpróbál küldeni az összes szervernek
    def send_data(self, data):
        for server in self.servers:
            success = self.try_to_send_data(server, data)
            if (success):
                break
        else:
            raise Exception("Could not send data to any server.")
    
    def recieve_msg(self, message):
        self.recieved_messages.__add__(message)

    #üzenetküldés próbája az összes szerver felé
    def send_message(self, message):
        for server in self.servers:
            success = self.try_to_send_data(server, message)
            if (success):
                break
        else:
            raise Exception("Could not send message to any server.")
    
    
