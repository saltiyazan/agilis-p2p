import rpyc.utils.registry
import logging
import sys


class RegistryServer(rpyc.utils.registry.TCPRegistryServer):

    def on_service_added(self, name, addrinfo):
        for server_id in self.services[name]:
            c = rpyc.connect(server_id, 9600)
            c.root.add_neighbour_server(addrinfo)


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    this = RegistryServer(logger=logging.getLogger())
    this.start()
    print("Registry server started!")
