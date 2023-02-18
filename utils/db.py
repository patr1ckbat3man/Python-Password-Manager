import os
import sqlite3
import getpass

import bcrypt

from .constants import *

class DatabaseHandler:
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
			print("Error occurred while changing the master key.")
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
			Tuple of filtered row/rows, if some entries are found.
			False, if the entry doesn't exist.
		"""
		try:
			self.connection = sqlite3.connect(STORAGE_DB)
			self.cursor = self.connection.cursor()
			self.cursor.execute(f"select * from storage where {filter_by} = ?", (value,))
			result = self.cursor.fetchall()
			if result:
				return result
			else:
				return False
		except sqlite3.Error:
			print("Error wile checking for existence of entry.")
			return False
		finally:
			self.close_connections()

	def add_entry(self):
		if not os.path.exists(STORAGE_DB):
			open(STORAGE_DB, "a").close()

		ttl, usr, psw, url = self.prompt_data()

		try:
			self.connection = sqlite3.connect(STORAGE_DB)
			self.cursor = self.connection.cursor()
			self.cursor.execute("create table if not exists storage(title TEXT NOT NULL, username TEXT, password TEXT NOT NULL, url TEXT);")
			self.cursor.execute(f"insert into storage (title, username, password, url) values (?, ?, ?, ?);", (ttl, usr, psw, url,))
			self.connection.commit()
			print("Entry succesfully added.")
			return True
		except sqlite3.Error:
			print("Error while adding entry.")
			return False
		finally:
			self.close_connections()

	def display_entry(self):
		column, value = self.prompt_filter()
		entries = self.fetch_entries(column, value)
		processed_entries = self.process_entries(entries, "display", prompt=False)

		for entry in processed_entries:
			print(entry)

	def update_entry(self):
		column, value = self.prompt_filter()
		entries = self.fetch_entries(column, value)
		processed_entries = self.process_entries(entries, "update")

		for entry in processed_entries:
			print(entry)

	def delete_entry(self):
		column, value = self.prompt_filter()
		entries = self.fetch_entries(column, value)
		processed_entries = self.process_entries(entries, "delete")

		for entry in processed_entries:
			print(entry)

	def prompt_data(self):
		title = str(input("Title: (Mandatory)\n> "))
		if not title:
			print("Title has to be filled in.")
			self.prompt_data()
		username = str(input("Username: (If none, leave empty)\n> "))
		password = getpass.getpass(prompt="Password: (Mandatory)\n> ")
		if not password:
			print("Password field has to be filled in.")
			self.prompt_data()
		url = str(input("URL: (If none, leave empty)\n> "))
		return title, username, password, url

	def prompt_filter(self):
		filter_options = {
			"t": "title",
			"u": "username",
			"r": "url"
		}

		column = input("Filter by (t=Title / u=Username / r=URL):\n> ").strip().lower()
		if column not in filter_options:
			print("Wrong filter specified! Try again.")
			self.prompt_filter()
		column_filter = filter_options[column]

		value = input(f"Value to search for in {column_filter} column:\n> ").strip().lower()

		return column_filter, value

	def process_entries(self, entries, operation, prompt=True):
		"""Process fetched entries.

		Parameters
		----------
		entries : list
			List of fetched entries.
		operation : string
			Operation chosen by user.

		Returns
		-------
		None		
		"""
		if not entries:
			print("No entries found.")
			return

		if len(entries) == 1:
			return entries[0]
		else:
			print(f"Found {len(entries)} matching entries:")
			for idx, val in enumerate(entries):
				print(f"{idx+1} - {val}")

			if prompt:
				choice = input(f"Select an entry to {operation} (1-{len(entries)}), or 'all':\n> ")
				if choice == "all":
					return entries
				elif choice.isdigit():
					try:
						index = int(choice) - 1
						if index >= 0 and index < len(entries):
							return [entries[index]]
						else:
							print("Invalid choice!")
							return
					except ValueError:
						print("Invalid choice!")
						return

	def close_connections(self):
		if self.connection:
			self.cursor.close()
			self.connection.close()
			self.cursor = None
			self.connection = None