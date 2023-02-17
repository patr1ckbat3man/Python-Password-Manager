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
			self.cursor.execute("insert into master (hash) values (?);", (key_hash,))
			self.connection.commit()
			self.cursor.close()
			return True
		except sqlite3.Error:
			print("Error occurred while writing master key to database.")
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
			key_hash = self.cursor.execute("select hash from master;").fetchone()[0]
			self.cursor.close()
			if bcrypt.checkpw(key.encode(), key_hash):
				return True
			else:
				print("Error veryfing master key. Database might be corrupted or password is incorrect.")
				return False
		except sqlite3.Error:
			print("Error occurred while veryfing master key.")
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
			self.cursor.execute("update master set hash = ?;", (key_hash,))
			self.connection.commit()
			self.cursor.close()
			return True
		except sqlite3.error:
			return False
		finally:
			self.close_connections()

	def table_exists(self, table_name):
		"""Check if table exists.

		Parameters
		----------
		table_name : string
			Name of database table.

		Returns
		-------
		bool
			boolean indicating whether the table exists.
		"""
		try:
			self.connection = sqlite3.connect(STORAGE_DB)
			self.cursor = self.connection.cursor()
			self.cursor.execute("select name from sqlite_master where type='table' and name = ?;", (table_name,))
			result = self.cursor.fetchall()
			if result:
				return True
			else:
				print("No data to query for. Add some entries first.")
				return False
		except sqlite3.Error:
			return False
		finally:
			self.close_connections()

	def entry_exists(self, filter_by, value):
		"""Check if entry exists.

		Parameters
		----------
		filter_by : string
			Name of column which is gonna be filtered.

		value : string
			Value to be searched for in filtered column.

		Returns
		-------
			Tuple of filtered rows, if some entries are found.
			False, if the entry doesn't exist.
		"""
		try:
			self.connection = sqlite3.connect(STORAGE_DB)
			self.cursor = self.connection.cursor()
			self.cursor.execute(f"select * from storage where {filter_by} = ?", (value,))
			result = self.cursor.fetchall()
			if result:
				return result
		except sqlite3.Error:
			return False
		finally:
			self.close_connections()

	def add_entry(self, **kwargs):
		"""Add entry to database.

		Parameters
		----------
		**kwargs : dict
			Data entered by the user

			- title : str
			- username : str
			- password : str
			- url : str

		Returns
		-------
		bool
			boolean indicating whether the entry was succesfully added.
		"""
		if not os.path.exists(STORAGE_DB):
			open(STORAGE_DB, "a").close()

		columns = ", ".join(kwargs.keys())
		placeholders = ", ".join(["?"] * len(kwargs))

		try:
			self.connection = sqlite3.connect(STORAGE_DB)
			self.cursor = self.connection.cursor()
			self.cursor.execute("create table if not exists storage(title TEXT NOT NULL, username TEXT, password TEXT NOT NULL, url TEXT);")
			self.cursor.execute(f"insert into storage ({columns}) values ({placeholders});", tuple(kwargs.values()))
			self.connection.commit()
			return True
		except sqlite3.Error:
			print("Error while adding entry.")
			return False
		finally:
			self.close_connections()

	def search_entry(self, filter_by, value):
		"""

		Parameters
		----------

		Returns
		-------
		"""
		result = self.entry_exists(filter_by, value)
		print(result)

	def update_entry(self):
		"""

		Parameters
		----------

		Returns
		-------
		"""
		pass

	def delete_entry(self):
		"""

		Parameters
		----------

		Returns
		-------
		"""
		pass

	def close_connections(self):
		"""Close all database connections.

		Parameters
		----------
		None

		Returns
		-------
		None
		"""
		if self.connection:
			self.cursor.close()
			self.connection.close()
			self.cursor = None
			self.connection = None