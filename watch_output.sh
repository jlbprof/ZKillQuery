#!/bin/bash

while true; do
    echo `date`
    curl https://zkillredisq.stream/listen.php?queueID=Bodger1234 >> output.jsonl; echo >> output.jsonl
    sleep 30
done

