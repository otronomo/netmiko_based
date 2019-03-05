#!/usr/bin/python3
# By NOMO

print("debug0")

from netmiko import Netmiko
print("debug0.0")
from pprint import pprint
print("debug0.00")
from getpass  import getpass
print("debug0.00")
import re

debug = 1

def debug_switch(debug, string_to_print):
    if debug == 1:
            print(string_to_print)


l3_device_list = "l3_device_list.txt"
l2_device_list = "l2_device_list.txt"
'''
user_input = input("\nInsert IP address or MAC address: ").strip()
username = input("Insert user to log in to devices: ").strip()
password = getpass()
'''
user_input = "aabb.cc00.8000"
username = "cisco"
password = "cisco"
mac = "1"

# From https://stackoverflow.com/questions/10086572/ip-address-validation-in-python-using-regex
ValidIpAddressRegex = "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$";
#
ValidMacAddress_1 = "^([0-9a-f]{2}(?::[0-9a-f]{2}){5})$"
ValidMacAddress_2 = "^([0-9a-f]{4}(?:\-[0-9a-f]{4}){2})$"
ValidMacAddress_3 = "^([0-9a-f]{4}(?:\.[0-9a-f]{4}){2})$"

pattern_ip = re.compile(ValidIpAddressRegex)
pattern_mac_1 = re.compile(ValidMacAddress_1)
pattern_mac_2 = re.compile(ValidMacAddress_2)
pattern_mac_3 = re.compile(ValidMacAddress_3)

input_type = ""

if pattern_ip.match(user_input) is not None:
    input_type = "IP"
    debug_switch(debug,"--------DEBUG----------Input_type = IP")
elif pattern_mac_1.match(user_input) is not None:
    input_type = "MAC"
    debug_switch(debug,"--------DEBUG----------Input_type = MAC")
elif pattern_mac_2.match(user_input) is not None:
    input_type = "MAC"
    debug_switch(debug,"--------DEBUG----------Input_type = MAC")
elif pattern_mac_3.match(user_input) is not None:
    input_type = "MAC"
    debug_switch(debug,"--------DEBUG----------Input_type = MAC")
else:
    print("\nThe input format does not match an IP address or a MAC address.\n" + \
          "MAC valid formats:\n" +  \
          "  XX:XX:XX:XX:XX\n" + \
          "  XXXX-XXXX-XXXX\n" + \
          "  XXXX.XXXX.XXXX\n")
    exit()

if input_type == "IP":    
    ip = user_input


elif input_type == "MAC":
    mac = user_input
    debug_switch(debug,"--------DEBUG----------MAC is user input. Value: " + mac)
    
# At this point, take MAC no matter where it came from (user or ARP table) and search
# in all switches:
    
switch_list = []

try:
    with open(l2_device_list) as file_handle:
        switch_list = file_handle.read().splitlines()
except:
    print("Couldn't open file")

for switch in switch_list:
    host = {
    'host': switch,
    'username': username,
    'password': password,
    'device_type': "cisco_ios",
    }
    print("Calling func with arg:" + switch)
    conn1 = Netmiko(**host)
    output = conn1.send_command("sh mac add add %s" %(mac), use_textfsm = True)

    if isinstance(output,list):
        pprint(output)


# By this point, user_input should have been identified as MAC, IP or smthing else.
# This "else" clause shour never run but just in case...
else:
    print("\nSomething went wrong. No MAC address found. Not sure why.")
    exit()


# At this point, take MAC no matter where it came from (user or ARP table) and search
# in all switches:


