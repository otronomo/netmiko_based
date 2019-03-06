#!/usr/bin/python3
# BY NOMO


from netmiko import Netmiko
from getpass import getpass
from datetime import datetime
import re
import os
import sys
import socket


# Function for DNS resolution

def hostnameLookup(hostname):
    try:
        socket.gethostbyname(hostname)
        return 1                        # If lookup works 
    except socket.error:
        return 0                        # If lookup fails


# Check arguments for hostname and hostname dns resolution

if  len(sys.argv) < 2:
    print("\nMissing parameter. Please enter the nexus hostname or IP address:")
    print("\nUsage:", sys.argv[0], "<hostname>\n\n")
    exit()
elif len(sys.argv) > 2:
    print("Too many parameters. Use a single hostname.")
    exit()

hostname_arg = sys.argv[1]
dns_lookup_result = hostnameLookup(hostname_arg)

if dns_lookup_result == 0:
    print("Hostname lookup failed. Please check name and retry.")
    exit()


# Device

nexus = {
    'host': hostname_arg,
    'username': input("Enter your Username: "),
    'password': getpass(),
    'device_type': 'cisco_nxos'
}


# Command list


filename = "checklist_commands.txt"

with open(filename) as file_handle:
    check_list = file_handle.read().splitlines()

conn1 = Netmiko(**nexus)


# Timestamp string nice and clean

timestamp = str(datetime.now()).replace(' ', '_')
timestamp = re.findall('(.*?)\.', timestamp)[0]

# Create new dir with unique name to store new output. 

current_dir = os.getcwd()
new_dir = current_dir + '/checklist_' + nexus['host'] + '_' + timestamp
try:
    os.mkdir(new_dir)
except OSError:
    print("Creation of directory %s failed" % new_dir)

# Run command list. 1 output to 1 file.

for command in check_list:

    filename = new_dir + '/' + \
               command.replace(' ', '_') + \
               '_' + \
               nexus['host'] + \
               '_' + \
               str(timestamp) \
               + '.txt'

    with open(filename, "w") as handle:
        output = conn1.send_command(command)
        handle.write(output)

print("\n You can find the results of the checklist at: " + new_dir + "\n")
