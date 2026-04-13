import hashlib
import sys
import sqlite3


def login_screen(db):
    print()
    print("Enter the realm...")
    print()
    while True:
        username = (
            input("By what name are you called, adventurer?\n> ")
            .strip()
            .capitalize()
            .replace(" ", "")
            .encode("ascii", "ignore")
            .decode()
        )
        existing = db.execute(
            "SELECT 1 FROM players WHERE name = ? LIMIT 1", (username,)
        ).fetchone()
        if not username:
            print("\nInvalid response. Please try again.\n")
            continue
        if not existing:
            print(f"\nI know none by the name of {username}.\n")
            continue
        break
    
    failed_logins = 0
    while True:
        password = (
            input(f"\nWhat might your password be, {username}?\n> ")
            .strip()
            .encode("ascii", "ignore")
            .decode()
        )
        login_check = db.execute(
            "SELECT 1 FROM players WHERE name = ? AND password = ?",
            (username, hashlib.sha256(password.encode()).hexdigest()),
        ).fetchone()
        if login_check:
            print("Enter the realms.")
            return username
            
        else:
            print(f"Failed login. {3-failed_logins} attempts remaining.")
            if failed_logins == 3:
                print("Closing connection...")
                sys.exit()
            else:
                failed_logins += 1
                continue
                
