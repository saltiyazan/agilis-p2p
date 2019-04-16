from p2p.Message import Message
from p2p.config import LOGGING_ENABLED

class Sensor:
    def __init__(self, id, servers):
        self.id = id
        self.servers = servers
        self.new_datas=[]
        self.has_new_data=False
        self.recieved_messages=[]
        self.message_to_send=""

    def __str__(self):
        """
        Stringge alakitas, kiiratashoz kell
        """
        return f'Sensor_{self.id}'

    def log(self, *args, **kwargs):
        """
        Fontosabb esemenyek logolasa konzolra, ha a config-ban LOGGING_ENABLED engedelyezve van.
        Hivas szintaxisa: print-tel megegyezoen
        :param args: kiirando dolgok felsorolasa
        :param kwargs: elvalaszto karakter megadhato sep=' ' formaban, alapertelmezes: szokoz
        """
        if LOGGING_ENABLED:
            if 'sep' in kwargs:
                sep = kwargs.get('sep')
            else:
                sep = ' '
            msg = sep.join(map(str, args))
            print('Sensor ', self.id, ': ', msg, sep='')

    #szerverek tömbjének újramegadása
    def redefine_servers(self, servers_array):
        self.log('New server list:', servers_array)
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
            self.log('Sending data', data, 'to', server)
            success = self.try_to_send_data(server, data)
            if not success:
                self.log('Sending was unsuccessful.')
            if (success):
                break
        else:
            self.log('Could not send data to any server.')
            raise Exception("Could not send data to any server.")
    
    def recieve_msg(self, message):
        self.log('Received message', message)
        self.recieved_messages.__add__(message)

    #üzenetküldés próbája az összes szerver felé
    def send_message(self, message):
        for server in self.servers:
            self.log('Sending message', message, 'to', server)
            success = self.try_to_send_data(server, message)
            if (success):
                break
        else:
            raise Exception("Could not send message to any server.")
    
    
