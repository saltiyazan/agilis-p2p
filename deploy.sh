
#!/usr/bin/env bash
#create networks and containers
#DNS server
 docker create --name dns-proxy-server \
        --publish 53:53 \
        --hostname dns.mageddo \
        -v /opt/dns-proxy-server/conf:/app/conf \
        -v /var/run/docker.sock:/var/run/docker.sock \
        -v /etc/resolv.conf:/etc/resolv.conf \
          engedics/p2p-dns

        docker start dns-proxy-server

for i in $(seq 1 $1);
do      
        #network
        docker network create \
          --driver bridge \
          --subnet 10.0.$i.0/24 \
          --gateway 10.0.$i.1 \
          br$i

        #server
        docker create --name h$i \
          --network br$i \
          --expose 9600 \
          --publish 10.0.$i.1:9600:9600 \
          --hostname h$i \
          --dns 172.17.0.1 \
          --dns-opt use-vc \
          engedics/p2p-server
        docker start h$i
        ping h1 -c 10

        #sensors
        for o in $(seq 1 $2);
        do
                docker create --name s$i-$o \
                  --network br$i \
                  --hostname s$i-$o \
		  --dns 172.17.0.1 \
                  --dns-opt use-vc \
                  engedics/p2p-sensor
                docker start s$i-$o
        done
done
