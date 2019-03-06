#!/usr/bin/python3
# By NOMO

from netmiko import Netmiko
from getpass import getpass
import re
import os
from pprint import pprint
import sys
import socket

# Takes connection handler and command string.
# Returns output of command as list of lines.
def getOutputLines( connection, command ):
    output = connection.send_command(command)
    output_lines = output.splitlines()
    return output_lines;


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

conn1 = Netmiko(**nexus)
interfaces = []
results = {}

# Get all relevant interfaces into a list.
output_lines = getOutputLines(conn1, "show interface status | i connected")

for line in output_lines:
    interface = line.split()[0]
    interfaces.append(interface)

# Use that list to create a dictionary interface:[attributes]
# Starting with description and port-channel.
for interface in interfaces:
    description = ""
    channel_group = ""
    output_lines = getOutputLines(conn1, "show run interface " + interface)
    for line in output_lines:
        if "description" in line:
            description = line.replace(",", " ")
        if "channel-group" in line:
            channel_group = line
    if len(description) == 0:
        description = "NO_DESCRIPTION"
    else:
        description = re.findall('description (.*)', description)[0]
    if len(channel_group) == 0:
        channel_group = "NO_GROUP"

    # Populate the dictionary with current attributes
    results[interface] = [description, channel_group]

# Add cdp neighbor information to the list of attributes for each if.
output = conn1.send_command("show cdp neigh", use_textfsm=True)
for device in output:
    neighbor = device['neighbor']
    local_if = device['local_interface']
    remote_if = device['neighbor_interface']
    for interface, attributes in results.items():
        interface_id = re.findall('\d.*', interface)[0]
        if interface_id == re.findall('\d.*', local_if)[0]:
            results[interface].append("CDP info: Connected to %s on %s" % (neighbor, remote_if))

# Dump results on CSV file
filename = "connected_ifs_" + nexus['host'] + ".csv"
current_dir = os.getcwd()
with open(filename, 'w') as handle:
    for interface, attributes in results.items():
        handle.write(interface)
        for attribute in attributes:
            handle.write(',' + attribute)
        handle.write('\n')
#pprint(results)
file_path = current_dir + "/" + filename
print("\n Results can be found in" + file_path + "\n")

