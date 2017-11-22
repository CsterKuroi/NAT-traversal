#!/usr/bin/python2.6  
# server.py  
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
  
if len(sys.argv) <= 1:  
    print """Usage: %s <port> 
        port                the [UDP] port to bind. 
For example: 
        %s 2013"""%(sys.argv[0], sys.argv[0]);  
    sys.exit(1);  
port=sys.argv[1];  
  
print "NAT traversal & udp hold-punching"  
print "Server-side which used to help the client behind NAT to hold-punching."  
  
max_packet_size = 4096  
  
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM);  
s.bind(('', int(port)));  
print "UDP bind at %s"%(port);  
  
peers = [];  
def get_peer(code, required_peer_id):  
    for peer in peers:  
        id = peer["id"];  
        if id != required_peer_id:  
            continue;  
        (peer_id, peer_address) = (id, peer["address"]);  
        return (code, peer_id, peer_address);  
    return (1, 0, None);  
  
while True:  
    (data, address) = s.recvfrom(max_packet_size);  
    #print "get data from %s: %s"%(address, data);  
      
    obj = json.loads(data);  
    action = obj["action"];  
    code = 0;  
      
    if action == "join":  
        id = obj["id"];  
          
        for i in range(0, len(peers)):  
            if peers[i]["id"] != id:  
                continue;  
            del peers[i];  
            break;  
                  
        peers.append({"id":id, "address":address});  
        print "[join] %s %s"%(id, address);  
        continue;  
          
    if action == "find":  
        (code, peer_server_id, peer_server_address) = get_peer(code, obj["peer_server_id"]);  
        (code, peer_client_id, peer_client_address) = get_peer(code, obj["peer_client_id"]);  
        print "[find] %s %s find %s %s"%(peer_client_id, peer_server_id, peer_server_id, peer_server_address);  
        s.sendto(json.dumps({"code": code, "peer_server_address": peer_server_address, "peer_server_id": peer_server_id, "peer_client_address":peer_client_address}), address);  
          
    if action == "hole_punching":  
        (code, peer_server_id, peer_server_address) = get_peer(code, obj["peer_server_id"]);  
        (code, peer_client_id, peer_client_address) = get_peer(code, obj["peer_client_id"]);  
          
        time.sleep(3);  
        print "[hole-punching] (%s)%s <==> (%s)%s"%(peer_client_id, peer_client_address, peer_server_id, peer_server_address);  
        s.sendto(json.dumps({"action": "hole_punching", "peer_server_address":peer_server_address, "peer_client_address": peer_client_address}), tuple(peer_server_address));  
    pass;  
  
s.close(); 
