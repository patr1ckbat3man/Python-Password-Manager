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
		print("1 - Add entry")
		print("2 - Search entry")
		print("3 - Update entry")
		print("4 - Delete entry")
		print("5 - Change master key")
		print("6 - Exit")

		try:
			choice = int(input("> "))
			if choice == 1:
				t, u, p, u = self.prompt_data()
				if self.dbmanip.add_entry(title=t, username=u, password=p, url=u):
					print("Entry succesfully added.")
				else:
					print("Error while adding entry.")
			elif choice == 2:
				filter_by = self.prompt_filter()
				self.dbmanip.search_entry(filter_by)
			elif choice == 3:
				filter_by = self.prompt_filter()
				self.dbmanip.update_entry(filter_by)
			elif choice == 4:
				filter_by = self.prompt_filter(filter_by)
				self.dbmanip.delete_entry()
			elif choice == 5:
				key = getpass.getpass("Enter new master key: ")
				if self.dbmanip.change_key(key):
					print("Master key succesfully changed.")
				else:
					print("There was an error while changing password.")
			elif choice == 6:
				print("Exiting...")
				sys.exit()
			else:
				print("Wrong choice! Try again.")
				self.prompt_menu()
		except ValueError:
			print("Wrong data input. Try again.")
			self.prompt_menu()

	def prompt_filter(self):
		filter_by = str(input("Filter by (Title / Username / URL): ")).split()[0].strip().lower()

		if filter_by not in ["title", "username", "url"]:
			print("Wrong filter specified! Try again.")
			self.prompt_filter()
		return filter_by

	def prompt_data(self):
		title = str(input("Title: (Mandatory) "))
		username = str(input("Username (If not, leave empty) "))
		password = getpass.getpass(prompt="Password: (Mandatory) ")
		url = str(input("URL: (If not, leave empty) "))

		if not title or not password:
			print("Both title and password need to be filled in.")
			self.prompt_data()
		else:
			return title, username, password, url
			print(title, type(username), password, type(url))

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
				print("Error writing master key to database.")
		else:
			master_key = getpass.getpass(prompt=f"Enter master key for {STORAGE_DB}: ")
			if self.dbmanip.verify_key(master_key):
				self.encryptor.key = master_key
				self.prompt_menu()
			else:
				print("Error veryfing master key. Database might be corrupted or password is incorrect.")
