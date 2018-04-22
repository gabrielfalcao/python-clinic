#!/bin/bash

set -xe
cd /root
./stop.sh
./reset.sh
nohup ./process.sh &
