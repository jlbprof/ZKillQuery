#!/bin/bash

set -x

rm -f db_zkill_query.db
ls -ld *.db

./ZKillQuery.py


