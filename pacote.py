import hashlib

class info_pacote(object):
	"""
	Organiza os dados do pacote

	"""
	def __init__(self,size,code,right,data):
		self.pack_size=size
		self.encrypt_code=code
		self.right=right
		self.data=data


class pacote(object):

	def __init__(self):
		"""
		Informações inciais referentes ao pacote, sendo: 
		ep = \xf1\xf2\xf3\xf4
		bs = \x00\xf1\x00\xf2\x00\xf3\x00\xf4

		"""
		self.head_size = 14
		self.max_size = 128
		ep=4059231220
		bs=67836508785279220
		self.eop = ep.to_bytes(4,"big")
		self.bytes_stuffing=bs.to_bytes(8,"big")

		# Head variables
		self.max_pack_size = 4
		self.max_code_size = 2

	######################
	# Funções Auxiliares #
	######################

	def find_eop(self,data):
		"""
		Encontra EOP's no meio do código
		"""
		for i in range(len(data)):
			if data[i:i+4]==self.eop:
				return i

	def find_false_eop(self,data):
		"""
		Encontra EOP's tranformados no meio do código
		"""
		for i in range(len(data)):
			if data[i:i+8]==self.bytes_stuffing:
				return i

	def fix_bytes_stuffing(self,data):
		"""
		Converte de EOP's no meio do código para falsos EOP's
		"""
		while True:
			i=self.find_eop(data)
			if i!=None:
				data=data[:i]+self.bytes_stuffing+data[i+4:]
			else:
				break
		return data

	def restore_bytes_stuffing(self,data):
		"""
		Converte de falsos EOP's para EOP's no meio do código
		"""
		while True:
			i=self.find_false_eop(data)
			if i!=None:
				data=data[:i]+self.eop+data[i+8:]
			else:
				break
		return data

	def encrypt_string(self,data):
		"""
		Gera um dígito de segunaça
		"""
		hash_string=str(data)
		sha_signature = hashlib.sha256(hash_string.encode()).hexdigest()
		sha=sha_signature[:4]
		int_sha=int(sha,16)
		sha_final=int_sha.to_bytes(2,"big")
		return sha_final

	######################
	# Criação de Pacotes #
	######################

	def head(self,data):
		"""
		Head (Soma de toda informação do head)

		"""
		pack_size = len(data)
		size_bytes = pack_size.to_bytes(self.max_pack_size, "big")
		encrypt_code = self.encrypt_string(data)
		complement = bytes(self.head_size-self.max_pack_size-self.max_code_size)
		final_head = size_bytes + complement + encrypt_code
		return final_head

	def empacotar(self,data):
		"""
		1- Conserta o código caso haja um EOP no meio do código, substituindo-o por 'bs'
		2- Junta head + arquivo + EOP

		"""
		data=self.fix_bytes_stuffing(data)
		self.pack=self.head(data) + data + self.eop
		return self.pack

	######################
	# Leitura de Pacotes #
	######################

	def read_head(self,data):
		"""
		Lê os arquivos correspondentes ao head, 
		por meio de splits de posições estratégicas

		"""
		size_bytes = int.from_bytes(data[:self.max_pack_size], "big")
		encrypt = data[self.head_size-self.max_code_size:]
		return size_bytes, encrypt

	def ler_pacotes(self,pacote):
		"""
		1- Procura por EOP's no código
		2- Procura por falsos EOP's sinalizados no código e os converte em código normal
		3- Vê se a encriptografia está correta
		4- Retorna um info_pacote

		"""
		size_bytes, encrypt = self.read_head(pacote[:self.head_size])
		eop_i = self.find_eop(pacote)
		data = self.restore_bytes_stuffing(pacote[self.head_size:eop_i])
		right = (encrypt==encrypt_string(data))
		info_packs = info_pacote(size_bytes,encrypt,right,data)
		return info_packs