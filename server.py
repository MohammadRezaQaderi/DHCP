import socket 
import sys
import time
import threading
import json
import struct
# we use the ethernet --> htype = 1 and hlen = 6 (FF:FF:FF:FF:FF:FF)

# the server and client port's in DHCP
Server_port = 6767
Client_port = 6868

# the massage maximum size in byte
Max_size = 1024



# make the offer message 
def offer():
    op = bytes([0x02])
    htype = bytes([0x01])
    hlen = bytes([0x06])
    hops = bytes([0x00])
    xid = bytes([0x39, 0x03, 0xF3, 0x26])
    secs = bytes([0x00, 0x00])
    flags = bytes([0x00, 0x00])
    ciaddr = bytes([0x00, 0x00, 0x00, 0x00])
    yiaddr = bytes([0xC0, 0xA8, 0x01, 0x64]) # ip client
    siaddr = bytes([0xC0, 0xA8, 0x01, 0x01]) # ip server
    giaddr = bytes([0x00, 0x00, 0x00, 0x00])
    chaddr1 = bytes([0x00, 0x05, 0x3C, 0x04]) 
    chaddr2 = bytes([0x8D, 0x59, 0x00, 0x00]) 
    chaddr3 = bytes([0x00, 0x00, 0x00, 0x00]) 
    chaddr4 = bytes([0x00, 0x00, 0x00, 0x00]) 
    chaddr5 = bytes(192)
    # the standard magic cookie
    magiccookie = bytes([0x63, 0x82, 0x53, 0x63])
    DHCPOptions1 = bytes([53 , 1 , 2])
    DHCPOptions2 = bytes([1 , 4 , 0xFF, 0xFF, 0xFF, 0x00])
    DHCPOptions3 = bytes([3 , 4 , 0xC0, 0xA8, 0x01, 0x01]) #192.168.1.1 router
    DHCPOptions4 = bytes([51 , 4 , 0x00, 0x01, 0x51, 0x80]) #86400s(1 day) IP address lease time
    DHCPOptions5 = bytes([54 , 4 , 0xC0, 0xA8, 0x01, 0x01]) # DHCP server

    offer_message = op + htype + hlen + hops + xid + secs + flags + ciaddr + yiaddr + siaddr + giaddr + chaddr1 + chaddr2 + chaddr3 + chaddr4 + chaddr5 + magiccookie + DHCPOptions1 + DHCPOptions2 + DHCPOptions3 + DHCPOptions4 + DHCPOptions5
    return offer_message




# make the ack message 
def ack():
    op = bytes([0x02])
    htype = bytes([0x01])
    hlen = bytes([0x06])
    hops = bytes([0x00])
    xid = bytes([0x39, 0x03, 0xF3, 0x26])
    secs = bytes([0x00, 0x00])
    flags = bytes([0x00, 0x00])
    ciaddr = bytes([0x00, 0x00, 0x00, 0x00])
    yiaddr = bytes([0xC0, 0xA8, 0x01, 0x64])
    siaddr = bytes([0xC0, 0xA8, 0x01, 0x01])
    giaddr = bytes([0x00, 0x00, 0x00, 0x00])
    chaddr1 = bytes([0x00, 0x05, 0x3C, 0x04]) 
    chaddr2 = bytes([0x8D, 0x59, 0x00, 0x00]) 
    chaddr3 = bytes([0x00, 0x00, 0x00, 0x00]) 
    chaddr4 = bytes([0x00, 0x00, 0x00, 0x00]) 
    chaddr5 = bytes(192)
    # the standard magic cookie
    magiccookie = bytes([0x63, 0x82, 0x53, 0x63])
    DHCPOptions1 = bytes([53 , 1 , 5]) # 5 for ACK and 6 for NACK
    DHCPOptions2 = bytes([1 , 4 , 0xFF, 0xFF, 0xFF, 0x00]) # subnet mask 255.255.255.0
    DHCPOptions3 = bytes([3 , 4 , 0xC0, 0xA8, 0x01, 0x01]) #192.168.1.1 router
    DHCPOptions4 = bytes([51 , 4 , 0x00, 0x01, 0x51, 0x80]) #86400s(1 day) IP address lease time
    DHCPOptions5 = bytes([54 , 4 , 0xC0, 0xA8, 0x01, 0x01]) # DHCP server

    ack_message = op + htype + hlen + hops + xid + secs + flags + ciaddr + yiaddr + siaddr + giaddr + chaddr1 + chaddr2 + chaddr3 + chaddr4 + chaddr5 + magiccookie + DHCPOptions1 + DHCPOptions2 + DHCPOptions3 + DHCPOptions4 + DHCPOptions5
    return ack_message


def ips(start, end):
    start = struct.unpack('>I', socket.inet_aton(start))[0]
    end = struct.unpack('>I', socket.inet_aton(end))[0]
    return [socket.inet_ntoa(struct.pack('>I', i)) for i in range(start, end)]

def read_config():
    CONFIG = []
    temp = json.loads(open("config.json" , "r").read())
    if temp["pool_mode"] == "subnet":
        ip = temp['subnet']['ip_block']
        cidr = sum(bin(int(x)).count('1') for x in temp['subnet']['subnet_mask'].split('.'))
        # handle do the ips :)

    elif temp["pool_mode"] == "subnet":
        start_ip =temp['range']['from']
        end_ip = temp['range']['to']
        CONFIG["ip"] = list(ips(start_ip, end_ip))
        print(CONFIG["ip"])
    CONFIG["lease_time"] = float(temp['lease_time'])
    
    if "reservation_list" in temp.keys():
        CONFIG["reservation"] = temp["reservation_list"]

    if "black_list" in temp.keys():
        CONFIG["black_list"] = temp["black_list"]

    CONFIG["used"] = dict()
    return CONFIG

# check that the mac address have get ip before
def reserv_id(mac , conf):
    have = False
    for x in conf["reservation_list"]:
        if x[0] == mac:
            ip = x[1]
            have = True
    return have , ip

# the mac list we did not get them ip :)))
def black_list(mac  , conf):
    get_or_not = True
    for x in conf["black_list"]:
       if  x ==  mac  :
           get_or_not = False
    return get_or_not

# when we request to client we set that ip in reservation list
# def get_ip(ip , conf):


print("DHCP server is run now ... \n")
s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST,1)
s.bind(('' , Server_port))

# the destination always is 255.255.255.255 that not have ip address
dest = ('255.255.255.255' , Client_port)
while True:
    try:
        # at the first the server should get the discovery message 
        print("wait for a client send the discovery message ... \n")
        message , address = s.recvfrom(Max_size)
        print("the discovery message given by server ... \n")
        # time.sleep(400)
        #  server should send the offer to client 
        print("make the offer message ... \n")
        message = offer()
        s.sendto(message , dest)
        
        while True:
            try:
                # wait for the client request to server for IP
                print("wait for request of client ... \n")
                message , address = s.recvfrom(Max_size)
                print("the request recive from cilent ... \n")

                print("send the ack to client ... \n")
                message = ack()
                s.sendto(message , dest)
                break
            except:
                raise
    except:
        raise