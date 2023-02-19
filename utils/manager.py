import os
import sys
import getpass

from .aes import AESCipher
from .db import DatabaseHandler
from .constants import *

class PasswordManager:
	def __init__(self):
		self.encrypted = None
		self.encryptor = None
		self.dbmanip = DatabaseHandler()

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

	def change(self):
		new_key = getpass.getpass(prompt="Enter new master key: ")
		if self.dbmanip.change_key(new_key):
			self.encryptor.key = new_key
			print("Master key succesfully changed.")
			self.prompt_menu()

	def update_db(func):
		def wrapper(self, *args, **kwargs):
			if os.path.isfile(f"{STORAGE_DB}.enc"):
				self.encryptor.decrypt()

			result = func(self, *args, **kwargs)

			self.encryptor.encrypt()

			return result
		return wrapper

	@update_db
	def add(self):
		if self.dbmanip.table_exists(DB_TABLE):
			self.dbmanip.add_entry()

	@update_db
	def search(self):
		if self.dbmanip.table_exists(DB_TABLE):
			self.dbmanip.display_entry()

	@update_db
	def update(self):
		if self.dbmanip.table_exists(DB_TABLE):
			self.dbmanip.delete_entry()

	@update_db
	def delete(self):
		if self.dbmanip.table_exists(DB_TABLE):
			self.dbmanip.delete_entry()

	def exit(self):
		if os.path.isfile(STORAGE_DB) and os.path.getsize(STORAGE_DB) > 0:
			if not self.encrypted:
				self.encryptor.encrypt()
				self.encrypted = True
		else:
			self.encrypted = False
		print("Exiting...")
		sys.exit()	

	def prompt_menu(self):
		actions = {
			1: lambda: self.add(),
			2: lambda: self.search(),
			3: lambda: self.update(),
			4: lambda: self.delete(),
			5: lambda: self.change(),
			6: lambda: self.exit(),
			"default": lambda: print("Wrong choice! Try again.")
		}

		print("1 - Add entry")
		print("2 - Search entry")
		print("3 - Update entry")
		print("4 - Delete entry")
		print("5 - Change master key")
		print("6 - Exit")

		try:
			choice = int(input("> "))
			action = actions.get(choice, actions["default"])
			action()
			self.prompt_menu()
		except ValueError:
			print("Wrong data input! Try again.")
			self.prompt_menu()