import os
import sys
import getpass

from .aes import AESCipher
from .db import DatabaseHandler
from .constants import *

class PasswordManager:
	def __init__(self):
		self.encryptor = None
		self.datamanip = None

	def auth(self):
		if not os.path.exists(FOLDER):
			os.mkdir(FOLDER)

		self.encryptor = AESCipher()
		self.datamanip = DatabaseHandler(self.encryptor)

		if not os.path.exists(MASTER_DB):
			master_key = getpass.getpass("Create master key: ")
			if self.datamanip.handle_key(master_key, write=True):
				self.encryptor.key = master_key
				self.prompt_menu()
		else:
			master_key = getpass.getpass(f"Enter master key for {STORAGE_DB}: ")
			if self.datamanip.handle_key(master_key, verify=True):
				self.encryptor.key = master_key
				self.prompt_menu()

	def change(self):
		new_key = getpass.getpass("Enter new master key: ")
		if self.datamanip.handle_key(new_key, change=True):
			self.encryptor.key = new_key
			print("Master key succesfully changed.")
			self.prompt_menu()

	def close_database(self):
		"""Check whether the file is encrypted and all connections are closed before exiting.
		"""
		if os.path.isfile(STORAGE_DB) and os.path.getsize(STORAGE_DB) > 0:
			if not self.encrypted:
				self.encryptor.encrypt()
				self.encrypted = True
		else:
			self.encrypted = False
		self._close_connections()
		print("Exiting...")
		sys.exit()

	def prompt_menu(self):
		actions = {
			1: lambda: self.datamanip.add_entry(),
			2: lambda: self.datamanip.display_entry(),
			3: lambda: self.datamanip.update_entry(),
			4: lambda: self.datamanip.delete_entry(),
			5: lambda: self.change(),
			6: lambda: sys.exit(),
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