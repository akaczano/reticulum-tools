#!/bin/bash

# Function to display the help menu
show_help() {
    echo "Usage: $0 -f [FROM] -t [TO] -m [MSG]"
    echo ""
    echo "Send a message from one user to another user."
    echo ""
    echo "Options:"
    echo "  -f      The user sending the message."
    echo "  -t      The user receiving the message."
    echo "  -m      The message to send"  
    echo "  -h      Show this help menu and exit."
    echo ""
    echo "Examples:"
    echo "  $0 -f gordon -t todd -m hello todd"
    echo "  $0 -f roger -t gordon -m what is up my dude"
    exit 0
}

# Check if the user asked for help
if [[ "$1" == "-h" || "$1" == "--help" || -z "$1" ]]; then
    show_help
fi

# Parse args
while getopts ":f:t:m:" opt; do
    case ${opt} in
        f)
            USER_FROM="${OPTARG}"
            ;;
        t)
            USER_TO="${OPTARG}"
            ;;
        m)
            MSG="${OPTARG}"
            ;;
        \?)
            echo "Error: Invalid flag -${OPTARG}" >&2
            exit 1
            ;;
        :)
            echo "Error: Flag -${OPTARG} requires an argument." >&2
            exit 1
            ;;
    esac
done

# Validate USER_FROM and get port number
USER_FROM_LOWERCASE=$(echo "${USER_FROM}" | tr '[:upper:]' '[:lower:]')
PORT_NUM=""
if [[ ${USER_FROM_LOWERCASE} == "gordon" ]]; then
    PORT_NUM="5001"
elif [[ ${USER_FROM_LOWERCASE} == "todd" ]]; then
    PORT_NUM="5002"
elif [[ ${USER_FROM_LOWERCASE} == "roger" ]]; then
    PORT_NUM="5003"
else
    echo "-f ${USER_FROM} is not a valid user"
    echo "Valid users are: Gordon, Roger, and Todd"
    exit 1
fi

# Validate USER_TO and correct case for parsing JSON
USER_TO_LOWERCASE=$(echo "${USER_TO}" | tr '[:upper:]' '[:lower:]')
FIRST_LETTER_UPPER_CASE_NAME=""
if [[ ${USER_TO_LOWERCASE} == "gordon" || ${USER_TO_LOWERCASE} == "todd" || ${USER_TO_LOWERCASE} == "roger" ]]; then
    FIRST_LETTER_UPPER_CASE_NAME=$(awk '{print toupper(substr($0,1,1)) substr($0,2)}' <<< "${USER_TO_LOWERCASE}")
else
    echo "-t ${USER_TO} is not a valid user"
    echo "Valid users are: Gordon, Roger, and Todd"
    exit 1
fi

# Validate USER_FROM is not equal to USER_TO
if [[ ${USER_FROM_LOWERCASE} == ${USER_TO_LOWERCASE} ]]; then
    echo "Cannot message yourself. Go make friends!"
    exit 1
fi

# Get contacts and extract user id
contacts_json=$(curl -s http://localhost:${PORT_NUM}/contacts)
USER_ID=$(jq -r --arg name "${FIRST_LETTER_UPPER_CASE_NAME}" '.[] | select(.name == $name) | .id' <<< "${contacts_json}")

# Send the message
curl -X POST -d '{"user": '${USER_ID}', "message": "'${MSG}'"}' -H 'Content-Type: application/json' http://localhost:${PORT_NUM}/send
