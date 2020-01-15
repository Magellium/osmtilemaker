#!/bin/bash

# Settings
set -e # Be sure we fail on error and output debugging information
trap 'echo "$0: error on line $LINENO"' ERR
set -x # Print commands and their arguments as they are executed

# Config reading
here="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
. $here/../conf/config

echo
echo ------------------------------------------------------
echo Create PGSQL user and database with extensions
echo

psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" <<-EOSQL
    CREATE USER $DBPG_USER_OSMTILEMAKER_USERNAME 
        NOSUPERUSER INHERIT NOCREATEDB NOCREATEROLE NOREPLICATION;
    CREATE DATABASE $DBPG_DATABASE_NAME
        WITH OWNER = $DBPG_USER_OSMTILEMAKER_USERNAME
            ENCODING = 'UTF8'
            TABLESPACE = pg_default
            LC_COLLATE = 'en_US.utf8'
            LC_CTYPE = 'en_US.utf8'
            CONNECTION LIMIT = -1
EOSQL

psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$DBPG_DATABASE_NAME" <<-EOSQL
    CREATE EXTENSION postgis;
    CREATE EXTENSION postgis_topology;
    CREATE EXTENSION hstore;
EOSQL