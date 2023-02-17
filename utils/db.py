import os
import sqlite3

import bcrypt

from .constants import *

class DbManip:
	def __init__(self):
		self.connection = None
		self.cursor = None

	def write_key(self, key):
		"""Write master key to database.

		Parameters
		----------
		key : utf-8 encoded string
			Master key of user.

		Returns
		-------
		bool
			boolean indicating whether the key was sucesfully written.
		"""
		salt = bcrypt.gensalt()
		key_hash = bcrypt.hashpw(key.encode(), salt)

		try:
			self.connection = sqlite3.connect(STORAGE_MASTER)
			self.cursor = self.connection.cursor()
			self.cursor.execute("create table if not exists master(hash BLOB NOT NULL);")
			query = "insert into master (hash) VALUES (?);"
			data = (key_hash,)
			self.cursor.execute(query, data)
			self.connection.commit()
			self.cursor.close()
			return True
		except sqlite3.Error:
			return False
		finally:
			self.close_connections()

	def verify_key(self, key):
		"""Verify entered master key.

		Parameters
		----------
		key : utf-8 encoded string
			Master key of user.

		Returns
		-------
		bool
			boolean indicating wheter the entered master key is valid.
		"""
		salt = bcrypt.gensalt()

		try:
			self.connection = sqlite3.connect(STORAGE_MASTER)
			self.cursor = self.connection.cursor()
			query = "select hash from master;"
			key_hash = self.cursor.execute(query).fetchone()[0]
			self.cursor.close()
			if bcrypt.checkpw(key.encode(), key_hash):
				return True
			else:
				return False
		except sqlite3.Error:
			return False
		finally:
			self.close_connections()

	def change_key(self, new_key):
		"""Change the current master key.

		Parameters
		----------
		new_key : utf-8 encoded string
			Master key of user.

		Returns
		-------
		bool
			boolean indicating wheter the key was changed.
		"""
		salt = bcrypt.gensalt()
		key_hash = bcrypt.hashpw(new_key.encode(), salt)

		try:
			self.connection = sqlite3.connect(STORAGE_MASTER)
			self.cursor = self.connection.cursor()
			query = "update master set hash = ?;"
			self.cursor.execute(query, (key_hash,))
			self.connection.commit()
			self.cursor.close()
			return True
		except sqlite3.error:
			return False
		finally:
			self.close_connections()

	def table_exists(self, table_name):
		try:
			self.connection(STORAGE_DB)
			self.cursor = self.connection.cursor()
			query = "select name from sqlite_master where type='table' and name = ?;"
			self.cursor.execute(query, (table_name,))
			result = self.cursor.fetchall()
			if result:
				return True
			else:
				return False
		except sqlite3.Error:
			return False
		finally:
			self.close_connections()

	def entry_exists(self, filter_by, value):
		try:
			query = f"select * storage where {filter_by} = ?"
			self.cursor.execute(query, (value,))
			result = self.cursor.fetchall()
		except sqlite3.OperationalError:
			return (False, [])

		if result:
			return (True, result)
		else:
			return (False, [])

	def add_entry(self, **kwargs):
		columns = ", ".join(kwargs.keys())
		placeholders = ", ".join(["?"] * len(kwargs))
		query = f"insert into storage ({columns}) values ({placeholders});"

		try:
			self.connection = sqlite3.connect(STORAGE_DB)
			self.cursor = self.connection.cursor()
			self.cursor.execute("create table if not exists storage(title TEXT NOT NULL, username TEXT, password TEXT NOT NULL, url TEXT);")
			self.cursor.execute(query, tuple(kwargs.values()))
			self.connection.commit()
			return True
		except sqlite3.Error:
			return False
		finally:
			self.close_connections()

	def search_entry(self, filter_by):
		pass

	def update_entry(self, filter_by):
		pass

	def delete_entry(self, filter_by):
		pass

	def close_connections(self):
		if self.connection:
			self.cursor.close()
			self.connection.close()
			self.cursor = None
			self.connection = None