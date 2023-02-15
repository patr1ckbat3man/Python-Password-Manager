import os
import sqlite3

class DbManip:
	def __init__(self):
		self.connection = None
		self.cursor = None

	def create_storage(self):
		if not os.path.exists(f"{DB_FOLDER}/{DB_STORAGE}"):
			open(f"{DB_FOLDER}/{DB_STORAGE}", "w").close()
		self.connection = sqlite3.connect(f"{DB_FOLDER}/{DB_STORAGE}")
		self.cursor = self.connection.cursor()
		self.cursor.execute("create table if not exists storage(title TEXT, username TEXT, password TEXT, url TEXT)")
		self.connection.commit()
		self.CREATED = True

	def table_exists(self):
		self.cursor.execute("select name from sqlite_master where type='table' and name='storage'")
		result = self.cursor.fetchall()

		if result:
			return True
		else:
			return False

	def entry_exists(self, filter_by, value):
		if filter_by not in ["Title", "URL", "Username"]:
			return (False, [])

		try:
			self.cursor.execute(f"select * from storage WHERE {filter_by}=?", (value,))
			result = self.cursor.fetchall()
		except sqlite3.OperationalError:
			return (False, [])

		if result:
			return (True, result)
		else:
			return (False, [])

	def add(self, **kwargs):
		columns = ", ".join(kwargs.keys())
		placeholders = ", ".join(["?"] * len(kwargs))
		query = f"insert into storage ({columns}) values ({placeholders})"
		self.cursor.execute(query, tuple(kwargs.values()))
		self.connection.commit()

	def delete(self, **kwargs):
		pass

	def close(self):
        pass
