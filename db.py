import os
import json
import sqlite3

import bcrypt

from constants import *

class MasterManip(object):
	def __init__(self):
		if not os.path.exists(DB_FOLDER):
			os.mkdir(DB_FOLDER)

	def verify_key(self, master_key):
		salt = bcrypt.gensalt()
		master_hash = bcrypt.hashpw(master_key, salt)

		try:
			with open(f"{DB_FOLDER}/{DB_MASTER}", "r") as f:
				master_data = json.load(f)
				master_hash = master_data["hash"]

			if bcrypt.checkpw(master_key, master_hash.encode()):
				return True
			return False
		except Exception:
			return False

	def write_key(self, master_key):
		salt = bcrypt.gensalt()
		master_hash = bcrypt.hashpw(master_key, salt)
		master_data = {"hash": master_hash.decode()}

		with open(f"{DB_FOLDER}/{DB_MASTER}", "w") as f:
			json.dump(master_data, f, indent=4)

	def master_exists(self):
		if os.path.exists(f"{DB_FOLDER}/{DB_MASTER}"):
			return True
		return False

class DbManip(object):
	def __init__(self):
		if not os.path.exists(f"{DB_FOLDER}/{DB_STORAGE}"):
			open(f"{DB_FOLDER}/{DB_STORAGE}", "a").close()
		self.connection = sqlite3.connect(f"{DB_FOLDER}/{DB_STORAGE}")
		self.cursor = self.connection.cursor()

	def create_storage(self):
		self.cursor.execute("create table if not exists storage(title TEXT, username TEXT, password TEXT, url TEXT)")
		self.connection.commit()

	def encrypt_storage(self, key):
		pass

	def decrypt_storage(self, key):
		pass

	def entry_exists(self, filter_by, value):
		assert filter_by in ["Title", "URL", "Username"]
		self.cursor.execute(f"select * from storage WHERE {filter_by}=?", (value,))
		found = self.cursor.fetchall()

		if found:
			return True
		return False

	def add(self, **kwargs):
		columns = ", ".join(kwargs.keys())
		placeholders = ", ".join(["?"] * len(kwargs))
		query = f"insert into storage ({columns}) values ({placeholders})"
		self.cursor.execute(query, tuple(kwargs.values()))
		self.connection.commit()

	def delete(self):
		pass

	def close(self):
		self.cursor.close()
		self.connection.close()