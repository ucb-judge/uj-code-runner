#!/bin/bash

if [ $# -ne 5 ]; then
  echo "Usage: $0 <program> <input_file> <output_file> <timeout> <memory_limit>"
  exit 1
fi

program="$1"
input_file="$2"
output_file="$3"
timeout_duration="$4"
memory_limit="$5"

# Get the execution time of the program beginning from the start of its execution
start_time=$(date +%s.%N)
# Run the program a second time to get the execution time in seconds
timeout "$timeout_duration"s ./"$program" < "$input_file" > "$output_file" 2>/dev/null
exit_status=$?
end_time=$(date +%s.%N)

# Check if the program exceeded the memory limit
if [ $exit_status -eq 137 ]; then
  echo "Memory limit exceeded"
  exit 1
fi

# Check if the program was terminated due to a timeout
if [ $exit_status -eq 124 ]; then
  echo "Timeout"
  exit 1
fi

# Run the program a second time to get the memory usage in KB
memory_usage=$(ps -o rss= -p $(pgrep "$program"))
# Compare memory usage with the memory limit
if [ $memory_usage -gt $memory_limit ]; then
  echo "Memory limit exceeded by $((memory_usage - memory_limit)) KB"
  exit 1
fi

# Calculate the execution time in seconds
execution_time=$(echo "$end_time - $start_time" | bc)

echo "Memory used in KB: $memory_usage"
echo "Execution time in seconds: $execution_time"
