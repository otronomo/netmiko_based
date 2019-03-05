#!/usr/bin/python3
# By NOMO

print("debug0")

from netmiko import Netmiko
print("debug0.0")
from pprint import pprint

print("debug1")

# Takes switch host dict and mac. Returns formatted output.
def get_one_mac_address(mac, switch, username, password, device_type):
    host = {
    'host': switch,
    'username': username,
    'password': password,
    'device_type': device_type,
    }
    conn1 = Netmiko(**host)
    output = conn1.send_command("sh mac add add %s" %(mac), use_textfsm = True)
    return output


l3_device_list = "l3_device_list.txt"
l2_device_list = "l2_device_list.txt"

mac_addr = "aabb.cc00.8000"


print("debug2")

switch_list = []

try:
    with open(l2_device_list) as file_handle:
        switch_list = file_handle.read().splitlines()
except:
    print("Couldn't open file")

for switch in switch_list:
    print("Calling func with arg:" + switch)
    mac_table_entry = get_one_mac_address(mac_addr, switch, "cisco", "cisco", "cisco_ios")
    if isinstance(mac_table_entry,list):
        pprint(mac_table_entry)

print("debug3")

