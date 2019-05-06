#!/usr/bin/env bash
#create networks and containers
		#DNS server
        docker create --name dns \
          engedics/p2p-dns
        docker start dns
for i in $(seq 1 $1);
do	
		#network
        docker network create \
          --driver=bridge \
          --subnet=10.0.$i.0/24 \
          --gateway=10.0.$i.1 \
          br$i

		#server
        docker create --name h$i \
          --network br$i \
		  --expose 9600 \
          --publish 10.0.$i.1:9600:9600 \
          engedics/p2p-server
        docker start h$i
	ping h1
	
		#sensors
        for o in $(seq 1 $2);
        do
				port=`echo "9600 + $o" | bc`
                docker create --name s$i-$o \
                  --network br$i \
				  --expose $port \
				  --publish 10.0.$i.1:$port:$port \
                  engedics/p2p-sensor
                docker start s$i-$o
        done
done
