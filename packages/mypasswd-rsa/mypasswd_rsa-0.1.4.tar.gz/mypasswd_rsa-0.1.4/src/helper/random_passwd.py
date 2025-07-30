import random
import string

def generate_strong_passwd(length=20):
    # Define the character set
    chars = string.ascii_letters + string.digits + "_.,"
    
    # Generate password
    password = ''.join(random.choice(chars) for _ in range(length))
    return password