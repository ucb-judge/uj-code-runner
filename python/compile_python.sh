#!/bin/bash

if [ $# -ne 1 ]; then
  echo "Usage: $0 <python_file>"
  exit 1
fi

python_file="$1"
python3 -m py_compile "$python_file"

if [ $? -eq 0 ]; then
  echo "Compilation successful"
else
 echo -e "\nCompilation failed"
 exit 1
fi
