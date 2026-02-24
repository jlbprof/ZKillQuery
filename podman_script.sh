#!/bin/bash

set -x

CLEAN_DB=false
CLEAN_LOGS=false
NO_CACHE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --clean-db)
            CLEAN_DB=true
            shift
            ;;
        --clean-logs)
            CLEAN_LOGS=true
            shift
            ;;
        --no-cache)
            NO_CACHE=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  --clean-db      Delete database before starting"
            echo "  --clean-logs    Delete logs before starting"
            echo "  --no-cache     Force rebuild without cache"
            echo "  --help, -h     Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage"
            exit 1
            ;;
    esac
done

if [ "$CLEAN_LOGS" = true ]; then
    rm -f /home/julian/ZKillQueryData/zkill.log
    rm -f /home/julian/ZKillQueryData/zkill_consumer.log
    rm -f /home/julian/ZKillQueryData/zkill_producer.log
    rm -f /home/julian/ZKillQueryData/zkill_db_init.log
    rm -f /home/julian/ZKillQueryData/*.log
fi

if [ "$CLEAN_DB" = true ]; then
    rm -f /home/julian/ZKillQueryData/db_zkill_query.db
fi

./podman_cleanup.sh

if [ "$NO_CACHE" = true ]; then
    podman-compose build --no-cache
else
    podman-compose build
fi

podman-compose up -d
