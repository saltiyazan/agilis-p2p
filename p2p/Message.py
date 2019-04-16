#úgy fog előállni egy üzenet, hogy a küldő elmondja, hogy ez melyik sensor üzenete, eredetileg, melyik szerverhez ment volna és, hogy a az a szerver él-e
#ha a szülő szerverhez megy az üzenet akkor azt sajátjaként fogja kezelni a szerver
#ha egy másik szerverhez megy mint a szülő akkor az a szerver a parent_is_alive flag alapján fogja értelmezni vagy duplikált vagy ideiglenes üzenetként
class Message:
    def __init__(self,sensor_id,server_id,content, is_replica=None):
        self.sensor_id=sensor_id
        self.parent_server_id=server_id
        self.is_replica=is_replica
        self.content=content

    def __str__(self):
        """
        Stringge alakitas, kiiratashoz kell
        """
        return f'Message[Sensor: {self.sensor_id}, server: {self.parent_server_id}, content: {self.content}, repl: {self.is_replica}]'

#Készült egy általánosabb megoldása is a message üzenetnek, szerdán megvitatjuk, melyik a szükségesebb.
class MessageV2:
    def __init__(self, source_id, destination_id, source_is_server, destination_is_server, is_sent=False, content=None):
        self.source_id = source_id
        self.destination_id = destination_id
        self.content = content
        self.is_sent = False
        self.source_is_server = source_is_server # bool
        self.destination_is_server = destination_is_server #bool