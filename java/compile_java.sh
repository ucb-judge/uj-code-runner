#!/bin/bash

if [ $# -ne 1 ]; then
  echo "Usage: $0 <java_file>"
  exit 1
fi

java_file="$1"
executable="${java_file%.*}"

javac -d . "$java_file"

if [ $? -eq 0 ]; then
  echo "Compilation successful"
else
  echo "Compilation failed"
  exit 1
fi
