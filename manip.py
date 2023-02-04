import os
import json
import secrets
from string import ascii_letters, digits, punctuation

import bcrypt
from Crypto.Cipher import AES

FOLDER = "database"
MASTER_FILE = "master.json"
STORAGE_FILE = "storage.json"

def master_file_exists():
	"""Check whether the file where master passwords is located exists.

	Args:
		None

	Returns:
		bool: True if file already exists or False if it doesn't.
	"""
	if os.path.exists(f"{FOLDER}/{MASTER_FILE}"):
		return True, f"{FOLDER}/{MASTER_FILE}"
	else:
		return False

def verify_password(master_password):
	"""Verify the master password entered by the user.

	Args:
		master_password (str): Master password of the end user.

	Returns:
		bool: True if hash matches or False if it doesn't or there is something wrong with the file.
	"""
	master_salt = bcrypt.gensalt()
	master_hash = bcrypt.hashpw(master_password, master_salt)
	try:
		with open(f"{FOLDER}/{MASTER_FILE}", "r") as f:
			master_data = json.load(f)	
		if bcrypt.checkpw(master_password, master_data["hash"].encode()):
			return True
		else:
			return False
	except Exception:
		return False

def write_password(master_password):
	"""Write the hash of the user into a json file.

	Args:
		master_password (str): Master password of the end user.

	Returns:
		None
	"""
	master_salt = bcrypt.gensalt()
	master_hash = bcrypt.hashpw(master_password, master_salt)
	master_data = {
	"hash": master_hash.decode()
	}
	with open(f"{FOLDER}/{MASTER_FILE}", "w") as f:
		json.dump(master_data, f, indent=4)

def generate_password(length):
	"""Generate secure password based on the user chosen length.

	Args:
		length (int): Length of the password.

	Returns:
		str: Generated password.
	"""
	return "".join(secrets.choice(ascii_letters+digits+punctuation) for _ in range(length))

def pack_data(**kwargs):
	"""Pack the data from the newly created entry.

	Args:
		**kwargs: Keyword arguments.

	Returns:
		dict: A json object.
	"""
	data = json.dumps(kwargs)
	return json.loads(data)

def create_storage():
	"""Create a storage, where all the data will be saved.

	Args:
		None

	Returns:
		None
	"""
	if not os.path.exists(f"{FOLDER}/{STORAGE_FILE}"):
		with open(f"{FOLDER}/{STORAGE_FILE}", "w") as f:
			pass

def delete_storage():
	"""Delete the storage, where all the data is located.

	Args:
		None

	Returns:
		None
	"""
	pass

def encrypt_storage(key):
	"""Encrypt the data storage.

	Args:
		key (str): Master password of the end user.

	Returns:
		None
	"""
	pass 

def decrypt_storage(key):
	"""Decrypt the data storage.

	Args:
		key (str): Master password of the end user.

	Returns:
		None
	"""
	pass

def insert_entry(data):
	"""Insert an entry of data into the storage.

	Args:
		data (dict): A json object.

	Returns:
		None
	"""
	pass

def delete_entry(data):
	"""Delete an entry of data from the storage.

	Args:
		data (dict): a json object.

	Returns:
		None
	"""
	pass