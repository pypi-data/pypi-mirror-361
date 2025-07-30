import json
from rich.console import Console
from src.helper.random_passwd import generate_strong_passwd
from src.helper.mypasswd_helper import (
    convert_base64,
    encrypt_message,
    get_db_path_and_file,
    print_passwd_db,
)

console = Console()


def encrypt_string(s):
    # encrypt with rsa and change to codex base64
    crypted_string = encrypt_message(s)
    base64_string = convert_base64(crypted_string)
    return base64_string
    

def new_site():
    mypasswd = get_db_path_and_file()
    console.print(f"Add new Site, User and Passwd to the database: {mypasswd}")
    
    # Load existing data
    try:
        with open(mypasswd, 'r', encoding='utf-8') as f:
            data_list = json.load(f)
    except FileNotFoundError:
        data_list = []

    while True:
        answer = console.input("[bold green]Enter[/] to continue (or 'q' to quit): ")
        if answer == 'q':
            break

        # ask for site-name, user and passwd
        site = console.input("Enter [bold green]site[/] name: ")
        crypt_site = encrypt_string(site)
        user = console.input("Enter [bold green]user[/] name: ")
        crypt_user = encrypt_string(user)

        # sugest a ramdom passwd
        print(generate_strong_passwd(15))

        passwd = console.input("Enter [bold green]password[/]: ")
        crypt_passwd = encrypt_string(passwd)

        data_list.append({'Site': crypt_site, 'User': crypt_user, 'Passwd': crypt_passwd})

    # Write updated data
    with open(mypasswd, 'w', encoding='utf-8') as f:
        json.dump(data_list, f, ensure_ascii=False, indent=4)

    # print out the db to the console
    print_passwd_db()