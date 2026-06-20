#!/bin/bash

if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit 1
fi

if [ -z "$1" ]; then
  echo "Usage: $0 <username>"
  exit 1
fi

NEW_USER="$1"

adduser --gecos "" "$NEW_USER"

echo "Please enter a password for the new user:"
passwd "$NEW_USER"

usermod -aG sudo "$NEW_USER"

if groups "$NEW_USER" | grep -q "\bsudo\b"; then
  echo "User $NEW_USER added to sudo group successfully."
else
  echo "Failed to add user $NEW_USER to sudo group."
fi

echo "$NEW_USER ALL=(ALL) NOPASSWD:ALL" >>/etc/sudoers.d/90-cloud-init-users
echo "User $NEW_USER has been created"
