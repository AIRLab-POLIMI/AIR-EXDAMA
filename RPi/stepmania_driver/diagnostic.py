import socket
import sys
import numpy as np
from math import floor

UDP_IP = "192.168.4.1"
UDP_PORT = 2390
N_SENSORS = 7
N_TRESHOLDS  = 2


def diagnostic():
	order=b'\x02\01\01\01\01'
	for x in range(N_SENSORS):
		message=b''
		
		#for x2 in range (2):
		#		message+=int(boxes[(x*2)+x2].value).to_bytes(2, byteorder ='big')
		message=np.int32(1)
		sock.sendto(order, ("192.168.4."+str(10+x), UDP_PORT))
	#sock.sendto(message, ("192.168.4.255", UDP_PORT))	print("tested\n")



	
	
	
	






sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # internet + UDP
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.bind(("", UDP_PORT))


diagnostic()
max_=0
while True:
	
	data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
			
	code=ord(data)
	if (code>max_):
		max_=code
	print(code)

   



