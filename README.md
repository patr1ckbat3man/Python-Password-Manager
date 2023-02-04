# Vault
A password manager that runs on your computer, allowing you to access your passwords and other sensitive information without an internet connection.
## Installation
Install dependencies:
```bash
sudo apt-get install xclip
sudo apt-get install build-essential cargo
```
Create a virtual environment and install packages:
```bash
python3 -m venv env
source env/bin/activate
(env) python3 -m pip install -r requirements.txt
```
Run the application:
```bash
python3 main.py
```
## Vulnerabilities
Both the json files where the hash of the master password is stored and the encrypted storage file, which contains all of your login credentials and other sensitive information, are located inside the database folder. This is acceptable even if they are read by a potential attacker, but if they are deleted, all of your data will be lost.
## Rant
For some reason every single python3 bind for sqlcipher is either not maintained anymore and potentionally contains many security vulnerabilities (not like this project doesn't), or just takes a whole day to get to run. Thats why for encrypting/decrypting the database in this project I am using Crypto primitives.
## License
MIT
