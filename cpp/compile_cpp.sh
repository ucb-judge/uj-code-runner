#!/bin/bash

if [ $# -ne 1 ]; then
  echo "Usage: $0 <cpp_file>"
  exit 1
fi

cpp_file="$1"
executable="${cpp_file%.*}"

g++ -std=c++11 -O2 -Wall -Wextra -Werror -Wno-sign-compare -Wshadow -fsanitize=address -fsanitize=undefined -D_GLIBCXX_DEBUG -D_GLIBCXX_DEBUG_PEDANTIC -D_FORTIFY_SOURCE=2 -fstack-protector -DLOCAL -o "$executable" "$cpp_file"

if [ $? -eq 0 ]; then
  echo "Compilation successful"
else
  echo "Compilation failed"
  exit 1
fi
