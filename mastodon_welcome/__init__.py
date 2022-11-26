import argparse
from mastodon import Mastodon
import os
import sqlite3
import tomllib

ACCOUNT_FETCH_LIMIT = 100000

def check_db_exists(cursor: sqlite3.Cursor) -> bool:
    res = cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='welcome_log'")
    if res.fetchone()[0] == 0:
        cursor.execute("CREATE TABLE welcome_log (id INTEGER PRIMARY KEY, username TEXT, userdb_id INTEGER, welcomed INTEGER DEFAULT 0)")
        return False
    return True

def user_exists(cursor: sqlite3.Cursor, userid: int) -> bool:
    res = cursor.execute("SELECT COUNT(*) FROM welcome_log WHERE userdb_id = ?", (userid,))
    return res.fetchone()[0] > 0

def user_welcomed(cursor: sqlite3.Cursor, userid: int) -> bool:
    res = cursor.execute("SELECT COUNT(*) FROM welcome_log WHERE userdb_id = ? AND welcomed = 1", (userid,))
    return res.fetchone()[0] > 0

def set_user_welcomed(cursor: sqlite3.Cursor, userid: int):
    cursor.execute("UPDATE welcome_log SET welcomed = 1 WHERE userdb_id = ?", (userid, ))

def create_user(cursor: sqlite3.Cursor, userid: int, username: str):
    cursor.execute("INSERT INTO welcome_log (userdb_id, username) VALUES(?, ?)", (userid, username))


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(
        description = "Welcomes users to the Mastodon instance",
        epilog = "Note: the user this bot logs in as must have admin:read:accounts access"
    )
    arg_parser.add_argument('--email', required=False, help="Only required for first execution")
    arg_parser.add_argument('--password', required=False, help="Only required for first execution")
    arg_parser.add_argument('--config', default="config.toml")
    args = arg_parser.parse_args()

    config = None # not strictly required, but I like explicit scope
    with open(args.config, "rb") as toml_file:
        config = tomllib.load(toml_file)

    mastodon = None

    if not os.path.exists(config['mastodon']['credential_storage']):
        if not (args.email and args.password):
            print("Initial login has not yet occured - this is required to generate the credential file. Please supply login credentials (--username, --password)")
            exit(-1)
        else:
            print("Registering app")
            Mastodon.create_app(
                config['mastodon']['client_id'],
                api_base_url = config['mastodon']['base_url'],
                to_file = config['mastodon']['secret_storage'],
                scopes=["write:statuses", "admin:read:accounts"]
            )

            print("Initializing client")
            mastodon = Mastodon(
                client_id = config['mastodon']['secret_storage'],
                api_base_url  = config['mastodon']['base_url']
            )

            print("Performing login")
            mastodon.log_in(
                username = args.email,
                password = args.password,
                to_file = config['mastodon']['credential_storage'],
                scopes=["write:statuses", "admin:read:accounts"]
            )
    else:
        mastodon = Mastodon(
            access_token = config['mastodon']['credential_storage'],
            api_base_url = config['mastodon']['base_url']
        )

    assert mastodon is not None, "Mastodon client not initialized"

    connection = sqlite3.connect(config['database']['sqlite_path'])
    cursor = connection.cursor()
    
    # are our tables defined?
    fresh_database = not check_db_exists(cursor) 
    if fresh_database:
        print("Database was freshly created - we'll set all pre-existing users as of now to 'welcomed' to avoid spamming everyone on the server.")

    all_accounts = mastodon.admin_accounts(remote=False, status='active', limit=ACCOUNT_FETCH_LIMIT)
    for account in all_accounts:
        # despite status='active', we still get zombie users from the API
        if not (account.confirmed and account.approved) or account.disabled or account.suspended or account.silenced:
            continue
        
        # does our welcome bot know about this user?
        if not user_exists(cursor, account.id):
            create_user(cursor, account.id, account.username)
            connection.commit()      
        
        # have we welcomed them yet?
        if fresh_database:
            set_user_welcomed(cursor, account.id)
            connection.commit()
        
        elif not user_welcomed(cursor, account.id):
            result_id = None
            for message in config['messages']:
                result = mastodon.status_post(status=f"@{account.username}, {message.content}", in_reply_to_id=result_id, visibility='unlisted', spoiler_text=message.content_warning)
                result_id = result.id
            
            set_user_welcomed(cursor, account.id)
            connection.commit()