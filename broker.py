import socket
import select
import packet as p
import json
import time

TYPESIZE = 2
DATASIZE = 10
HEADERSIZE = TYPESIZE + DATASIZE

class Broker:
	def __init__(self, host = socket.gethostname() , port = 4242, listen = 10 , timeout = None):
		self.host = host
		self.port = port
		self.listen_for = listen
		self.host_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.clients = [self.host_socket]
		self.subscriptions = {}
		self.host_socket.settimeout(timeout)

	def start(self):
		print("-------- Starting Broker --------")
		self.host_socket.bind((self.host, self.port))
		self.host_socket.listen(self.listen_for)
	
	def receive_ack(self):
		try:
			ack = self.host_socket.recv(HEADERSIZE)
			if not len(ack):
				return False

			ack = ack.decode('utf-8')
			packet_type = int(ack[:TYPESIZE])
			packet_size = int(ack[TYPESIZE:HEADERSIZE])

			packet_type = p.packet.TYPES[packet_type]
			# print("pkt type = ",packet_type)

			self.host_socket.recv(packet_size)
			print(f'{packet_type} received')

		except:
			print(f'{p.packet.TYPES[packet_type]} not recived')
			return False

		return True

	def receive_packet(self,client_socket):
		try:
		# print("t",self.host_socket.gettimeout())
			print(".")
			header = client_socket.recv(HEADERSIZE)
			print("-")
			# print("header = ",header)
			if not len(header):
				return self.ping(client_socket)

			d_header = header.decode('utf-8')
			packet_type = int(d_header[:TYPESIZE])
			packet_size = int(d_header[TYPESIZE:HEADERSIZE])

			packet_type = p.packet.TYPES[packet_type]

			c = client_socket.recv(packet_size).decode('utf-8')
			data = json.loads(c)
			print(f'\nPacket received ! \ntype: {packet_type} | size: {packet_size}\ncontent: {data} \n')
			print("\n..................................................................................")
			return p.packet(packet_type, data)

		except:
			return self.ping(client_socket)

	def send_ack(self, client_socket, ack_type = '' ):

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
			client_socket.send(ack)
			print("Done!")
			return True

		except:
			print("Not sent!")
			return False

	def ping(self, client_socket):
		if not self.send_ack(client_socket, "PINGREQ"):
			print(f'Cound\'t send PINGREQ...\nClosing connetion with: {client_socket}')
			client_socket.close()
			return False

		if not self.receive_ack():
			print(f'No response to PINGREQ...\nClosing connetion with: {client_socket}')
			client_socket.close()
			return False
		return True

	def publish(self, client_socket, pkt):

		print(f'Trying to publish : {pkt.data}')
		try:
			client_socket.send(pkt.stage())
		except:
			print(f'Cound\'t PUBLISH {pkt.data} \nto: {client_socket}')
			self.ping()
		
		return self.receive_ack("PUB")

	def run(self):

		try:
			while True:
				#scan dos sockects monitorados para verificar se tem algo novo 
				read_sockets, _, exception_sockets = select.select(self.clients, [], self.clients, self.host_socket.gettimeout())
				# print("outs", exception_sockets)
				#pra cada um deles ver se

				for notified_client in read_sockets:

					#É uma nova conexão chegando
					if notified_client == self.host_socket:

						#aceitar conexão
						client_socket, client_address = self.host_socket.accept()

						#receber pacote como um objeto packet
						pkt = self.receive_packet(client_socket)
						
						#se for nulo, repetir while
						if pkt is False:
							print("pkt false?")
							continue

						#acidionar socket na lista de monitorados
						self.clients.append(client_socket)


						print(f'New {p.packet.TYPES[pkt.type]} packet from {client_address}')

						#enviar CONNACK
						self.send_ack(client_socket, "CONN")
           

					#tem um atualização do cliente monitorado
					else:
						
						#receber pacote 	
						pkt = self.receive_packet(notified_client)
						

						#se for nulo, já fechou a conexão. Agora remover da lista e retirar da llista de inscritos e repetir while
						if pkt is False:
							self.clients.remove(notified_client)
							for topic_subscribers in self.subscriptions.values():
								if notified_client in topic_subscribers:
									topic_subscribers.remove(notified_client)

							continue
						
						#traduzir para string o tipo de pacote
						packet_type = p.packet.TYPES[pkt.type]

						
						# if packet_type == 9:
						# 	print(pkt.data)

						#Se for do tipo PUBLISH


						if packet_type == "PUBLISH":

							#mandar PUBACK para o cliente
							self.send_ack(notified_client, "PUB")

							#Para cada topico,valor que chegou nesse pacote
							for key,value in pkt.data.items():

								#se esse topico existir na lista de inscritos 
								if key in self.subscriptions.keys():

									#para cada cliente inscrito nesse topico
									for client in self.subscriptions[key]:

										#Tentar encaminhar o topico de interrese desse 
										#pacote para os inscritos
										aux = p.packet("PUBLISH", {key : value})
										
										try:
											client.send(aux.stage())
										except:
											print(f'Cound\'t PUBLISH {key} : {value}\nto: {client}')

										#testar ping?

								#se não existe adicionar no dicionario de topicos e seus inscritos (lista vazia)
								else:
									self.subscriptions[key] = []

						##Se for do tipo SUBSCRIBE
						elif packet_type == "SUBSCRIBE":

							print("Received packet: ", pkt.data,end = '\n\n')
							
							#pegar lista de topicos que quer se inscrever
							subscribe_list = pkt.data["topics"] 

							#pra cada topico recebido
							for topic in subscribe_list:

								#se o topico já existe
								if topic in self.subscriptions.keys():

									#se o cliente já não estiver na lista 
									if notified_client not in self.subscriptions[topic]:

										#adicione ele na lista desse topico
										self.subscriptions[topic].append(notified_client)

								#se o topico não existe 
								else:
									#crie ele e adicione o cliente a lista
									self.subscriptions[topic] = [notified_client]
							

							for key,value in self.subscriptions.items():
								print(f'Dictionary state: {key} : {len(value)}', end ='\n')

							#mandar SUBACK confirmando inscrição
							self.send_ack(notified_client, "SUB")
						
						elif packet_type == "PINGREQ":
							self.send_ack(notified_client,"PINGRESP")

						elif packet_type == "PINGRESP":
							# self.send_ack(notified_client,"PINGRESP")
							print("ok...")

				# if len(read_sockets) == 0:
				# 	for client in self.clients:
				# 		if client != self.host_socket:
				# 			self.ping(client)



		except:
			print("AHHHHHHHH")
			for client in self.clients:
				if client != self.host_socket:
					self.ping(client)

			#Se algo deu errado ou apertou [ ^C ] fechar socket
			print(".....")
			self.host_socket.close()


def main():

	b = Broker()
	b.start()
	b.run()

if __name__ == '__main__':
    main()