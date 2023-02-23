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
			else:
				print("You have either entered incorrect password or the database is corrupt.")

	def change(self):
		new_key = getpass.getpass("Enter new master key: ")
		if self.datamanip.handle_key(new_key, change=True):
			self.encryptor.key = new_key
			print("Master key succesfully changed.")
			self.prompt_menu()

	def prompt_menu(self):
		actions = {
			1: lambda: self.datamanip.handle_database(add=True),
			2: lambda: self.datamanip.display_entry(),
			3: lambda: self.datamanip.handle_database(update=True),
			4: lambda: self.datamanip.handle_database(delete=True),
			5: lambda: self.change(),
			6: lambda: self.on_close(),
			"default": lambda: os.system("cls||clear")
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
			os.system("cls||clear")
			self.prompt_menu()

	def on_close(self):
		self.datamanip.close_database()