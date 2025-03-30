#!/usr/bin/env bash

podman rm -f mongo-cluster-1
podman rm -f mongo-cluster-2
podman rm -f mongo-cluster-3

podman rm -f rabbit-mq
