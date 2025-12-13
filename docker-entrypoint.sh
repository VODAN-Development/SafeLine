#!/bin/bash
set -e

# Start Fuseki server directly without the problematic initialization
exec /jena-fuseki/fuseki-server --update --mem /sord
