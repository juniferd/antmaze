#!/bin/bash

function run_server {
  while [[ 1 ]]; do
   echo "STARTING SERVER";
   python MAZE/app.py > maze.output &
   pid=$!
   sleep 24h
   kill -9 $pid
   sleep 1s
   rm -fr MAZE/db/
   mkdir -p MAZE/db/
  done
}

function finish {
  echo "EXITING SERVER, MAKING LAST DITCH KILL OF $pid"
  kill -9 $pid
}

trap finish EXIT
run_server
