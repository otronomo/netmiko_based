#!/usr/bin/python3
# By NOMO


from netmiko import Netmiko
from getpass import getpass
from pprint import pprint
import re
import sys

# Retruns formatted ARP table. Takes VRF="" as arg:
# LIST of DICTS 
def get_arp_ios(host_dict, vrf=""):
    hostname = host_dict['host']
    try:
    # Establish connection
        #print("Trying connection to " + hostname)
        connection = Netmiko(**host_dict)
    except:
        print("get_arp_ios - Could not establish ssh connection to host" + hostname)
        return -1
    # Run command with textfsm - this should return structured data
    #print("Running command")
    if vrf == "":
        output = connection.send_command("sh ip arp", use_textfsm = True)
    else:
        output = connection.send_command("sh ip arp vrf " + vrf, use_textfsm = True)
    # Return structured data
    #print("Returning output")
    return output
    
# Retruns formatted sh ip int brie table:
# LIST of DICTS     
def get_ip_int_bri_ios(host_dict):
    hostname = host_dict['host']
    try:
    # Establish connection
        #print("Trying connection to " + hostname)
        connection = Netmiko(**host_dict)
    except:
        print("get_ip_int_bri_ios - Could not establish ssh connection to host" + hostname)
        return -1
    # Run command with textfsm - this should return structured data
    #print("Running command")
    output = connection.send_command("sh ip int brie", use_textfsm = True)
    # Return structured data
    #print("Returning output")
    return output



