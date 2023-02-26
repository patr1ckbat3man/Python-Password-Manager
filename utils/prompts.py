__all__ = ["get_data", "get_filter", "get_entry"]

import getpass

def get_data():
	"""Prompts the user to enter data for a new entry.

	Parameters
	----------
	None

	Returns
	-------
	tuple
		A tuple containing the title, username, password, and URL.
	"""
	title = input("Title: (Mandatory)\n> ").strip()
	while not title:
		print("Title has to be filled in.")
		title = input("Title: (Mandatory)\n> ").strip()

	username = input("Username: (If none, leave empty)\n> ").strip()

	password = None
	while not password:
		password = getpass.getpass("Password: (Mandatory)\n> ")
		if not password:
			print("Password field has to be filled in.")

	url = input("URL: (If none, leave empty)\n> ").strip()

	return title, username, password, url

def get_filter():
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
			print("Wrong filter specified.")
			return prompt_filter()

		column_filter = filter_options[column]
		value = input(f"Value to search for in {column_filter} column:\n> ").strip().lower()

		return column_filter, value

def get_entry(operation, num_entries):
	"""Get user input based on operation.

	Parameters
	----------
	operation : str
		Operation chosen by user.
	num_entries : int
		Number of fetched entries.

	Returns
	-------
	choice : str
		User choice for operation.
	"""
	if operation == "copy data from":
		prompt = f"Select an entry to {operation} (1-{num_entries})\n> "
	else:
		prompt = f"Select an entry to {operation} (1-{num_entries}), or 'all':\n> "
			
	choice = input(prompt)
	return choice