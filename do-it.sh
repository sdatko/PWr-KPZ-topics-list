#!/usr/bin/env bash
#
# Helper script to update the list on server
#
set -o errexit
set -o nounset

SERVER=''
SERVER_DIR=''

LOGOS_DEST='logotypy'
TABLE_DEST='lista.html'

./generate-list-of-projects.py

scp logos/* "${SERVER}:${SERVER_DIR}/${LOGOS_DEST}"
scp result.html "${SERVER}:${SERVER_DIR}/${TABLE_DEST}"
