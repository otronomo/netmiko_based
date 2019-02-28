#!/usr/bin/python3
# By NOMO

from netmiko import Netmiko
from getpass import getpass
from pprint import pprint
import re
import sys


def get_arp_ios(host_dict, vrf=""):
    hostname = host_dict['host']
    try:
    # Establish connection
        print("Trying connection to " + hostname)
        connection = Netmiko(**host_dict)
    except:
        print("get_arp_ios - Could not establish ssh connection to host" + hostname)
        return -1
    # Run command with textfsm - this should return structured data
    print("Running command")
    if vrf == "":
        output = connection.send_command("sh ip arp", use_textfsm = True)
    else:
        output = connection.send_command("sh ip arp vrf " + vrf, use_textfsm = True)
    # Return structured data
    print("Returning output")
    return output

host1 = {
    'host': '10.20.20.100',
    'username': 'cisco',
    'password': 'cisco',
    'device_type': 'cisco_ios',
}





