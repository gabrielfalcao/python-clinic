#!/bin/bash

set -x
cd /root/
ps aux | egrep process.sh | grep -v grep | awk '{print $2}' | xargs kill -9
docker stop $(docker ps -qa)
ps aux | egrep process.sh | grep -v grep | awk '{print $2}' | xargs kill -9
rm -f nohup.out
