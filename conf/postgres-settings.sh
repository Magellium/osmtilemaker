#!/bin/bash

# Settings
set -e # Be sure we fail on error and output debugging information
trap 'echo "$0: error on line $LINENO"' ERR

echo
echo ------------------------------------------------------
echo Set PGSQL settings
echo

# postgres settings (compatible with postgres 10):
# - uncomment and set wanted parameters
# - [help] the command `sed -i -e"s/^shared_buffers = 128MB.*$/shared_buffers = 4GB/" ${PGDATA}/postgresql.conf`
#   will update "shared_buffers" parameter from "128MB" (default) to "4GB" in postgresql.conf file
# the recommended settings are taken from here: https://osm2pgsql.org/doc/manual.html#preparing-the-database

set -x # Print commands and their arguments as they are executed
sed -i -e"s/^max_connections = 100.*$/max_connections = 200/" ${PGDATA}/postgresql.conf
sed -i -e"s/^shared_buffers = 128MB.*$/shared_buffers = 1GB/" ${PGDATA}/postgresql.conf
sed -i -e"s/^#work_mem = 4MB.*$/work_mem = 64MB/" ${PGDATA}/postgresql.conf
sed -i -e"s/^#maintenance_work_mem = 64MB.*$/maintenance_work_mem = 10GB/" ${PGDATA}/postgresql.conf
sed -i -e"s/^#autovacuum_work_mem = -1.*$/autovacuum_work_mem = 2GB/" ${PGDATA}/postgresql.conf
sed -i -e"s/^#wal_level = replica.*$/wal_level = minimal/" ${PGDATA}/postgresql.conf
sed -i -e"s/^#max_wal_senders = 10.*$/max_wal_senders = 0/" ${PGDATA}/postgresql.conf
sed -i -e"s/^max_wal_size = 1GB.*$/max_wal_size = 10GB/" ${PGDATA}/postgresql.conf
sed -i -e"s/^#checkpoint_timeout = 5min.*$/checkpoint_timeout = 60min/" ${PGDATA}/postgresql.conf
sed -i -e"s/^#effective_cache_size = 4GB.*$/effective_cache_size = 10GB/" ${PGDATA}/postgresql.conf
sed -i -e"s/^#wal_buffers = -1.*$/wal_buffers = -1/" ${PGDATA}/postgresql.conf
sed -i -e"s/^#checkpoint_completion_target = 0.5.*$/checkpoint_completion_target = 0.9/" ${PGDATA}/postgresql.conf
sed -i -e"s/^#random_page_cost = 4.0.*$/random_page_cost = 1.0/" ${PGDATA}/postgresql.conf
sed -i -e"s/^#cpu_tuple_cost = 0.01.*$/cpu_tuple_cost = 0.05/" ${PGDATA}/postgresql.conf
sed -i -e"s/^#autovacuum_vacuum_scale_factor = 0.2.*$/autovacuum_analyze_scale_factor = 0.2/" ${PGDATA}/postgresql.conf
#sed -i -e"s/^#full_page_writes = on.*$/full_page_writes = off/" ${PGDATA}/postgresql.conf
#sed -i -e"s/^#logging_collector = off.*$/logging_collector = on/" ${PGDATA}/postgresql.conf
#sed -i -e"s/^#log_statement = 'none'.*$/log_statement = 'all'/" ${PGDATA}/postgresql.conf
