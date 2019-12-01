import json
TYPESIZE = 2
DATASIZE = 10
HEADERSIZE = TYPESIZE + DATASIZE


class packet:
	TYPES = {
	"CONNECT" : 1,
	1 : "CONNECT", 
	"CONNACK" : 2,
	2 : "CONNACK",
	"PUBLISH" : 3,
	3 : "PUBLISH",
	"PUBACK" : 4,
	4 : "PUBACK",
	"SUBSCRIBE" : 8,
	8 : "SUBSCRIBE",
	"SUBACK" : 9,
	9 : "SUBACK",
	"UNSUBSCRIBE" : 10,
	10 : "UNSUBSCRIBE",
	"UNSUBACK" : 11,
	11 : "UNSUBACK",
	"PINGREQ" : 12,
	12 : "PINGREQ",
	"PINGRESP" : 13,
	13 : "PINGRESP",
	"DISCONNECT" : 14,
	14 : "DISCONNECT"
	}


	def __init__(self, pkt_type, data = {}):
		if isinstance(pkt_type, str): 
			self.type =  packet.TYPES[pkt_type]
		else:
			self.type = pkt_type

		self.size = 0
		self.data = data
	# def __init__(self, header):
	# 	d_header = header.decode('utf-8')
	# 	self.type = int(d_header[:TYPESIZE])
	# 	self.size = int(d_header[TYPESIZE:HEADERSIZE])
			

	def stage(self):
		parsed_data = json.dumps(self.data)
		self.size += len(parsed_data)
		self.coded_data = bytes( f'{self.type:<{TYPESIZE}}' + 
						   f'{self.size:<{DATASIZE}}'+
						   parsed_data
						, 'utf-8')
		return self.coded_data

