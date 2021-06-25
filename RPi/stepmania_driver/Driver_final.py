import socket
import keyboard
import sys
from math import floor                   
import RPi.GPIO as GPIO
import signal
import numpy as np
import time
ENTER_GPIO = 20
ESC_GPIO = 16
ALIAS_UP = 'e'
ALIAS_DOWN = 'c'
time_=time.perf_counter()
debounce=0.12


def signal_handler(sig, frame):
    GPIO.cleanup()
    sys.exit(0)

def esc_callback(channel):
	global time_
	if ((time.perf_counter()-time_)>debounce):
		if (not GPIO.input(ESC_GPIO)):
			if (keyboard.is_pressed(chr(13))):
				order=b'\x05\01\01\01\01'
				for x in range(N_SENSORS):
					message=b''
					message=np.int32(1)
					sock.sendto(order, ("192.168.4."+str(10+x), UDP_PORT))
			else:
				keyboard.press(chr(27))#27=esc
		else:
			keyboard.release(chr(27))
		time_=time.perf_counter()


def enter_callback(channel):
    global time_
    if ((time.perf_counter()-time_)>debounce):
	    if keyboard.is_pressed(ALIAS_UP):
		    keyboard.send("down")
	    elif keyboard.is_pressed(ALIAS_DOWN):
		    keyboard.send("up")
	    else:
		    if not GPIO.input(ENTER_GPIO):
			    keyboard.press(chr(13))
		    else:
			    keyboard.release(chr(13))
	    time_=time.perf_counter()

if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(ENTER_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(ESC_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(ENTER_GPIO, GPIO.BOTH, callback=enter_callback, bouncetime=50)
    GPIO.add_event_detect(ESC_GPIO, GPIO.BOTH, callback=esc_callback, bouncetime=50)
    signal.signal(signal.SIGINT, signal_handler)



UDP_IP = "192.168.4.1"
UDP_PORT = 2390
N_SENSORS = 7
N_TRESHOLDS  = 2


sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # internet + UDP
sock.bind(("", UDP_PORT))


while True:
	
    data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes

    code=ord(data)
    #print(code)
    if code<N_SENSORS:
	    keyboard.press(chr(code + 97))
    else:
	    keyboard.release(chr(code + 97 - N_SENSORS))




