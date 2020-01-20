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

set -x # Print commands and their arguments as they are executed
sed -i -e"s/^shared_buffers = 128MB.*$/shared_buffers = 512MB/" ${PGDATA}/postgresql.conf
sed -i -e"s/^#work_mem = 4MB.*$/work_mem = 64MB/" ${PGDATA}/postgresql.conf
sed -i -e"s/^#maintenance_work_mem = 64MB.*$/maintenance_work_mem = 1024MB/" ${PGDATA}/postgresql.conf
sed -i -e"s/^#wal_buffers = -1.*$/wal_buffers = -1/" ${PGDATA}/postgresql.conf
sed -i -e"s/^#checkpoint_completion_target = 0.5.*$/checkpoint_completion_target = 0.9/" ${PGDATA}/postgresql.conf
sed -i -e"s/^#random_page_cost = 4.0.*$/random_page_cost = 2.0/" ${PGDATA}/postgresql.conf
sed -i -e"s/^#cpu_tuple_cost = 0.01.*$/cpu_tuple_cost = 0.05/" ${PGDATA}/postgresql.conf
sed -i -e"s/^#autovacuum_vacuum_scale_factor = 0.2.*$/autovacuum_analyze_scale_factor = 0.2/" ${PGDATA}/postgresql.conf
#sed -i -e"s/^#full_page_writes = on.*$/full_page_writes = off/" ${PGDATA}/postgresql.conf
#sed -i -e"s/^#logging_collector = off.*$/logging_collector = on/" ${PGDATA}/postgresql.conf
#sed -i -e"s/^#log_statement = 'none'.*$/log_statement = 'all'/" ${PGDATA}/postgresql.conf
