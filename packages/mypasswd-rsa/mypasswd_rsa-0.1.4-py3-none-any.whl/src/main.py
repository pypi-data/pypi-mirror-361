import os
from src.helper.rsa_crypt import setup_new_keys
from src.helper.add_passwd_db import new_site
from rich import print
from src.helper.random_passwd import generate_strong_passwd
from src.helper.mypasswd_helper import (
    get_file_path, 
    print_passwd_db, 
    get_db_path_and_file,
    file_exist,
    find_passwd,
    )


# Globals
file_path = get_file_path()
db_file = get_db_path_and_file()


def welcome():
    print(r"""
 __  __                                       _ 
|  \/  |_   _ _ __   __ _ ___ _____      ____| |
| |\/| | | | | '_ \ / _` / __/ __\ \ /\ / / _` |
| |  | | |_| | |_) | (_| \__ \__ \\ V  V / (_| |
|_|  |_|\__, | .__/ \__,_|___/___/ \_/\_/ \__,_|
        |___/|_|                                
""")
    print('[magenta]********************************')
    menu()


def check_pem() -> bool:
    '''  check if private.pem exist  '''
    # check if private.pem exist
    if not file_exist(file_path + 'private.pem'):
        print(file_path + "private.pem")
        print('"private.pem" do not exist! Do you wont to set up new public and private.pem?')
        answer = input("(Y/n): ")
        if answer == "y" or answer == "Y" or  answer == "":
            os.mkdir(file_path, mode=0o770, dir_fd=None)
            setup_new_keys(file_path)
            print("new keys in: ", file_path)
            return True
        else:
            return False
    return True


def menu():
    print("[green]*[/green] [yellow]'q'[/yellow] [green]-[/green] [yellow]Quit [/yellow]")
    print("[green]*[/green] [yellow]'m'[/yellow] [green]-[/green] [yellow]Menu [/yellow]")
    print("[green]*[/green] [yellow]'l'[/yellow] [green]-[/green] [yellow]List passwd db [/yellow]")
    print("[green]*[/green] [yellow]'a'[/yellow] [green]-[/green] [yellow]Add new site [/yellow]")
    print("[green]*[/green] [yellow]'s'[/yellow] [green]-[/green] [yellow]print Strong passwd [/yellow]")
    print("[green]*[/green] [yellow]'f'[/yellow] [green]-[/green] [yellow]Find site with user and passwd [/yellow]")
    print('[magenta]********************************')


def main():
    welcome()
    run = True
    if not check_pem():
        run = False
        print('Somthing went wrong! Could not create: ', db_file)

    while run:
        answer = input("mypasswd ('q' - quit or 'm' - menue): ")
        if answer == 'q':
            run = False
        elif answer == 'm':
            menu()
        elif answer == 'l':
            print_passwd_db(db_file)
        elif answer == 'a':
            new_site()
        elif answer == 'f': # find site with user and passwd
            site_name = input("Find site: ")
            find_passwd(site_name)
        elif answer == 's':
            print(generate_strong_passwd(15))


if __name__ == "__main__":
    main()