#!/bin/bash

set -x

rm -f ~/ZKillQueryData/run.log
rm -f ~/ZKillQueryData/zkill.log
mkdir -p ~/ZKillQueryData/queue

python3 zkill_producer.py


