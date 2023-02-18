import os
import sys
import getpass

from .aes import AESCipher
from .db import DatabaseHandler
from .constants import *

class PasswordManager:
	def __init__(self):
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
			print("Master key succesfully changed.")
			self.prompt_menu()

	def add(self):
		if self.dbmanip.add_entry():
			self.prompt_menu()

	def search(self):
		if self.dbmanip.table_exists(DB_TABLE):
			self.dbmanip.display_entry()

	def update(self):
		if self.dbmanip.table_exists(DB_TABLE):
			self.dbmanip.update_entry()

	def delete(self):
		if self.dbmanip.table_exists(DB_TABLE):
			self.dbmanip.delete_entry()

	def prompt_menu(self):
		actions = {
			1: lambda: self.add(),
			2: lambda: self.search(),
			3: lambda: self.update(),
			4: lambda: self.delete(),
			5: lambda: self.change(),
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
			self.prompt_menu()
		except ValueError:
			print("Wrong data input! Try again.")
			self.prompt_menu()