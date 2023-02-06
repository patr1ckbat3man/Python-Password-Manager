import os
import json

import bcrypt

from constants import *

class MasterManip(object):
	def __init__(self):
		if not os.path.exists(DB_FOLDER):
			os.mkdir(DB_FOLDER)

	def verify_key(self, key):
		salt = bcrypt.gensalt()
		master_hash = bcrypt.hashpw(key, salt)

		try:
			with open(f"{DB_FOLDER}/{DB_MASTER}", "r") as f:
				master_data = json.load(f)
				master_hash = master_data["hash"]
		except Exception:
			return False
		else:
			if bcrypt.checkpw(key, master_hash.encode()):
				return True
			else:
				return False

	def write_key(self, key):
		salt = bcrypt.gensalt()
		master_hash = bcrypt.hashpw(key, salt)
		master_data = {"hash": master_hash.decode()}

		with open(f"{DB_FOLDER}/{DB_MASTER}", "w") as f:
			json.dump(master_data, f, indent=4)