## Installation
Install dependencies:
```bash
sudo apt-get install build-essential cargo
sudo apt-get install xclip
```
Create a virtual environment and install packages:
```bash
python3 -m venv env
source env/bin/activate
(env) pip3 install -r requirements.txt
```
Run the application:
```bash
python3 main.py
```
## Authentication
```python3
key_hash = self.cursor.execute("select hash from user;").fetchone()[0]
if bcrypt.checkpw(key.encode(), key_hash):
    return True
else:
    return False
```
## Vulnerabilities
If an attacker gets access to the database file where the user's password hash is kept or the encrypted database file, it's not a huge deal. But if either of these files gets deleted, all the stored data will be gone for good and most likely can't be recovered.
## Performance
This manager is not efficient at all because the database is decrypted and encrypted everytime an operation is executed. This is because I didn't want to leave the database file decrypted during the whole time the app is running, even though it doesn't really matter because the database is decrypted the whole time any operation is getting executed by user.
## Disclaimer
I strongly advise you to not use this as your actual password manager and use something that is maintained properly and up to all security standars like KeepassXC. This was just a small project.