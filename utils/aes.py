import os

import pyAesCrypt

from .constants import *

class AESCipher:
	def __init__(self):
		self._key = None
		self.buff = 64 * 1024

	@property
	def key(self):
		return self._key

	@key.setter
	def key(self, master_key):
		self._key = master_key

	def encrypt(self):
		try:
			if os.path.isfile(STORAGE_DB):
				with open(STORAGE_DB, "rb") as inp:
					if not os.path.isfile(f"{STORAGE_DB}.aes"):
						mode = "wb"
					else:
						mode = "ab"
					with open(f"{STORAGE_DB}.aes", mode) as out:
						pyAesCrypt.encryptStream(inp, out, self._key, self.buff)
				os.remove(STORAGE_DB)
		except Exception as e:
			print(e)


	def decrypt(self):
		if os.path.isfile(f"{STORAGE_DB}.aes"):
			file_size = os.stat(f"{STORAGE_DB}.aes").st_size
		else:
			file_size = 0

		try:
			if os.path.isfile(f"{STORAGE_DB}.aes"):
				with open(f"{STORAGE_DB}.aes", "rb") as inp:
					with open(STORAGE_DB, "ab") as out:
						pyAesCrypt.decryptStream(inp, out, self._key, self.buff, file_size)
				os.remove(f"{STORAGE_DB}.aes")
		except Exception as e:
			print(e)
