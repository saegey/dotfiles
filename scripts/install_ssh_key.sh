#!/bin/bash

# Define the array of hostnames
HOSTNAMES=("dietpi1.local", "dietpi2.local", "bignas.local", "pve.local", "docker.local") # Replace with your actual hostnames

# Your SSH user
SSH_USER="saegey"

# Your SSH public key
SSH_KEY="$HOME/.ssh/id_rsa_personal_github.pub"

# Check if SSH key exists
if [ ! -f "$SSH_KEY" ]; then
	echo "SSH public key not found at $SSH_KEY. Please generate an SSH key pair first."
	exit 1
fi

# Loop through the array of hostnames
for HOST in "${HOSTNAMES[@]}"; do
	# Check if the hostname is reachable
	if ping -c 1 -W 1 "$HOST" >/dev/null; then
		echo "Copying SSH key to $HOST"

		# Copy the SSH key to the remote machine
		ssh-copy-id -i "$SSH_KEY" "$SSH_USER@$HOST" 2>/dev/null

		if [ $? -eq 0 ]; then
			echo "Successfully copied SSH key to $HOST"
		else
			echo "Failed to copy SSH key to $HOST"
		fi
	else
		echo "Host $HOST is not reachable"
	fi
done

echo "SSH key installation script completed."
