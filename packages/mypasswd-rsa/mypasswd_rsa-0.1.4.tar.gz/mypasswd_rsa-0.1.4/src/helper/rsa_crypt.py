import rsa
from src.helper.mypasswd_helper import get_file_path

file_path = get_file_path()


def setup_new_keys(file_path):
    ''' Delete the rsa-keys and creat new keys in file_path'''

    public_key, private_key = rsa.newkeys(1024)
    
    with open(file_path + "public.pem", "wb") as f:
        f.write(public_key.save_pkcs1("PEM"))
    
    with open(file_path + "private.pem", "wb") as f:
        f.write(private_key.save_pkcs1("PEM"))


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


def write_encrypt_message_to_file(message, file_name):
    ''' write encrypted message to file '''
    with open(file_name, "wb") as f:
        f.write(message)
        print(f"add message to {file_name}")


def decrypt_message_from_file(file_name):
    ''' open encryted message and return decrypted message '''
    encrypt_message = open(file_name, "rb").read()
    clear_message = rsa.decrypt(encrypt_message, get_private_key())
    return clear_message.decode()

