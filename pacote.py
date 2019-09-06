import hashlib

def encrypt_string(data):
	hash_string=str(data)
	sha_signature = hashlib.sha256(hash_string.encode()).hexdigest()
	sha=sha_signature[:4]
	int_sha=int(sha,16)
	sha_final=int_sha.to_bytes(2,"big")
	return sha_final

class info_pacote(object):
	def __init__(self,size,file_size,code,right,data,overhead):
		self.pack_size=size
		self.file_size=file_size
		self.encrypt_code=code
		self.right=right
		self.data=data
		self.overhead=overhead


class info_all_packs(object):
	def __init__(self):
		self.total_packs=0
		self.packs={}
		self.last_pack=0
		
	def insert_pack(self,pacot):
		pack=pacote()
		info_packs,total_packs,this_pack=pack.ler_pacotes(pacot)

		if (not self.packs) and (this_pack==1) and info_packs.right:
			self.last_pack+=1
			self.total_packs=total_packs
			self.packs[this_pack]=info_packs
			return True

		elif (this_pack==self.last_pack+1) and info_packs.right and (total_packs==self.total_packs) and (self.last_pack<self.total_packs):
			self.packs[this_pack]=info_packs
			self.last_pack+=1
		else:
			pass

	def full_data(self):
		if self.last_pack==self.total_packs:
			dat=b''
			for i in self.packs:
				dat+=self.packs[i].data
			return dat
		else:
			pass


class pacote(object):
	def __init__(self):
		self.head_size = 14
		self.eop_size=4
		self.max_size = 128
		ep=4059231220
		bs=67836508785279220
		self.eop = ep.to_bytes(4,"big")
		self.bytes_stuffing=bs.to_bytes(8,"big")
		self.payload=128

		self.max_pack_size = 1
		self.max_code_size = 2
		self.max_total_packs_size=2
		self.this_pack_number_size=2

	def recebedor(self,com):
		lenRead = self.pack_size + self.max_code_size
		rxBuffer, nRx = com.getData(lenRead)
		txlen = int.from_bytes(rxBuffer,"big")
		rxBuffer2, nRx2 = com.getData(txlen)
  
  		return(rxBuffer + rxBuffer2)

	def find_eop(self,data):
		for i in range(len(data)):
			if data[i:i+4]==self.eop:
				return i

	def find_false_eop(self,data):
		for i in range(len(data)):
			if data[i:i+8]==self.bytes_stuffing:
				return i

	def fix_bytes_stuffing(self,data):
		while True:
			i=self.find_eop(data)
			if i!=None:
				data=data[:i]+self.bytes_stuffing+data[i+4:]
			else:
				break
		return data

	def restore_bytes_stuffing(self,data):
		while True:
			i=self.find_false_eop(data)
			if i!=None:
				data=data[:i]+self.eop+data[i+8:]
			else:
				break
		return data


	def head(self,data,total_packs,indice):
		pack_size=(self.head_size - self.max_pack_size)+len(data)+self.eop_size
		encrypt_code=encrypt_string(data)
		size_bytes = pack_size.to_bytes(self.max_pack_size, "big")
		total_packs =total_packs.to_bytes(self.max_total_packs_size,"big")
		indice = indice.to_bytes(self.this_pack_number_size,"big")
		complement = bytes(self.head_size-self.max_pack_size-self.max_code_size-self.max_total_packs_size-self.this_pack_number_size)
		final_head=size_bytes+total_packs+indice+complement+encrypt_code

		return final_head

	def read_head(self,data):
		size_bytes = int.from_bytes(data[:self.max_pack_size], "big")+self.max_pack_size
		total_packs = int.from_bytes(data[self.max_pack_size:self.max_pack_size+self.max_total_packs_size], "big")
		this_pack = int.from_bytes(data[self.max_pack_size+self.max_total_packs_size:self.max_pack_size+self.max_total_packs_size+self.this_pack_number_size], "big")
		encrypt = data[self.head_size-self.max_code_size:]

		return size_bytes,encrypt,total_packs,this_pack


	def empacotar(self,data,total_packs,indice):
		data=self.fix_bytes_stuffing(data)
		self.pack=self.head(data,total_packs,indice)+data+self.eop

		return self.pack

	def ler_pacotes(self,pacote):
		size_bytes, encrypt, total_packs, this_pack= self.read_head(pacote[:self.head_size])
		eop_i=self.find_eop(pacote)
		data=pacote[self.head_size:eop_i]
		original=self.restore_bytes_stuffing(data)
		size_file=len(original)
		right = (encrypt==encrypt_string(data))
		overhead = (size_bytes-self.eop_size-self.head_size+self.max_pack_size)/(size_bytes+self.max_pack_size)
		info_packs=info_pacote(size_bytes,size_file,encrypt,right,original,overhead)

		return info_packs, total_packs, this_pack

	def full_empacotacao(self,data):
		li=[]
		total_packs=(len(data)//self.payload)+1

		for i in range(0,total_packs):
			indice=i+1
			unit_data=data[i*self.payload:(i+1)*self.payload]
			li.append(self.empacotar(unit_data,total_packs,indice))
			
		return li