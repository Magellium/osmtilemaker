#!/bin/bash

# Settings
set -e # Be sure we fail on error and output debugging information
trap 'echo "$0: error on line $LINENO"' ERR
#set -x # Print commands and their arguments as they are executed

# Config reading
here="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
. $here/../conf/config


echo
echo ------------------------------------------------------
echo Check requirements
echo

## Check if docker is installed
if ! [ -x "$(command -v docker)" ]
then
  echo 'Error: docker is not installed.' >&2
  exit 1
else
  echo '- Docker is installed.' >&2
fi

## Check for some directories
DIR="\
$HOSTPATH_OSM_FILE_DIR \
$HOSTPATH_PG_DATA_DIR \
$HOSTPATH_OSM2PGSQL_FLATNODE_DIR \
$HOSTPATH_TILES_DIR \
$HOSTPATH_LOG_DIR"
MISSING_DIR=""
for dir in $DIR
do
if [ ! -d "$dir" ]
then
    MISSING_DIR="$MISSING_DIR $dir"
    >&2 echo -e "Error: '$dir' directory does not exist."
else
  echo "- '$dir' directory exists.">&2
fi
done

if [ ! -z "$MISSING_DIR" ]; then
    echo -e "At least one working directory is missing. You could run:\n\
    mkdir -p $MISSING_DIR"
    exit 1
fi

## Check for the latest .osm.pbf file
if [ ! -f "$HOSTPATH_OSM_FILE_DIR/$OSM_LATEST_FILE_NAME" ]
then
    >&2 echo -e "Error: '$HOSTPATH_OSM_FILE_DIR/$OSM_LATEST_FILE_NAME' file does not exist."
    if [ ! -z "$OSM_LATEST_FILE_DOWNLOAD_URL" ]; then
    echo -e "You could run:\n\
    wget $OSM_LATEST_FILE_DOWNLOAD_URL -O $HOSTPATH_OSM_FILE_DIR/$OSM_LATEST_FILE_NAME"
    fi
    exit 1
else
  echo "- '$HOSTPATH_OSM_FILE_DIR/$OSM_LATEST_FILE_NAME' file exists">&2
fi

## Check tile dir is empty
if [ "$(ls -A  $HOSTPATH_TILES_DIR)" ]; 
then
    echo -e "'$HOSTPATH_TILES_DIR' is not empty. You could run:\n\
    rm -rf $HOSTPATH_TILES_DIR/*"
    exit 1
else
  echo "- '$HOSTPATH_TILES_DIR' tiles directory is empty">&2
fi
echo
echo Success: you fulfil all requirements!
echo ------------------------------------------------------
echo
