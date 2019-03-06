#!/usr/bin/python3
# By NOMO


from netmiko import Netmiko
from pprint import pprint
from getpass  import getpass
import re

debug = 0

def debug_switch(debug, string_to_print):
    if debug == 1:
            print(string_to_print)


l3_device_list = "l3_device_list.txt"
l2_device_list = "l2_device_list.txt"

user_input = input("\nInsert IP address or MAC address: ").strip()
username = input("Insert user to log in to devices: ").strip()
password = getpass()

#user_input = "10.30.30.125"
#username = "cisco"
#password = "cisco"
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

# If userinput is an IP address
if input_type == "IP":    
    ip = user_input
    router_list = []
    try:
        with open(l3_device_list) as file_handle:
            router_list = file_handle.read().splitlines()
    except:
        print("Couldn't open file")

    for router in router_list:
        host = {
        'host': router,
        'username': username,
        'password': password,
        'device_type': "cisco_ios",
        }
        conn1 = Netmiko(**host)
        output = conn1.send_command("sh ip arp | i %s" %(ip), use_textfsm = True)

        if isinstance(output,list):
            print("\nFound ARP entry for %s in %s interface %s\n" %(ip, router, output[0]['interface']))
            #pprint(output)
            mac = output[0]['mac']
        

elif input_type == "MAC":
    mac = user_input
    debug_switch(debug,"--------DEBUG----------MAC is user input. Value: " + mac)

else:
    print("\nSomething went wrong. No MAC address found. Not sure why.")
    exit()

# At this point, take MAC no matter where it came from (user or ARP table) and search
# in all switches:
    
switch_list = []

try:
    with open(l2_device_list) as file_handle:
        switch_list = file_handle.read().splitlines()
except:
    print("\nCouldn't open file\n")

for switch in switch_list:
    host = {
    'host': switch,
    'username': username,
    'password': password,
    'device_type': "cisco_ios",
    }
    print("Connecting to " + switch)
    conn1 = Netmiko(**host)
    output = conn1.send_command("sh mac add add %s" %(mac), use_textfsm = True)

    if isinstance(output,list):
        print("\nFound MAC entry for %s in switch %s interface %s\n" %(mac, switch, output[0]['destination_port']))


