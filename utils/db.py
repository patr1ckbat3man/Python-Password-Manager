import os
import sys
import sqlite3
import getpass

import pyperclip
import bcrypt

from .constants import *

class DatabaseHandler:
	def __init__(self, obj):
		self.encryptor = obj

		self.connection = None
		self.cursor = None

	def update_database(func):
		def wrapper(self, *args, **kwargs):
			if os.path.isfile(f"{STORAGE_DB}.aes"):
				self.encryptor.decrypt()

			result = func(self, *args, **kwargs)

			if os.path.isfile(STORAGE_DB):
				self.encryptor.encrypt()

			return result
		return wrapper

	def handle_key(self, key=None, **kwargs):
		"""Execute key operation based on parameters.

		Parameters
		----------
		key : utf-8 encoded string
			Master key of user.

		**kwargs : dict
			Optional keyword arguments specifying the key operation to execute.

		Returns
		-------
		bool
			Boolean indicating whether the operation was succesful.
		"""
		salt = bcrypt.gensalt()

		try:
			self.connection = sqlite3.connect(MASTER_DB)
			self.cursor = self.connection.cursor()

			if kwargs.get("write"):
				key_hash = bcrypt.hashpw(key.encode(), salt)
				self.cursor.execute("create table if not exists user(hash BLOB NOT NULL);")
				self.cursor.execute("insert into user (hash) values (?);", (key_hash,))
				self.connection.commit()
				return True
			elif kwargs.get("verify"):
				key_hash = self.cursor.execute("select hash from user;").fetchone()[0]
				if bcrypt.checkpw(key.encode(), key_hash):
					return True
				else:
					return False
			elif kwargs.get("change"):
				new_key_hash = bcrypt.hashpw(key.encode(), salt)
				self.cursor.execute("update user set hash=?;", (new_key_hash,))
				self.connection.commit()
				return True
			else:
				raise ValueError("Wrong key operation!")
		except sqlite3.Error:
			print(f"Error ocurred while handling the master key.")
			return False
		finally:
			self._close_connections()

	@update_database
	def display_entry(self):
		"""Display filtered entries.
		"""
		column, value = self.prompt_filter()
		entries = self.fetch_entries(column, value)
		processed_entries = self.process_entries(entries, "copy data from")

		if processed_entries:
			for entry in processed_entries:
				if isinstance(entry, tuple):
					entry_id = entry[0]
					data = input("Which data would you like to copy? (title / username / password / url)\n> ").strip().lower()
				if data not in ["title", "username", "password", "url"]:
					print("Wrong choice.")
					return
				elif data == "title":
					pyperclip.copy(entry[1])
				elif data == "username":
					pyperclip.copy(entry[2])
				elif data == "password":
					pyperclip.copy(entry[3])
				elif data == "url":
					pyperclip.copy(entry[4])

	@update_database
	def handle_database(self, **kwargs):
		"""Execute database operation based on parameters.

		Parameters
		----------
		**kwargs : dict
			Optional keyword arguments specifying the key operation to execute.

		Returns
		-------
		None	
		"""
		try:
			self.connection = sqlite3.connect(STORAGE_DB)
			self.cursor = self.connection.cursor()

			if kwargs.get("add"):
				if not os.path.exists(STORAGE_DB):
					open(STORAGE_DB, "a").close()

				ttl, usr, psw, url = self.prompt_data()

				self.cursor.execute("create table if not exists storage(id INTEGER PRIMARY KEY, title TEXT, username TEXT, password TEXT, url TEXT);")
				self.cursor.execute("insert into storage (title, username, password, url) values (?, ?, ?, ?);", (ttl, usr, psw, url))
				self.connection.commit()
				print("Entry succesfully added.")
			elif kwargs.get("update"):
				column, value = self.prompt_filter()
				entries = self.fetch_entries(column, value)
				processed_entries = self.process_entries(entries, "update")

				if processed_entries:
					for entry in processed_entries:
						if isinstance(entry, tuple):
							entry_id = entry[0]
							print(f"Updating values for: {entry}")
							ttl, usr, psw, url = self.prompt_data()
							self.cursor.execute("update storage set title=?, username=?, password=?, url=? where id=?;", (ttl, usr, psw, url, entry_id,))
					self.connection.commit()
					print(f"Updated {len(processed_entries)} entry/entries.")
			elif kwargs.get("delete"):
				column, value = self.prompt_filter()
				entries = self.fetch_entries(column, value)
				processed_entries = self.process_entries(entries, "delete")

				if processed_entries:
					for entry in processed_entries:
						if isinstance(entry, tuple):
							entry_id = entry[0]
							self.cursor.execute("delete from storage where id=?", (entry_id,))
					self.connection.commit()
					print(f"Deleted {len(processed_entries)} entry/entries.")
			else:
				raise ValueError("Wrong database operation!")
		except sqlite3.Error as e:
			print(e)
		finally:
			self._close_connections()

	@update_database
	def table_empty(self, table_name):
		"""Check for the table existence in the database.

		Parameters
		----------
		table_name : string
			Name of database table.

		Returns
		-------
		bool
			Boolean indicating whether the table exists.
		"""
		try:
			self.connection = sqlite3.connect(STORAGE_DB)
			self.cursor = self.connection.cursor()
			self.cursor.execute(f"select name from sqlite_master where type='table' and name='{table_name}';")
			table_exists = self.cursor.fetchall()
			self.cursor.execute("select count(*) from storage;")
			row_count = self.cursor.fetchall()
			if not table_exists:
				if row_count[0][0] == 0:
					print("No data to query! Add some entries first.")
					return True
				else:
					return False
			else:
				return False
		except sqlite3.Error as e:
			print(e)
			return False

	@update_database
	def fetch_entries(self, filter_by, value):
		"""Fetch all entries if they exist.

		Parameters
		----------
		filter_by : string
			Name of column which is gonna be filtered.

		value : string
			Value to be searched for in filtered column.

		Returns
		-------
		result : tuple
			Tuple of filtered row/rows, if some entries are found.
		bool
			False, if the entry doesn't exist.
		"""
		try:
			self.connection = sqlite3.connect(STORAGE_DB)
			self.cursor = self.connection.cursor()
			self.cursor.execute(f"select * from storage where {filter_by}=?", (value,))
			result = self.cursor.fetchall()
			if result:
				return result
			else:
				return False
		except sqlite3.Error as e:
			print(e)

	def process_entries(self, entries, operation):
		"""Process fetched entries.

		Parameters
		----------
		entries : list
			List of fetched entries.
		operation : string
			Operation chosen by user.

		Returns
		-------
		entries : tuple
			Tuple containing arrays for each processed entry.		
		"""
		if not entries:
			print("No entries found.")
			return

		print("------------------------------------------------------------")
		print(f"Found {len(entries)} matching entry/entries:")
		print("<choice> - (ID, Title, Username, Password, URL)")
		for idx, entry in enumerate(entries):
			print(f"{idx+1} - {entry}")
		print("------------------------------------------------------------")

		if len(entries) == 1:
			choice = input(f"Select an entry to {operation}:\n> ")
			index = int(choice) - 1
			return [entries[index]]
		else:
			choice = self.prompt_entry(operation, len(entries))
			if choice == "all":
				return entries
			else:
				try:
					index = int(choice) - 1
					if index >= 0 and index < len(entries):
						return [entries[index]]
					else:
						print("Invalid choice!")
				except ValueError:
					print("Wrong data input!")

	def prompt_data(self):
		"""Display choices of data to be entered into entry.

		Parameters
		----------
		None

		Returns
		-------
		title : str
		username : str
		password : str
		url : str
		"""
		title = str(input("Title: (Mandatory)\n> "))
		if not title:
			print("Title has to be filled in.")
			self.prompt_data()
		username = str(input("Username: (If none, leave empty)\n> "))
		password = getpass.getpass("Password: (Mandatory)\n> ")
		if not password:
			print("Password field has to be filled in.")
			self.prompt_data()
		url = str(input("URL: (If none, leave empty)\n> "))
		return title, username, password, url

	def prompt_filter(self):
		"""Display choices for filters.

		Parameters
		----------
		None

		Returns
		-------
		column_filter : str
			Name of column which is gonna be filtered.
		value : str
			Value to be searched for in filtered column.
		"""
		filter_options = {
			"t": "title",
			"u": "username",
			"r": "url"
		}

		column = input("Filter by (t=Title / u=Username / r=URL):\n> ").strip().lower()
		if column not in filter_options:
			print("Wrong filter specified! Try again.")
			return self.prompt_filter()

		column_filter = filter_options[column]
		value = input(f"Value to search for in {column_filter} column:\n> ").strip().lower()

		return column_filter, value

	def prompt_entry(self, operation, num_entries):
		"""Get user input based on operation.

		Parameters
		----------
		operation : string
			Operation chosen by user.
		num_entries : int
			Number of fetched entries.

		Returns
		-------
		choice : string
			User choice for operation.
		"""
		if operation == "copy data from":
			prompt = f"Select an entry to {operation} (1-{num_entries})\n> "
		else:
			prompt = f"Select an entry to {operation} (1-{num_entries}), or 'all':\n> "
			
		choice = input(prompt)
		return choice

	def _close_connections(self):
		"""Close all database connections.
		"""
		if self.connection:
			self.cursor.close()
			self.connection.close()
			self.cursor = None
			self.connection = None

	def close_database(self):
		"""Check whether the file is encrypted and all connections are closed before exiting.
		"""
		self._close_connections()

		if os.path.isfile(STORAGE_DB):
			self.encryptor.encrypt()
			os.remove(STORAGE_DB)

		print("Terminating script...")
		sys.exit()