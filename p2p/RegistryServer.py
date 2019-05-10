import rpyc.utils.registry
import logging
import sys
import time
import threading


class RegistryServer(rpyc.utils.registry.TCPRegistryServer):

    def on_service_added(self, name, addrinfo):
        new_neighbour_list = []
        for server in self.services["STORAGESERVER"]:
            server_ip = server[0].split(".")
            server_ip = server_ip[0] + "." + server_ip[1] + "." + server_ip[2] + ".1"
            new_neighbour_list.append(server_ip)
        print(new_neighbour_list)
        for server_id in new_neighbour_list:
            try:
                c = rpyc.connect(server_id, 9600)
                c.root.refresh_neighbour_list(new_neighbour_list)
            except Exception as ex:
                print("Failed RPC: ", ex)

    def on_service_removed(self, name, addrinfo):
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

    def remove_stale(self, name):
        try:
            self.logger.debug("checking stales")
            oldest = time.time() - self.pruning_timeout
            print(oldest)
            all_servers = sorted(self.services[name].items(), key=lambda x: x[1])
            servers = []
            for addrinfo, t in all_servers:
                self.logger.debug("checking stale %s:%s", *addrinfo)
                print(t)
                if t < oldest:
                    self.logger.debug("discarding stale %s:%s", *addrinfo)
                    self._remove_service(name, addrinfo)
        except Exception as ex:
            print(ex)


def check_stale():
    this.remove_stale("STORAGESERVER")
    threading.Timer(5.0, check_stale).start()


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
    this = RegistryServer(logger=logging.getLogger(), pruning_timeout=30)
    check_stale()
    this.start()
    print("Registry server started!")
