import rpyc.utils.registry
import logging
import sys


#class RegistryServer(rpyc.utils.registry.TCPRegistryServer):

    #def on_service_added(self, name, addrinfo):
    #    print(addrinfo)
    #    print(self.services)
    #    for server_id in self.services[name]:
    #        try:
    #            c = rpyc.connect(server_id, 9600)
    #            c.root.add_neighbour_server(addrinfo)
    #        except Exception as ex:
    #            print("Failed: ", ex)


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    this = rpyc.utils.registry.TCPRegistryServer(logger=logging.getLogger())
    this.start()
    print("Registry server started!")
