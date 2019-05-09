import rpyc.utils.registry
import logging
import sys


class RegistryServer(rpyc.utils.registry.TCPRegistryServer):

    def on_service_added(self, name, addrinfo):
        new_neighbour_list = []
        for server in self.services["STORAGESERVER"]:
            server_ip = server[0].split(".")
            server_ip = server_ip[0] + "." + server_ip[1] + "." + server_ip[2] + ".1"
            new_neighbour_list.append(server_ip)
        for server_id in new_neighbour_list:
            try:
                c = rpyc.connect(server_id, 9600)
                c.root.refresh_neighbour_list(new_neighbour_list)
            except Exception as ex:
                print("Failed RPC: ", ex)


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    this = rpyc.utils.registry.TCPRegistryServer(logger=logging.getLogger())
    this.start()
    print("Registry server started!")
