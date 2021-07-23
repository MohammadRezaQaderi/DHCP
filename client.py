import socket 
import sys
import time
# we use the ethernet --> htype = 1 and hlen = 6 (FF:FF:FF:FF:FF:FF)

# the server and client port's in DHCP
Server_port = 6767
Client_port = 6868

# the massage maximum size in byte
Max_size = 1024

Ack_time_out = 15

backoff_cutoff = 120
initial_interval = 10

# discover message (find the variable bytes from )
def discover():
    op = bytes([0x01]) # client = 1 , server = 2
    htype = bytes([0x01]) 
    hlen = bytes([0x06])   
    hops = bytes([0x00])
    xid = bytes([0x39, 0x03, 0xF3, 0x26]) # is unique id to have uniqe converstation
    secs = bytes([0x00, 0x00]) 
    flags = bytes([0x00, 0x00])
    ciaddr = bytes([0x00, 0x00, 0x00, 0x00]) 
    yiaddr = bytes([0x00, 0x00, 0x00, 0x00])
    siaddr = bytes([0x00, 0x00, 0x00, 0x00])
    giaddr = bytes([0x00, 0x00, 0x00, 0x00])
    chaddr1 = bytes([0x00, 0x05, 0x3C, 0x04]) 
    chaddr2 = bytes([0x8D, 0x59, 0x00, 0x00]) 
    chaddr3 = bytes([0x00, 0x00, 0x00, 0x00]) 
    chaddr4 = bytes([0x00, 0x00, 0x00, 0x00]) 
    chaddr5 = bytes(192)
    magiccookie = bytes([0x63, 0x82, 0x53, 0x63])
    DHCPOptions1 = bytes([53 , 1 , 1]) # DHCP DISCOVER
    DHCPOptions2 = bytes([50 , 4 , 0xC0, 0xA8, 0x01, 0x64]) # 50 4 192.168.1.100

    discover_message = op + htype + hlen + hops + xid + secs + flags + ciaddr + yiaddr + siaddr + giaddr + chaddr1 + chaddr2 + chaddr3 + chaddr4 + chaddr5 + magiccookie + DHCPOptions1 + DHCPOptions2 

    return discover_message

# the request message is make to get the id that servre offer it 
def request():
    op = bytes([0x01])
    htype = bytes([0x01])
    hlen = bytes([0x06])
    hops = bytes([0x00])
    xid = bytes([0x39, 0x03, 0xF3, 0x26])
    secs = bytes([0x00, 0x00])
    flags = bytes([0x00, 0x00])
    ciaddr = bytes([0x00, 0x00, 0x00, 0x00])
    yiaddr = bytes([0x00, 0x00, 0x00, 0x00])
    siaddr = bytes([0x00, 0x00, 0x00, 0x00])
    giaddr = bytes([0x00, 0x00, 0x00, 0x00])
    chaddr1 = bytes([0x00, 0x0C, 0x29, 0xDD]) 
    chaddr2 = bytes([0x5C, 0xA7, 0x00, 0x00]) 
    chaddr3 = bytes([0x00, 0x00, 0x00, 0x00]) 
    chaddr4 = bytes([0x00, 0x00, 0x00, 0x00]) 
    chaddr5 = bytes(192)
    magiccookie = bytes([0x63, 0x82, 0x53, 0x63])
    DHCPOptions1 = bytes([53 , 1 , 3]) # request 
    DHCPOptions2 = bytes([50 , 4 , 0xC0, 0xA8, 0x01, 0x64]) # 192.168.1.100 requested
    DHCPOptions3 = bytes([54 , 4 , 0xC0, 0xA8, 0x01, 0x01]) # 192.168.1.1 DHCP SERVER

    request_message = op + htype + hlen + hops + xid + secs + flags + ciaddr + yiaddr + siaddr + giaddr + chaddr1 + chaddr2 + chaddr3 + chaddr4 + chaddr5 + magiccookie + DHCPOptions1 + DHCPOptions2 + DHCPOptions3

    return request_message

# the Users Ip is in the 16 to 20 bytes of the ack message 
def showIP(message):

    print(message[16:20])
    
    print("Your IP address is : " + str(int.from_bytes(message[16:17] , "big")) + "." +str(int.from_bytes(message[17:18] , "big")) + "." +str(int.from_bytes(message[18:19] , "big")) + "." +str(int.from_bytes(message[19:20] , "big")) )

#  count down :|
def countdown(t):
    while t:
        mins, secs = divmod(t, 60)
        timeformat = '{:02d}:{:02d}'.format(mins, secs)
        print(timeformat, end='\r')
        time.sleep(1)
        t -= 1
    return 0
print("Client start to find DHCP Server ... \n")
dest = ('<broadcast>' , Server_port)
s = socket.socket(socket.AF_INET , socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET , socket.SO_BROADCAST , 1)
s.bind(('0.0.0.0' , Client_port))




# at the first client should send discover message :)

while True:
    try:
        print("make the discover message ... \n")
        message = discover()

        print("send discover message to DHCP server ... \n")
        s.sendto(message , dest)

        message , address = s.recvfrom(Max_size)
        print(address)
        print("Recive the offer from server.")

        print("make the request message for get IP from server ... \n")
        message = request()
        s.sendto(message , dest)
        s.settimeout(Ack_time_out)
        print("get the acknowlage of IP from server ... \n")
        message , address = s.recvfrom(Max_size)
        showIP(message)
        break
    except socket.timeout as e:
        print(e)