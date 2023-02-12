import os
import struct
import sqlite3

from Crypto.Cipher import AES

from constants import *

class DbManip(object):
	def __init__(self, master_key):
		if not os.path.exists(f"{DB_FOLDER}/{DB_STORAGE}"):
			open(f"{DB_FOLDER}/{DB_STORAGE}", "w").close()

		self.connection = sqlite3.connect(f"{DB_FOLDER}/{DB_STORAGE}")
		self.cursor = self.connection.cursor()
		self._master_key = master_key
		self._file = f"{DB_FOLDER}/{DB_STORAGE}"

	def create_storage(self):
		self.cursor.execute("create table if not exists storage(title TEXT, username TEXT, password TEXT, url TEXT)")
		self.connection.commit()

	def encrypt(self, chunk_size=64*1024):
		output_file = self._file + ".enc"
		iv = os.urandom(16)
		encryptor = AES.new(self._master_key, AES.MODE_CBC, iv)
		file_size = os.path.getsize(self._file)

		with open(self._file, "rb") as inp:
			with open(output_file, "wb") as out:
				out.write(struct.pack("<Q", file_size))
				out.write(iv)

				while True:
					chunk = inp.read(chunk_size)
					if not chunk:
						break
					elif len(chunk) % 16 != 0:
						chunk += b" " * (16 - len(chunk) % 16)
					out.write(encryptor.encrypt(chunk))
		os.remove(self._file)

	def decrypt(self, chunk_size=64*1024):
		encrypted_file = f"{self._file}.enc"
		with open(encrypted_file, "rb") as inp:
			size = struct.unpack("<Q", inp.read(struct.calcsize("Q")))[0]
			iv = inp.read(16)
			decryptor = AES.new(self._master_key, AES.MODE_CBC, iv)

			with open(self._file, "wb") as out:
				while True:
					chunk = inp.read(chunk_size)
					if not chunk:
						break
					out.write(decryptor.decrypt(chunk))
				out.truncate(size)
		os.remove(self._file + ".enc")

	def table_exists(self):
		self.cursor.execute("select name from sqlite_master where type='table' and name='storage'")
		result = self.cursor.fetchall()

		if result:
			return True
		else:
			return False

	def entry_exists(self, filter_by, value):
		if filter_by not in ["Title", "URL", "Username"]:
			return (False, [])

		try:
			self.cursor.execute(f"select * from storage WHERE {filter_by}=?", (value,))
			result = self.cursor.fetchall()
		except sqlite3.OperationalError:
			return (False, [])

		if result:
			return (True, result)
		else:
			return (False, [])

	def add(self, **kwargs):
		columns = ", ".join(kwargs.keys())
		placeholders = ", ".join(["?"] * len(kwargs))
		query = f"insert into storage ({columns}) values ({placeholders})"
		self.cursor.execute(query, tuple(kwargs.values()))
		self.connection.commit()

	def delete(self, **kwargs):
		pass

	def close(self):
		self.cursor.close()
		self.connection.close()