#úgy fog előállni egy üzenet, hogy a küldő elmondja, hogy ez melyik sensor üzenete, eredetileg, melyik szerverhez ment volna és, hogy a az a szerver él-e
#ha a szülő szerverhez megy az üzenet akkor azt sajátjaként fogja kezelni a szerver
#ha egy másik szerverhez megy mint a szülő akkor az a szerver a parent_is_alive flag alapján fogja értelmezni vagy duplikált vagy ideiglenes üzenetként
class Message:
    def __init__(self,sensor_id,server_id,content, is_alive=None):
        self.sensor_id=sensor_id
        self.parent_server_id=server_id
        self.is_parent_alive=is_alive
        self.content=content

#Készült egy általánosabb megoldása is a message üzenetnek, szerdán megvitatjuk, melyik a szükségesebb.
class MessageV2:
    def __init__(self, source_id, destination_id, content, source_is_server, destination_is_server):
        self.source_id = source_id
        self.destination_id = destination_id
        self.content = content
        self.is_sent = False
        self.source_is_server = source_is_server # bool
        self.destination_is_server = destination_is_server #bool