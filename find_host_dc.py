#!/usr/bin/python3
# By NOMO

print("debug0")

from netmiko import Netmiko
from getpass import getpass
from pprint import pprint
import re

print("debug1")

l3_device_list = "l3_device_list.txt"
l2_device_list = "l2_device_list.txt"

mac_addr = "aabb.cc00.1010"


print("debug2")

switch_list = []

try:
    with open(l2_device_list) as file_handle:
        switch_list = file_handle.read().splitlines()
except:
    print("Couldn't open file")

for switch in switch_list:
    #get_one_mac_address(switch, mac_addr)
    pprint(switch)        

print("debug3")

print("debug4")

print("debug5")

print("debug6")
