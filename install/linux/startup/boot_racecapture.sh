#!/bin/bash
# boot up for racecapture app

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

# run as the user specified as the first argument
sudo -u $1 ./run_racecapture.sh -w 1 & disown

