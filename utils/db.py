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
			Boolean indicating whether the key was sucesfully written.
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
			Boolean indicating wheter the entered master key is valid.
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
			Boolean indicating wheter the key was changed.
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
		"""Check for the table existence in database.

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
			self.cursor.execute("select name from sqlite_master where type='table' and name = ?;", (table_name,))
			result = self.cursor.fetchall()
			if result:
				return True
			else:
				print("No data to query! Add some entries first.")
				return False
		except sqlite3.Error:
			print("Error occurred while checking the existence of table.")
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
		result : tuple
			Tuple of filtered row/rows, if some entries are found.
		bool
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
		"""Add user entries to database.

		Parameters
		----------
		None

		Returns
		-------
		bool
			Boolean indicating whether the entry was added.
		"""
		if not os.path.exists(STORAGE_DB):
			open(STORAGE_DB, "a").close()

		ttl, usr, psw, url = self.prompt_data()

		try:
			self.connection = sqlite3.connect(STORAGE_DB)
			self.cursor = self.connection.cursor()
			self.cursor.execute("create table if not exists storage(id INTEGER PRIMARY KEY, title TEXT NOT NULL, username TEXT, password TEXT NOT NULL, url TEXT);")
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
		"""Display filtered entries.

		Parameters
		----------
		None

		Returns
		-------
		None
		"""
		column, value = self.prompt_filter()
		entries = self.fetch_entries(column, value)
		processed_entries = self.process_entries(entries, "display", prompt=False)

	def update_entry(self):
		"""Update filtered entries.

		Parameters
		----------
		None

		Returns
		-------
		bool
			boolean indicating whether the entries were succesfully updated.
		"""
		column, value = self.prompt_filter()
		entries = self.fetch_entries(column, value)
		processed_entries = self.process_entries(entries, "update")

		try:
			self.connection = sqlite3.connect(STORAGE_DB)
			self.cursor = self.connection.cursor()

			if processed_entries: # Have to check, otherwise we might get NoneType error
				for entry in processed_entries:
					if isinstance(entry, tuple):
						entry_id = entry[0]
						print(f"Updating values for: {entry}")
						ttl, usr, psw, url = self.prompt_data()
						self.cursor.execute("update storage set title = ?, username = ?, password = ?, url = ? WHERE id = ?;", (ttl, usr, psw, url, entry_id,))
				self.connection.commit()
				print(f"Updated {len(processed_entries)} entry/entries.")
			return True
		except sqlite3.Error:
			print("Error occurred while updating entry/entries from database.")
			return False
		finally:
			self.close_connections()

	def delete_entry(self):
		"""Delete filtered entries.

		Parameters
		----------
		None

		Returns
		-------
		None
		"""
		column, value = self.prompt_filter()
		entries = self.fetch_entries(column, value)
		processed_entries = self.process_entries(entries, "delete")

		try:
			self.connection = sqlite3.connect(STORAGE_DB)
			self.cursor = self.connection.cursor()

			if processed_entries:
				for entry in processed_entries:
					if isinstance(entry, tuple):
						entry_id = entry[0]
						self.cursor.execute("delete from storage where id = ?;", (entry_id,))
				self.connection.commit()
				print(f"Deleted {len(processed_entries)} entry/entries.")
			return True
		except sqlite3.Error:
			print("Error occurred while deleting entry/entries from database.")
			return False
		finally:
			self.close_connections()

	def prompt_data(self):
		"""Display choices of data to be entered into entry.

		Parameters
		----------
		None

		Returns
		-------
		title : str
			Title 
		username : str
			Username 
		password : str
			Password
		url : str
			URL
		"""
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

	def process_entries(self, entries, operation, prompt=True):
		"""Process fetched entries.

		Parameters
		----------
		entries : list
			List of fetched entries.
		operation : string
			Operation chosen by user.
		prompt : bool
			boolean indicating whether the prompt is gonna appear or not.

		Returns
		-------
		entries : tuple
			tuple containing arrays for each processed entry.		
		"""
		if not entries:
			print("No entries found.")
			return

		print(f"Found {len(entries)} matching entry/entries:")
		print("<choice> - (ID, Title, Username, Password, URL)")
		for idx, val in enumerate(entries):
			print(f"{idx+1} - {val}")

		if prompt:
			if len(entries) == 1:
				choice = input(f"Select an entry to {operation}:\n> ")
				index = int(choice) - 1
				return [entries[index]]
			else:
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
						print("Wrong data input!")
						return
		else:
			return entries

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