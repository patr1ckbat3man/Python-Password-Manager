import os
import sys
import sqlite3

import pyperclip
import bcrypt

from .prompts import *
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
		key : utf-8 encoded str
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
		column, value = get_filter()
		entries = self.fetch_entries(column, value)
		if not entries:
			print("No entries found!")
			return
		processed_entries = self.process_entries(entries, "copy data from")

		if processed_entries:
			for entry in processed_entries:
				if not isinstance(entry, tuple):
					continue

				_, title, username, password, url = entry

				while True:
					data = input("Which data would you like to copy? (title / username / password / url), or press ENTER\n> ").strip().lower()
					if data in ["title", "username", "password", "url"]:
						pyperclip.copy(entry[["title", "username", "password", "url"].index(data) + 1])
						print(f"{data.capitalize()} copied to clipboard.")
						break
					else:
						print("Invalid choice. Please try again.")

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

				ttl, usr, psw, url = get_data()

				self.cursor.execute("create table if not exists storage(id INTEGER PRIMARY KEY, title TEXT, username TEXT, password TEXT, url TEXT);")
				self.cursor.execute("insert into storage (title, username, password, url) values (?, ?, ?, ?);", (ttl, usr, psw, url))
				self.connection.commit()
				print("Entry succesfully added.")
			elif kwargs.get("update"):
				column, value = get_filter()
				entries = self.fetch_entries(column, value)
				if not entries:
					print("No entries found!")
					return
				processed_entries = self.process_entries(entries, "update")

				if processed_entries:
					for entry in processed_entries:
						if isinstance(entry, tuple):
							entry_id = entry[0]
							print(f"Updating values for: {entry}")
							ttl, usr, psw, url = get_data()
							self.cursor.execute("update storage set title=?, username=?, password=?, url=? where id=?;", (ttl, usr, psw, url, entry_id,))
					self.connection.commit()
					print(f"Updated {len(processed_entries)} entry/entries.")
			elif kwargs.get("delete"):
				column, value = get_filter()
				entries = self.fetch_entries(column, value)
				if not entries:
					print("No entries found!")
					return
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
	def fetch_entries(self, filter_by, value):
		"""Fetch all entries if they exist.

		Parameters
		----------
		filter_by : str
			Name of column which is gonna be filtered.

		value : str
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
		except sqlite3.Error:
			print("Table doesn't exist yet. Add some entries first.")
			return

	def process_entries(self, entries, operation):
		"""Process fetched entries.

		Parameters
		----------
		entries : list
			List of fetched entries.
		operation : str
			Operation chosen by user.

		Returns
		-------
		entries : tuple
			Tuple containing arrays for each processed entry.		
		"""	
		print("------------------------------------------------------------")
		print(f"Found {len(entries)} matching entry/entries:")
		for idx, entry in enumerate(entries):
			entry_id, title, username, password, url = entry
			print(f"{idx+1}")
			print(f"Title: {title}")
			print(f"Username: {username}")
			print(f"Password: {password}")
			print(f"URL: {url}")
		print("------------------------------------------------------------")

		if len(entries) == 1:
			choice = input(f"Select an entry to {operation}, or press ENTER\n> ")
			index = int(choice) - 1
			return [entries[index]]
		else:
			choice = get_entry(operation, len(entries))
			if choice == "all":
				return entries
			else:
				try:
					index = int(choice) - 1
					if index >= 0 and index < len(entries):
						return [entries[index]]
					else:
						print("Invalid choice of entry.")
				except ValueError:
					print("Wrong data input.")

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