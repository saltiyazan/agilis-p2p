
#!/usr/bin/env bash
#create registry network
docker network create \
          --driver bridge \
          --subnet 10.10.10.0/24 \
          --gateway 10.10.10.1 \
          registry-net

#create registry server
docker create --name registry \
        --publish 18811:18811 \
        --hostname registry \
         engedics/p2p-registry

docker start registry

#create networks and containers
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
          --publish 10.0.$i.1:9600:9600 \
          engedics/p2p-server
        docker start h$i

        #sensors
        for o in $(seq 1 $2);
        do
                docker create --name s$i-$o \
                  --network br$i \
                  engedics/p2p-sensor
                docker start s$i-$o
        done
done
