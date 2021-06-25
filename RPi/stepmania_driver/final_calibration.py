import socket
import sys
from guizero import App, Text, TextBox, Box, PushButton
from math import floor

UDP_IP = "192.168.4.1"
UDP_PORT = 2390
N_SENSORS = 7
N_TRESHOLDS  = 2


def Test(boxes):
	
	command=0;
	
	for x in range(N_SENSORS):
		message=b''
		if (boxes[N_SENSORS*2+x].value=="Auto"):
			command=3
		elif (boxes[N_SENSORS*2+x].value=="Manual"):
			command=0
		else:
			command=3
			print(f"Unrecognised command {boxes[N_SENSORS*2+x].value} for sensor number {x}, automatic mode will be used")
		order=(command).to_bytes(1, byteorder ='big')
		for x2 in range (2):
			message+=int(boxes[(x*2)+x2].value).to_bytes(2, byteorder ='big')
		sock.sendto(order+message, ("192.168.4."+str(10+x), UDP_PORT))
	#sock.sendto(message, ("192.168.4.255", UDP_PORT))
	print("tested\n")

def Save(boxes):
	file = open("Calibration_tresholds.txt","w")
	for x in range(N_SENSORS):
		file.write(boxes[x*2].value)
		file.write(",")
		file.write(boxes[(x*2)+1].value)
		file.write("\n")
	file.close()
	command=[]
	file = open("Sensor_commands.txt","w")
	for x in range(N_SENSORS):
		file.write(boxes[N_SENSORS*2+x].value)
		if (boxes[N_SENSORS*2+x].value=="Auto"):
			command.append(4)
		elif (boxes[N_SENSORS*2+x].value=="Manual"):
			command.append(1)
		else:
			command.append(4)
			print(f"Unrecognised command {boxes[N_SENSORS*2+x].value} for sensor number {x}, automatic mode will be used")
		file.write("\n")
	file.close()
	
	
	
	#for x in range(len(boxes)):
		#message+=int(boxes[x].value).to_bytes(2, byteorder ='big')
	#sock.sendto(message, ('<broadcast>', UDP_PORT))
	for x in range(N_SENSORS):
		message=b''
		order=(command[x]).to_bytes(1, byteorder ='big')
		for x2 in range (2):
				message+=int(boxes[(x*2)+x2].value).to_bytes(2, byteorder ='big')
		sock.sendto(order+message, ("192.168.4."+str(10+x), UDP_PORT))
	print ("saved\n")



def Calibrate():
	tresholds=[]
	with open("Calibration_tresholds.txt") as f:
		data = f.read()
		data=data.replace("\n",",")
		tresholds=data.split(",")#WARNING: SE CAMBIA (AUMENTA) IL NUMERO massimo di senori non funziona più
		tresholds.pop()
	
	#sock.sendto(message, ('<broadcast>', UDP_PORT))
	#data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
	
	#for x in range(len(tresholds)):
	#	tresholds[x]=int(tresholds[x])
	

	
	app = App(title="Calibration menu", layout="grid")
	#message = Text(app, text="Choose the appropiate treshold values", grid=[1,0,2,1])#[x,y,xspan,yspan]
	message = Text(app, text="Sensor ID", grid=[0,0])
	message2 = Text(app, text="Press", grid=[1,0])
	message3 = Text(app, text="Sensor color", grid=[2,0])
	message4 = Text(app, text="Release", grid=[3,0])
	message6 = Text(app, text="    ", grid=[4,0])
	message6 = Text(app, text="Command", grid=[5,0])
	
	
	with open("Sensor_colors.txt") as f:
		data = f.read()
		colors=data.split("\n")
	with open("Sensor_commands.txt") as f:
		data = f.read()
		commands=data.split("\n")
	
	id_boxes=[]
	id_texts=[]
	color_boxes=[]
	for x in range(N_SENSORS):
		id_boxes.append(Box(app, grid=[0,x+1]))
		#id_boxes[x].bg="red"
		id_texts.append(Text(id_boxes[x], text=str(x)))
		color_boxes.append(Box(app, width=50, height=15,grid=[2,x+1]))
		color_boxes[x].bg=colors[x]
	
	boxes=[]
	for x in range (N_SENSORS*2):
		boxes.append(TextBox (app, text=tresholds[x], grid=[((x%2)*2)+1,floor(x/2)+1]))
	for x in range (N_SENSORS):
		boxes.append(TextBox (app, text=commands[x], grid=[5,x+1]))
	print(len(boxes))
	
	placeholder=Box(app,height=10, width=10 ,grid=[1,N_SENSORS+2])
	placeholder=Box(app,height=10, width=10 ,grid=[3,N_SENSORS+2])
	test_button = PushButton(app, command=Test, text="test", args=[boxes], grid=[1,N_SENSORS+3])
	save_button = PushButton(app, command=Save, text="save", args=[boxes], grid=[3,N_SENSORS+3])
	
	
	app.display()






sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # internet + UDP
sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
sock.bind(("", UDP_PORT))


Calibrate()


   



