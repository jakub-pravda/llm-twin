#!/usr/bin/env bash

POD_PREFIX="llm-assist-"

echo "*** Starting MONGO podman instances ***"
podman run --rm -d --name ${POD_PREFIX}mongo-cluster-1 \
    --network=host \
    --healthcheck-command 'mongosh --eval "try { rs.status() } catch (err)' \
    --healthcheck-interval=30s \
    mongo:8.0.0 --port 27017 --replSet rs0 --bind_ip localhost,mongo-cluster-1

podman run --rm -d --name ${POD_PREFIX}mongo-cluster-2 \
    --network=host \
    mongo:8.0.0 --port 27018 --replSet rs0 --bind_ip localhost,mongo-cluster-2

podman run --rm -d --name ${POD_PREFIX}mongo-cluster-3 \
    --network=host \
    mongo:8.0.0 --port 27019 --replSet rs0 --bind_ip localhost,mongo-cluster-3

echo "*** MONGO creating replica cluster ***"
podman exec -it ${POD_PREFIX}mongo-cluster-1 mongosh --eval "rs.initiate({_id:'rs0',members:[{_id:0,host:'localhost:27017'},{_id:1,host:'localhost:27018'},{_id:2,host:'localhost:27019'}]})" 

echo "*** MONGO replica cluster status ***"
podman exec -it ${POD_PREFIX}mongo-cluster-1 mongosh --eval "rs.status()"

echo "*** Starting RABBIT-MQ podman instance ***"
podman run --rm -d --name ${POD_PREFIX}rabbit-mq \
    --network=host \
    rabbitmq:3-management-alpine
    
echo "*** Starting Qdrant podman instance"
podman run --rm -d --name ${POD_PREFIX}qdrant \
    --network=host \
    qdrant/qdrant