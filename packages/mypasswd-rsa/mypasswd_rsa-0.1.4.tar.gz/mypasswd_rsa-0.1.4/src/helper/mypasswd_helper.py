import os
import json
import rsa
import base64
from rich.table import Table
from rich import print


file_path = os.path.expanduser("~/.mypasswd_pem/")


def get_file_path():
    return file_path

def get_db_path_and_file():
    return file_path + "passwd_db.json"


def file_exist(path) -> bool:
    if not os.path.exists(path):
        return False
    else:
        return True


def get_public_key():
    ''' read public.pem and return public key '''
    with open(file_path + "public.pem", "rb") as f:
        public_key = rsa.PublicKey.load_pkcs1(f.read())
    return public_key


def get_private_key():
    ''' read private.pem and return private key '''
    with open(file_path + "private.pem", "rb") as f:
        private_key = rsa.PrivateKey.load_pkcs1(f.read())
    return private_key


def encrypt_message(message):
    encrypted_mess = rsa.encrypt(message.encode(), get_public_key())
    return encrypted_mess


def decrypt_message(message):
    decrypted_mess = rsa.decrypt(message, get_private_key())
    return decrypted_mess.decode()


def convert_base64(message):
    # Convert the encrypted bytes to a base64-encoded string
    base64_message = base64.b64encode(message).decode("utf-8")
    return base64_message


def decrypt_from_base64(base64_message):
    """ Decrypts a base64-encoded RSA-encrypted message."""
    # Decode the base64 message to bytes
    encrypted_bytes = base64.b64decode(base64_message.encode())

    # Decrypt the message using the private key
    decrypted_bytes = decrypt_message(encrypted_bytes)

    return decrypted_bytes


def get_json_file(file):
    ''' open file data, return json_list '''
    data_file = file
    # load data from json file
    try:
        with open(data_file, 'r', encoding='utf-8') as f:
            data_list = json.load(f)
        return data_list
    except FileNotFoundError :
        print(file, " do not exist")
        return [] # return emty list


def print_passwd_db(file=get_db_path_and_file()):
    ''' open file data, print rich.table from json_list '''
    # load data from json file
    data_list = get_json_file(file)
   
    # create a table
    table = Table(title=file, style="orange1", show_lines=True)
    
    # add columns to the table
    table.add_column("Site", style="green")
    table.add_column("User", style="cyan")
    table.add_column("Passwd", style="cyan")
    
    # add rows to the table
    for data in data_list:
        site = decrypt_from_base64(data['Site'])
        user = decrypt_from_base64(data['User'])
        passwd = decrypt_from_base64(data['Passwd'])
        table.add_row(site, user, passwd)
    
    # print the table using rich console
    print(table)


## find passwd
def find_passwd(site_name):
    ''' open file data, print rich.table from json_list '''
    # load data from json file
    data_list = get_json_file(get_db_path_and_file())
   
    # create a table
    table = Table(title=get_file_path(), style="orange1", show_lines=True)
    
    # add columns to the table
    table.add_column("Site", style="green")
    table.add_column("User", style="cyan")
    table.add_column("Passwd", style="cyan")
    
    # add rows to the table
    for data in data_list:
        site = decrypt_from_base64(data['Site'])
        user = decrypt_from_base64(data['User'])
        passwd = decrypt_from_base64(data['Passwd'])
        if site_name.upper() in site.upper():
            table.add_row(site, user, passwd)
    
    # print the table using rich console
    print(table)

## TEST ##
def testing():
    # Encrypt the message
    message = "Hej på dig!"
    encrypted_message = encrypt_message(message)
    
    # Convert the encrypted bytes to a base64-encoded string
    encrypted_message_base64 = base64.b64encode(encrypted_message).decode("utf-8")
    
    # Save the encrypted message to a JSON file
    data = {"encrypted_message": encrypted_message_base64}
    with open(get_file_path() + "encrypted_message.json", "w") as f:
        json.dump(data, f)
    
    # Load the encrypted message from the JSON file and decrypt it
    with open(get_file_path() + "encrypted_message.json", "r") as f:
        data = json.load(f)
        encrypted_message_base64 = data["encrypted_message"]
        encrypted_message_json = base64.b64decode(encrypted_message_base64.encode("utf-8"))
        # decrypted_base64_json = decrypt_message(encrypted_message_json)
    
        decrypted_message_json = decrypt_message(encrypted_message)
 #       decrypted_base64 = decrypt_message(decrypted_base64_json)

    print(f"Original message: {message}")
    print(f"Decrypted message: {decrypted_message_json}")
    print(f"Encrypted message: {encrypted_message_json}")
    print(f"Encrypted_64 message: {encrypted_message_base64}")
 #   print(f"Decrypted_64 !!!: {decypted_base64}")
