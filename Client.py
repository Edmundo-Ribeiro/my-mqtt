import socket
import time
import packet as p
import json
import random

TYPESIZE = 2
DATASIZE = 10
HEADERSIZE = TYPESIZE + DATASIZE

class client:
	def __init__(self, host = socket.gethostname() , port = 4242, subscribe_to = [] , timeout = None):
		self.host = host
		self.port = port
		self.subs = subscribe_to
		self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.client_socket.settimeout(timeout)
	
	def start(self):
		try:
			print("Connecting...", end = ' ')
			self.client_socket.connect((self.host, self.port))
			print("Done")

			connect = p.packet("CONNECT").stage()
			print("Sending connect packet => ", connect)
			self.client_socket.send(connect)

		except:
			print("Unable to connect")
			return False
		


		return self.receive_ack()
	
	def receive_ack(self):
		try:
			ack = self.client_socket.recv(HEADERSIZE)
			if not len(ack):
				return False

			ack = ack.decode('utf-8')
			packet_type = int(ack[:TYPESIZE])
			packet_size = int(ack[TYPESIZE:HEADERSIZE])

			packet_type = p.packet.TYPES[packet_type]
			# print("pkt type = ",packet_type)

			self.client_socket.recv(packet_size)
			print(f'{packet_type} received')

		except:
			print(f'{p.packet.TYPES[packet_type]} not recived')
			return False

		return True

	def receive_packet(self):
		try:
			header = self.client_socket.recv(HEADERSIZE)
			# print("header = ",header)
			if not len(header):
				return self.ping()

			d_header = header.decode('utf-8')
			packet_type = int(d_header[:TYPESIZE])
			packet_size = int(d_header[TYPESIZE:HEADERSIZE])

			packet_type = p.packet.TYPES[packet_type]

			c = self.client_socket.recv(packet_size).decode('utf-8')
			data = json.loads(c)
			print(f'\nPacket received!\ntype: {packet_type} | size: {packet_size}\ncontent: {data} \n')
			return p.packet(packet_type, data)

		except:
			return self.ping()

	def subscribe(self):
		subs = p.packet("SUBSCRIBE",{"topics": self.subs})
		print(f'Trying to subscribe to : {subs.data["topics"]}')
		self.client_socket.send(subs.stage())
		
		return self.receive_ack()

	def publish(self, pkt):

		print(f'Trying to publish : {pkt.data}')
		try:
			self.client_socket.send(pkt.stage())
		except:
			print(f'Cound\'t PUBLISH {pkt.data} \nto: {self.client_socket}')

		
		return self.receive_ack()

	def ping(self):
		self.send_ack("PINGREQ")
		if not self.receive_ack():
			print(f'No response to PINGREQ...\nClosing connetion with: {self.client_socket}')
			self.client_socket.close()
			return False
		return True

	def send_ack(self, ack_type = '' ):

		if ack_type == "PINGREQ":
			print(f'Sending {ack_type}...', end = ' ')
			ack = p.packet(ack_type).stage()
		
		elif ack_type == "PINGRESP":
			print(f'Sending {ack_type}...', end = ' ')
			ack = p.packet(ack_type).stage()
		
		else:
			print(f'Sending {ack_type}ACK...', end = ' ')
			ack = p.packet(f'{ack_type}ACK').stage()
			

		try:
			self.client_socket.send(ack)
			print("Done!")
			return True

		except:
			print("Not sent!")
			return False


def main():
	if input("[s] for sensor [c] for client\nmode:") == 'c':

		c = client(subscribe_to = ["temperatura c", "temperatura f", "umidade"])
		
		if c.start():
			
			if c.subscribe():
				
				while True:
					pkt = c.receive_packet()
					packet_type = p.packet.TYPES[pkt.type]
					if packet_type == "PUBLISH":
						#mandar PUBACK para o cliente
						self.send_ack(notified_client, "PUB")

					elif packet_type == "PINGREQ" :
						self.send_ack("PINGRESP")
					print(".................................................................")	
				
				
					
	else:
		s = client(timeout = 5)
		
		if s.start():
			flag = True 
			while flag:
				sensor_data = random.random()
				pkt = p.packet("PUBLISH", {"temperatura c":sensor_data})
				flag = s.publish(pkt)
				time.sleep(4)
			print("Closing client")
			s.client_socket.close()
				


if __name__ == '__main__':
    main()