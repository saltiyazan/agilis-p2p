import rpyc.utils.registry


class RegistryServer(rpyc.utils.registry.TCPRegistryServer):

    def on_service_added(self, name, addrinfo):
        for server_id in self.services[name]:
            c = rpyc.connect(server_id, 9600)
            c.root.add_neighbour_server(addrinfo)


if __name__ == "__main__":
    this = RegistryServer()
    this.start()
    print("Registry server started!")