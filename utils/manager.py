import os
import sys
import getpass

from .aes import AESCipher
from .db import DbManip
from .constants import *

class PasswordManager:
	def __init__(self):
		self.encryptor = None
		self.dbmanip = DbManip()

	def prompt_menu(self):
		actions = {
			1: lambda: self.add(),
			2: lambda: self.search(),
			3: lambda: self.update(),
			4: lambda: self.delete(),
			5: lambda: self.change_key(),
			6: sys.exit
		}
		print("1 - Add entry")
		print("2 - Search entry")
		print("3 - Update entry")
		print("4 - Delete entry")
		print("5 - Change master key")
		print("6 - Exit")

		try:
			choice = int(input("> "))
			actions.get(choice, lambda: print("Wrong choice! Try again."))()
		except ValueError:
			print("Wrong data input! Try again.")
			self.prompt_menu()

	def add(self):
		ttl, usr, psw, url = self.prompt_data()
		if self.dbmanip.add_entry(title=ttl, username=usr, password=psw, url=url):
			print("Entry succesfully added.")
			self.prompt_menu()

	def search(self):
		if self.dbmanip.table_exists(DB_TABLE):
			filter_by, value = self.prompt_filter()
			self.dbmanip.search_entry(filter_by, value)

	def update(self):
		if self.dbmanip.table_exists(DB_TABLE):
			filter_by, value = self.prompt_filter()

	def delete(self):
		if self.dbmanip.table_exists(DB_TABLE):
			filter_by, value = self.prompt_filter()

	def prompt_filter(self):
		filter_by = str(input("Filter by (Title / Username / URL):\n> ")).split()[0].strip().lower()
		value = str(input("Enter value to search for in filtered column:\n> "))

		if filter_by not in ["title", "username", "url"]:
			print("Wrong filter specified! Try again.")
			self.prompt_filter()
		else:
			return filter_by, value

	def prompt_data(self):
		title = str(input("Title: (Mandatory)\n> "))
		if not title:
			print("Title has to be filled in.")
			self.prompt_data()
		username = str(input("Username (If none, leave empty)\n> "))
		password = getpass.getpass(prompt="Password: (Mandatory)\n> ")
		if not password:
			print("Password field has to be filled in.")
			self.prompt_data()
		url = str(input("URL: (If none, leave empty)\n> "))
		return title, username, password, url

	def auth(self):
		if not os.path.exists(STORAGE):
			os.mkdir(STORAGE)

		self.encryptor = AESCipher()

		if not os.path.exists(STORAGE_MASTER):
			master_key = getpass.getpass(prompt="Create master key: ")
			if self.dbmanip.write_key(master_key):
				self.encryptor.key = master_key
				self.prompt_menu()
		else:
			master_key = getpass.getpass(prompt=f"Enter master key for {STORAGE_DB}: ")
			if self.dbmanip.verify_key(master_key):
				self.encryptor.key = master_key
				self.prompt_menu()