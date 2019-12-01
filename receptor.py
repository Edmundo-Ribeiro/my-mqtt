from packet import packet
from client import client
import time
import socket

import json

TYPESIZE = 2
DATASIZE = 10
HEADERSIZE = TYPESIZE + DATASIZE



tp = 'log.txt'#input("Informe o Arquivo com dados do sensor: ").strip()
place = 'sala'#input("Informe o comodo onde esta o sensor: ").strip()
read_time = 10#float(input("Informe o intervalo de leitura do sensor: ").strip())
delay = 5#float(input("Informe o timeout do sensor: ").strip())

print(f_name,place,read_time,delay)



c = client(subscribe_to = tp, timeout = delay)

if c.start():
	if c.subscribe():
		start_t = time.time()
		while True:
			if( time.time() - start_t >= s.timeout):

				start_t = time.time()

				pkt = c.receive_packet()
				
				packet_type = p.packet.TYPES[pkt.type]
				
				if packet_type == "PUBLISH":
					#mandar PUBACK para o cliente
					c.send_ack("PUB")

				elif packet_type == "PINGREQ" :
					c.send_ack("PINGRESP")
				print(".................................................................")	
				
						

					
print("Closing client")
s.client_socket.close()

