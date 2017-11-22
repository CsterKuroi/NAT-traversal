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
  
if len(sys.argv) <= 4:  
    print """Usage: %s <server> <port> <id> <peer_server_id> 
        server              the server to connect to. 
        port                the UDP port to connect to. 
        id                  the id of peer. 
        peer_server_id     the id of peer to hole-punching to. 
For example: 
        %s 192.168.20.118 2013 peer.client peer.server"""%(sys.argv[0], sys.argv[0]);  
    sys.exit(1);  
(server, port, id, peer_server_id)=sys.argv[1:];  
port = int(port);  
  
print "NAT traversal & udp hold-punching"  
print "Peer-side which is behind NAT to hold-punching."  
  
server_endpoint = (server, port)  
max_packet_size = 4096  
  
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM);  
  
# join server  
s.sendto(json.dumps({"action": "join", "id": id}), server_endpoint);  
print "[join] %s"%(id)  
  
(peer_client_address, peer_server_address) = (None, None);  
while True:  
    # find the peer to hole-punching  
    s.sendto(json.dumps({"action": "find", "peer_client_id": id, "peer_server_id": peer_server_id}), server_endpoint);  
  
    # discovery result  
    (data, address) = s.recvfrom(max_packet_size);  
    #print "get data from %s: %s"%(address, data);  
    obj = json.loads(data);  
          
    code = obj["code"];  
    if code is not 0:  
        print "[find] peer %s not found"%(peer_server_id);  
        time.sleep(1);  
        continue;  
    peer_server_address = obj["peer_server_address"];  
    peer_client_address = obj["peer_client_address"];  
    break;  
  
# to punching hole.  
print "[find] peer(%s) address is %s"%(peer_server_id, peer_server_address);  
# step 1: directly send a packet to peer, open self tunnel.  
print "[hole-punching] try to punching hole to %s"%(peer_server_address);  
s.sendto(json.dumps({"action": "hole_punching", "peer_client_id": id, "peer_client_address":peer_client_address, "peer_server_address":peer_server_address}), tuple(peer_server_address));  
# step 2: send a packet to server, open the peer tunnel.  
print "[hole-punching] try to use server %s to punching hole"%(str(server_endpoint));  
s.sendto(json.dumps({"action": "hole_punching", "peer_client_id": id, "peer_server_id": peer_server_id}), server_endpoint);  
  
while True:  
    (data, address) = s.recvfrom(max_packet_size);  
    print "[success] %s ===> %s: %s"%(address, peer_client_address, data);  
  
s.close();
