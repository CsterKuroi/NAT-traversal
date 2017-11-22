#!/usr/bin/python2.6  
# peer.server.py  
import signal;  
import sys;  
def handler(signum, frame):    
    print 'usr press ctrl+c, exit';    
    sys.exit(0)  
signal.signal(signal.SIGINT, handler)  
  
##################################################################  
import socket;  
import json;  
import time;  
  
if len(sys.argv) <= 3:  
    print """Usage: %s <server> <port> <id>  
        server              the server to connect to. 
        port                the UDP port to connect to. 
        id                  the id of peer. 
For example: 
        %s 192.168.20.118 2013 peer.server"""%(sys.argv[0], sys.argv[0]);  
    sys.exit(1);  
(server, port, id) = sys.argv[1:];  
port = int(port);  
  
print "NAT traversal & udp hold-punching"  
print "Peer-server-side which is behind NAT to hold-punching."  
print "peer-server means it wait for peer-client to hole-punching with"  
  
server_endpoint = (server, port)  
max_packet_size = 4096  
  
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM);  
  
# join server  
s.sendto(json.dumps({"action": "join", "id": id}), server_endpoint);  
print "[join] %s"%(id)  
  
while True:  
    # recv request from server.  
    (data, address) = s.recvfrom(max_packet_size);  
    #print "get data from %s: %s"%(address, data);  
    obj = json.loads(data);  
          
    action = obj["action"];  
    if action != "hole_punching":  
        continue;  
          
    if "peer_client_address" not in obj:  
        continue;  
          
    peer_client_address = obj["peer_client_address"];  
    peer_server_address = obj["peer_server_address"]  
    print "[open_hole] by %s"%(str(address));  
      
    # send a packet to peer.client to open the hole.  
    s.sendto(json.dumps({"action": "open_hole", "id": id}), tuple(peer_client_address));  
      
    data = json.dumps({"action": "video", "video": "xxxxx video xxxxxx"})  
    while True:  
        ret = s.sendto(data, tuple(peer_client_address));  
        print "[success] %s ===> %s: %s"%(peer_server_address, peer_client_address, data);  
        time.sleep(3);  
      
    break;  
  
s.close();
