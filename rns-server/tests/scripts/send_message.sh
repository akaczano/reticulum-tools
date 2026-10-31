#!/bin/bash

# Function to display the help menu
# Update help message
show_help() {
    echo "Usage: $0 [OPTIONS] "[MSG]""
    echo ""
    echo "Send a message to a specified user."
    echo ""
    echo "Options:"
    echo "  Name        Specify a user."
    echo "  -h          Show this help menu and exit."
    echo ""
    echo "Examples:"
    echo "  $0 -h"
    echo "  $0 gordon "hello gordon""
    echo "  $0 todd "howdy todd""
    exit 0
}

# Check if the user asked for help
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    show_help
fi

# Check if an argument was provided at all
# TODO: update help message
if [[ -z "$1" ]]; then
    echo "Error: Missing name."
    echo "Usage: $0 [NAME] or use $0 -h for help."
    echo "Examples: $0 gordon"
    exit 1
fi

# Assign the first positional argument to a descriptive variable
NAME="$1"
MSG="$2"

# Figure out user id
PORT_NUM=""
if [[ ${NAME} == "gordon" ]]; then
    PORT_NUM="5001"
elif [[ ${NAME} == "todd" ]]; then
    PORT_NUM="5002"
elif [[ ${NAME} == "roger" ]]; then
    PORT_NUM="5003"
fi

# Get contacts
contacts_json=$(curl http://localhost:${PORT_NUM}/contacts)

# Print the variable to verify
echo "${contacts_json}"

# Extract user id from JSON
$USER_ID=0
# TODO: extract id from contacts JSON - use jq

# Send message
# curl -X POST -d '{"user": ${USER_ID}, "message": "${MSG}"}' -H 'Content-Type: application/json' http://localhost:${PORT_NUM}/send
