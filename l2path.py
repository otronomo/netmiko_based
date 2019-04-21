#!/usr/bin/python3
# By NOMO

print("1")
#from netmiko import Netmiko
from netmiko import ConnectHandler
print("2")
from getpass import getpass
print("3")
from pprint import pprint
print("4")
import re
print("5")

# Verbosity flags.
debug = 1
informational = 1
def debugCode(debug, string_to_print):
    if debug == 1:
            print(string_to_print)

# Request and validate IP from user input. Returns IP as string.
def askForIp():
    # 3 attempts to input a valid IP address.
    for i in range(3):    
        ip = input("Enter IP address: ").strip()    
        # IP address validation expression from: https://stackoverflow.com/questions/10086572/ip-address-validation-in-python-using-regex
        ValidIpAddressRegex = "^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$";
        pattern_ip = re.compile(ValidIpAddressRegex)
        if pattern_ip.match(ip) is not None:            
            debugCode(debug,"\n--------DEBUG----------Input validated = IP\n")
            return ip
            break
        else:
            print("\nThe input format does not match an IP address\n")
    print ("\nToo many attempts to input an IP address. Exiting.\n")
    exit()

# User credentials. Returns as list.    
def askForCreds():
    #username = input("\nUsername: ")
    username = "cisco"
    #password = getpass("Password: ")   
    password = "cisco"
    creds = [username, password]
    return creds    

# Connects to host as, checks IOS/NX-OS, reconnects if NX-OS, returns conn handle.
def connectToNextHop(ip, creds):
    next_host = {
        'host': ip,
        'username': creds[0],
        'password': creds[1],
        'device_type': "cisco_ios",
        }
    # Figure out if IOS or NX-OS
    conn1 = ConnectHandler(**next_host)
    output = conn1.send_command("sh ver")
    if "Cisco IOS" in output:
        debugCode(informational,"\n--------INFORM----------Device type is IOS.\n")
    elif "Cisco NX-" in output:
        conn1.disconnect()
        debugCode(debug,"\n--------DEBUG----------Device type is not IOS. Trying with NX-OS.\n")
        debugCode(informational,"\n--------INFORM----------Device type is NX-OS.\n")
        next_host = {
            'host': ip,
            'username': creds[0],
            'password': creds[1],
            'device_type': "cisco_nxos"
            }
        conn1 = ConnectHandler(**next_host)
        print( conn1.find_prompt() )
    else:
        print("Unable to determine Device Type of %s. Doesn't seem to be IOS or NX-OS" % ip)
        exit()
    return conn1 

# Takes a host IP, the destination IP and a connHandle.    
# Gathers next L3 hops from sh ip route command. Returns a list of IPs.
def getNextHopIp(host_ip, destination_ip, conn_handle):
    output = conn_handle.send_command("sh ip route %s" %(destination_ip)).splitlines()
    routes = dict()    
    routes["ips_next_hop"] = []
    for line in output:
        # If only default is available.
        if "not in table" in line:
            print("No specific route to destinantion in %s, using 0.0.0.0/0 instead." % (destination_ip))
            routes = getNextHopIp(host_ip, "0.0.0.0", conn_handle)
            return routes
            break           
        # Take the source of the route (static, ospf, bgp...)
        elif "Known via" in line:
            routes['known_via'] = re.search(r"Known via \"(.+?)\"", line).group(1) 
        # Store all available next-hop IPs in a list.
        elif re.search( r"^\s+(.+\d+\.\d+\.\d+\.\d)", line ) != None:            
            #ip_next_hop = re.search( r"^\s+\D+(\d+\.\d+\.\d+\.\d), from", line ).group(1)
            ip_next_hop = re.search( r"^\s+\D+(\d+\.\d+\.\d+\.\d+)", line ).group(1)
            routes["ips_next_hop"].append(ip_next_hop)    
    return routes

# Takes a host IP, a list of directly connected IPs and a connHandle
# Returns a dict of IP:egress physical interfaces.
def getEgressInterface(host_ip, routes, conn_handle):
    # Run through that list to find out the egress interface for each available next hop
    egress_interfaces = {}
    for next_hop in routes['ips_next_hop']:
        # Arp for the mac address
        output = conn_handle.send_command("sh ip arp %s" %(next_hop), use_textfsm = True)
        mac = output[0]['mac']
        # Account for Vlan interfaces (extra "sh mac add" command)
        if "vlan" not in output[0]['interface'].lower():
            egress_interface = output[0]['interface']
        else:           
            output = conn_handle.send_command("sh mac add add %s" %(mac), use_textfsm = True)
            egress_interface = output[0]['destination_port']
            #pprint(output[0])
        egress_interfaces[next_hop] = egress_interface
        #pprint(egress_interface)
    return egress_interfaces
    

# Takes a host IP and a destination IP. Returns information of egrees interfaces as dict.
def gatherEgressInfo(host_ip, destination_ip, creds, visited_hosts):

    # Check if host already visited    
    conn1 = connectToNextHop(host_ip, creds)
    hostname = conn1.find_prompt()
    #print("\nCONNECTED TO "+hostname+"\n")    
    
    if hostname not in visited_hosts:
        visited_hosts.append(hostname)       
            
        next_hops = getNextHopIp(host_ip, destination_ip, conn1)
        print("On host " + hostname + ", to reach " + destination_ip + " next hops:")
        print("Routes known via \"" + next_hops['known_via'] + "\"")
        for nh in next_hops['ips_next_hop']:
            print(nh)
        print("\n")
        
        egress_interfaces = getEgressInterface(host_ip, next_hops, conn1)
        print("On host " + hostname + ", to reach " + destination_ip + " egress ifs are:")
        for key, value in egress_interfaces.items():            
            print("Next hop "+key+" reached via egress interface "+value)
        #pprint(egress_interfaces)
        print("\n\n")
        
        if "ospf" in next_hops['known_via'] or "static" in next_hops['known_via']:        
            debugCode(debug,"\n--------DEBUG----------ospf or static in via, calling again\n")
            for next_ip in next_hops['ips_next_hop']:
                debugCode(debug,"\n--------DEBUG----------Func run with next_ip: " +next_ip+ "\n")
                gatherEgressInfo(next_ip, destination_ip, creds, visited_hosts)
    
    else:
        print("\nHost "+ hostname +"has already been checked.\n")    
        
print("\nInput the SOURCE IP.")   
#source_ip = askForIp()
source_ip = "10.20.20.100"

print("\nInput the DESTINATION IP.")   
#destination_ip = askForIp()
destination_ip = "10.9.9.9"

creds = askForCreds()

# Keep list of all hosts where tried. Avoid duplicity.
visited_hosts = []
gatherEgressInfo(source_ip, destination_ip, creds, visited_hosts)




    
 
