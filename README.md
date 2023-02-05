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
(env) pip3 install -r requirements.txt
```
Run the application:
```bash
python3 main.py
```
## Vulnerabilities
If a attacker gets access to the JSON file where the user's password hash is kept or the encrypted database file, it's not a huge deal. But if either of these files gets deleted, all the stored data will be gone for good and most likely can't be recovered.
## License
MIT