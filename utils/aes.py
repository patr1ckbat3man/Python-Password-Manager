import os
import struct
import hashlib

from Crypto.Cipher import AES

from .constants import *

class AESCipher:
	def __init__(self):
		self._key = None
		self.chunk_size = 64 * 1024
		self.file = STORAGE_DB

	@property
	def key(self):
		return self._key

	@key.setter
	def key(self, master_key):
		self._key = hashlib.sha256(master_key.encode()).digest()

	def encrypt(self):
		iv = os.urandom(16)
		encryptor = AES.new(self._key, AES.MODE_CBC, iv)
		file_size = os.path.getsize(self.file)

		with open(self.file, "rb") as inp:
			with open(f"{self.file}.enc", "wb") as out:
				out.write(struct.pack("<Q", file_size))
				out.write(iv)

				while True:
					chunk = inp.read(self.chunk_size)
					if not chunk:
						break
					elif len(chunk) % 16 != 0:
						chunk += b" " * (16 - len(chunk) % 16)
					out.write(encryptor.encrypt(chunk))
		os.remove(self.file)

	def decrypt(self):
		with open(f"{self.file}.enc", "rb") as inp:
			size = struct.unpack("<Q", inp.read(struct.calcsize("Q")))[0]
			iv = inp.read(16)
			decryptor = AES.new(self._key, AES.MODE_CBC, iv)

			with open(self._file, "wb") as out:
				while True:
					chunk = inp.read(self.chunk_size)
					if not chunk:
						break
					out.write(decryptor.decrypt(chunk))
				out.truncate(size)
		os.remove(f"{self.file}.enc")
