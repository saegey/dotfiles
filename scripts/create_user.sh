#!/bin/bash

# Check if script is run as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit 1
fi

# Define the new username
#NEW_USER="newusername"  # Replace with your desired username

# Create the new user
adduser --gecos "" "$NEW_USER"

# Set password for the new user
echo "Please enter a password for the new user:"
passwd "$NEW_USER"

# Add the new user to the sudo group
usermod -aG sudo "$NEW_USER"

# Verify that the user was added to the sudo group
if groups "$NEW_USER" | grep -q "\bsudo\b"; then
  echo "User $NEW_USER added to sudo group successfully."
else
  echo "Failed to add user $NEW_USER to sudo group."
fi

# Adding user to sudoers file for password-less sudo (optional)
echo "$NEW_USER ALL=(ALL) NOPASSWD:ALL" >>/etc/sudoers.d/90-cloud-init-users

echo "User $NEW_USER has been created"
