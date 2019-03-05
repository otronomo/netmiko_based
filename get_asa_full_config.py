#!/usr/bin/python3
# BY NOMO


from netmiko import Netmiko
from getpass import getpass
from datetime import datetime
from pprint import pprint
import re
import os
import sys
import socket

# Vars

config_dir = "/home/reponeg/logs/asa_configs"

# Function for DNS resolution

def hostnameLookup(hostname):
    try:
        socket.gethostbyname(hostname)
        return 1                        # If lookup works 
    except socket.error:
        return 0                        # If lookup fails

def getShowRun(connection_handle, context, dirname):
    output = connection_handle.send_command("changeto context " + context)
    sh_run = connection_handle.send_command("show run")
    hostname_simple = re.findall( r'(.+?)\.+', hostname_arg )[0]
    file_path = dirname + "/" + "sh_run_" + hostname_simple +"_"+ context + ".txt"
    with open(file_path, "w") as file_handle:
        file_handle.write(sh_run)
    return 1


# Check arguments for hostname and hostname dns resolution

if  len(sys.argv) < 4:
    print("\nMissing parameter. Please enter the hostname or IP address:")
    print("\nUsage:", sys.argv[0], "<hostname>\n\n")
    exit()
elif len(sys.argv) > 4:
    print("Too many parameters. Use a single hostname.")
    exit()

hostname_arg = sys.argv[1]
username = sys.argv[2]
password = sys.argv[3]

dns_lookup_result = hostnameLookup(hostname_arg)

if dns_lookup_result == 0:
    print("Hostname lookup for %s failed. Please check name and retry." %(hostname_arg) )
    exit()


# Device

asa = {
    'host': hostname_arg,
    'username': username,
    'password': password,
    'device_type': 'cisco_asa'
}

auth_pending = True
while auth_pending:
    try:
        conn1 = Netmiko(**asa)
        auth_pending = False
    except:
        print("Authentication failed. This is host " + hostname_arg)
        asa['username'] = input("\nEnter your Username FOR THIS HOST): ")
        asa['password'] = getpass()  
        try:
            conn1 = Netmiko(**asa)
            pass
        except:
            print("Failed to authenticate on " + hostname_arg + "\nTry again.")
            pass

# Move to context sys to grab the list of all contexts
command = "changeto context sys"
output = conn1.send_command(command)

command = "show run | i context"
output = conn1.send_command(command).splitlines()

# Get the list
context_list = []
for line in output:
    if line.startswith("context "):
        context_name = line.replace("context ", "")
        context_list.append(context_name)


# Start hopping contexts and retrieving running configs

for context in context_list:
    getShowRun(conn1, context, config_dir)
print("Retrieved config for contexts:") 
print(context_list)
print("\n")


