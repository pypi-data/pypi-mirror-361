#!/bin/bash

# Script to install Elasticsearch on Debian-based systems

# Exit immediately if a command exits with a non-zero status.
set -e

# Define Elasticsearch version - you can change this to a specific version if needed
ELASTICSEARCH_VERSION="8.x" # Or "7.x", or a specific version like "8.11.1"

echo "Starting Elasticsearch installation..."

# 1. Install prerequisite: apt-transport-https
echo "Installing apt-transport-https..."
sudo apt-get update > /dev/null
sudo apt-get install -y apt-transport-https gnupg2 > /dev/null
echo "apt-transport-https installed."

# 2. Import the Elasticsearch GPG Key
echo "Importing Elasticsearch GPG key..."
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo gpg --dearmor -o /usr/share/keyrings/elasticsearch-keyring.gpg
echo "Elasticsearch GPG key imported."

# 3. Add the Elasticsearch repository
echo "Adding Elasticsearch repository for version ${ELASTICSEARCH_VERSION}..."
if ! grep -q "artifacts.elastic.co" /etc/apt/sources.list.d/elastic-${ELASTICSEARCH_VERSION}.list 2>/dev/null; then
    echo "deb [signed-by=/usr/share/keyrings/elasticsearch-keyring.gpg] https://artifacts.elastic.co/packages/${ELASTICSEARCH_VERSION}/apt stable main" | sudo tee /etc/apt/sources.list.d/elastic-${ELASTICSEARCH_VERSION}.list
    echo "Elasticsearch repository added."
else
    echo "Elasticsearch repository already exists."
fi

# 4. Update package lists and install Elasticsearch
echo "Updating package lists..."
sudo apt-get update > /dev/null
echo "Installing Elasticsearch..."
sudo apt-get install -y elasticsearch > /dev/null
echo "Elasticsearch installed."

# 5. Reload systemd and enable Elasticsearch service
echo "Reloading systemd daemon..."
sudo systemctl daemon-reload
echo "Enabling Elasticsearch service to start on boot..."
sudo systemctl enable elasticsearch.service
echo "Elasticsearch service enabled."

# 6. Start Elasticsearch service
echo "Starting Elasticsearch service..."
sudo systemctl start elasticsearch.service

# 7. Check Elasticsearch service status
echo "Waiting a few seconds for Elasticsearch to start..."
sleep 15 # Give Elasticsearch some time to start up

echo "Checking Elasticsearch service status..."
if sudo systemctl is-active --quiet elasticsearch.service; then
    echo "Elasticsearch service is active and running."
    echo "You can test it by running: curl -X GET \"localhost:9200\""
else
    echo "ERROR: Elasticsearch service failed to start. Please check the logs:"
    echo "sudo journalctl -u elasticsearch.service"
    echo "sudo cat /var/log/elasticsearch/YOUR_CLUSTER_NAME.log"
    exit 1
fi

echo "Elasticsearch installation and startup complete!"

exit 0
