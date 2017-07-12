#!/bin/bash

# RaceCapture App launch script for Linux

# launch with -w 1 to enable watchdog
# launch with -l <logfile> to specify the logfile path


LOGFILE=~/racecapture.log
WATCHDOG=0

while getopts ":w:l:" opt; do
    case ${opt} in
    w)  WATCHDOG=$OPTARG
        ;;
    l)  LOGFILE=$OPTARG
        ;;
    esac
done

# create the configuration directories as needed
mkdir -p ~/.kivy
mkdir -p ~/.config/racecapture

# check for ar1100 resistive touch screen controller
if lsusb | grep -q 04d8:0c02
then
  echo 'Configuring for  ar1100 resistive touch controller'
  cp -n ar1100_kivy_config.ini ~/.kivy/config.ini
fi

# check for ft5406 capacitive touch screen controller
if lsmod | grep -q rpi_ft5406
then
  echo 'Configuring for ft5406 capacitive touch controller'
  cp -n ft5406_kivy_config.ini ~/.kivy/config.ini
fi

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR

while
  ./racecapture > $LOGFILE 2>&1
  if [[ $WATCHDOG -ne 1 ]]; then
    break
  fi
  echo "racecapture crashed with code $?. Restarting..." >&2
do
  :
done

