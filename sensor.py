from packet import packet
from client import client
import time
import socket

import json

TYPESIZE = 2
DATASIZE = 10
HEADERSIZE = TYPESIZE + DATASIZE



f_name = 'log.txt'#input("Informe o Arquivo com dados do sensor: ").strip()
place = 'sala'#input("Informe o comodo onde esta o sensor: ").strip()
read_time = 10#float(input("Informe o intervalo de leitura do sensor: ").strip())
delay = 5#float(input("Informe o timeout do sensor: ").strip())

print(f_name,place,read_time,delay)

f_name = f_name
f = open(f_name,"r")
data_pkt = {}


s = client(timeout = delay)

if s.start():
	i = 0
	# for line in f:
	start_t = time.time()
	while True:
		if( time.time() - start_t >= s.timeout):

			start_t = time.time()
			line = f.readline()

			print(f'---------{i}----------')
			i+=1
			formated_line = line.strip()
			formated_line = formated_line.replace(':','')
			a = formated_line.split(' ')
			a.remove('')
			
			if(len(a)):
				humidity = f'{a[0]} ({place}): '
				humidity_value = a[1]
				tempC = f'{a[2]} in °C ({place}):'
				tempF = f'{a[2]} in °F ({place}):'
				tempC_value = a[3]
				tempF_value = a[4]

				data_pkt[humidity] = humidity_value
				data_pkt[tempC] = tempC_value
				data_pkt[tempF_value]= tempF_value
				
				pkt = packet("PUBLISH", data_pkt)
				# time.sleep(read_time)
				if s.publish(pkt):
					continue
				else :
					s.start()
					

				
print("Closing client")
s.client_socket.close()



f.close()