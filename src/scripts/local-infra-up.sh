#!/usr/bin/env bash
echo "*** MONGO start podman instances ***"
podman run -d --name mongo-cluster-1 \
    --network=host \
    --healthcheck-command 'mongosh --eval "try { rs.status() } catch (err)' \
    --healthcheck-interval=30s \
    mongo:8.0.0 --port 27017 --replSet rs0 --bind_ip localhost,mongo-cluster-1

podman run -d --name mongo-cluster-2 \
    --network=host \
    mongo:8.0.0 --port 27018 --replSet rs0 --bind_ip localhost,mongo-cluster-2

podman run -d --name mongo-cluster-3 \
    --network=host \
    mongo:8.0.0 --port 27019 --replSet rs0 --bind_ip localhost,mongo-cluster-3

echo "*** MONGO create replica cluster ***"
podman exec -it mongo-cluster-1 mongosh --eval "rs.initiate({_id:'rs0',members:[{_id:0,host:'localhost:27017'},{_id:1,host:'localhost:27018'},{_id:2,host:'localhost:27019'}]})" 

echo "*** MONGO replica cluster status ***"
podman exec -it mongo-cluster-1 mongosh --eval "rs.status()"

echo "*** RABBIT-MQ start podman instances ***"
podman run -d --name rabbit-mq \
    --network=host \
    rabbitmq:3-management-alpine