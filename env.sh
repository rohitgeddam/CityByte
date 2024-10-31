#!/bin/bash

# Path to your env.sh file
ENV_FILE=".env"

# Check if the env.sh file exists
if [[ ! -f "$ENV_FILE" ]]; then
    echo "Error: env.sh file not found!"
    exit 1
fi

# Prepend 'export' to each line and output to a new file
while IFS= read -r line; do
    # Skip empty lines and comments
    [[ -z "$line" || "$line" =~ ^# ]] && echo "$line" && continue
    
    # Print 'export' followed by the line
    echo "export $line"
done < "$ENV_FILE"
