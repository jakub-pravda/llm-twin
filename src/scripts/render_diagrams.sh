#!/bin/sh

# This script renders all diagrams in the project with d2 cli tool

# Check if d2 is installed
if ! command -v d2 > /dev/null
then
    echo "d2 could not be found. Please install it"
    exit
fi

for f in ../diagrams/*.d2; do
    d2 "$f"
done