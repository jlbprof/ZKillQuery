#!/bin/bash

python3 -c "with open('utils.py') as f: compile (f.read(), 'utils.py', 'exec')"
python3 -c "with open('zkill_producer.py') as f: compile (f.read(), 'zkill_producer.py', 'exec')"
python3 -c "with open('zkill_consumer.py') as f: compile (f.read(), 'zkill_consumer.py', 'exec')"

