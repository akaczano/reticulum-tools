#!/bin/bash

# Function to display the help menu
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Get a list of contacts for a specified user."
    echo ""
    echo "Options:"
    echo "  Name        Specify a user."
    echo "  -h          Show this help menu and exit."
    echo ""
    echo "Examples:"
    echo "  $0 -h"
    echo "  $0 gordon"
    echo "  $0 todd"
    exit 0
}

# Check if the user asked for help
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
    show_help
fi

# Check if an argument was provided at all
if [[ -z "$1" ]]; then
    echo "Error: Missing name."
    echo "Usage: $0 [NAME] or use $0 -h for help."
    echo "Examples: $0 gordon"
    exit 1
fi

# Assign the first positional argument to a descriptive variable
NAME="$1"

# Figure out port number for the user
PORT_NUM=""
if [[ ${NAME} == "gordon" ]]; then
    PORT_NUM="5001"
elif [[ ${NAME} == "todd" ]]; then
    PORT_NUM="5002"
elif [[ ${NAME} == "roger" ]]; then
    PORT_NUM="5003"
fi

# Get contacts
curl http://localhost:${PORT_NUM}/contacts
