#!/bin/bash

if [ $# -ne 1 ]; then
  echo "Usage: $0 <java_file>"
  exit 1
fi

java_file="$1"
executable="${java_file%.*}"

base_name="$(basename "$java_file" .java)"
chmod 777 "$java_file"
sed -i 's/public class [^ ]\+/public class '"$base_name"'/g' "$java_file"

javac "$java_file"

if [ $? -eq 0 ]; then
  echo "Compilation successful"
else
  echo "Compilation failed"
  exit 1
fi
