#!/bin/bash

  cat *.txt| egrep -vi '^(total|running|thread|verbose|suspending|genera|warning|found)' > all-onions.txt
  egrep '^[a-z0-9]+[.]onion' all-onions.txt  | sort | uniq > all-hostnames.txt
