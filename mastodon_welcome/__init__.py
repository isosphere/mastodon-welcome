from mastodon import Mastodon
import sqlite3

CLIENT_ID = 'welcome-bot'
BASE_URL = 'https://oceanplayground.social'
SECRET_STORAGE = '../pytooter_clientcred.secret'
USER_STORAGE = '../pytooter_usercred.secret'
SQLITE_LOCATION = '../database.db'

def check_db_exists(cursor: sqlite3.Cursor):
    res = cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='welcome_log'")
    if res.fetchone()[0] == 0:
        cursor.execute("CREATE TABLE welcome_log (id INTEGER PRIMARY KEY, username TEXT, userdb_id INTEGER, welcomed INTEGER DEFAULT 0)")

def check_user_exists(cursor: sqlite3.Cursor, userid: int):
    res = cursor.execute("SELECT COUNT(*) FROM welcome_log WHERE userdb_id = ?", (userid,))
    return res.fetchone()[0] > 0

def check_user_welcomed(cursor: sqlite3.Cursor, userid: int):
    res = cursor.execute("SELECT COUNT(*) FROM welcome_log WHERE userdb_id = ? AND welcomed = 1", (userid,))
    return res.fetchone()[0] > 0

def set_user_welcomed(cursor: sqlite3.Cursor, userid: int):
    cursor.execute("UPDATE welcome_log SET welcomed = 1 WHERE userdb_id = ?", (userid, ))

def create_user(cursor: sqlite3.Cursor, userid: int, username: str):
    cursor.execute("INSERT INTO welcome_log (userdb_id, username) VALUES(?, ?)", (userid, username))

WELCOME_MESSAGE = """welcome to this Atlantic Canada-local instance! 🦞

For help getting started check out https://fedi.tips

To connect with people post an #introduction with lots of hashtags! 

Follow folks from elsewhere using their _full_ username in the search bar. My full username is @welcome\u200b@oceanplayground.social

Please use the CW (content warning) for sensitive content
"""

WELCOME_MESSAGE_MORE = """
Content warnings can be used for bad poetry, political hot takes, personal topics, or whatever people should have a right to consent to before reading.

Follow @news for a local news feed (with bad news behind content warnings!), and bug @matt if you have a question or concern with this server.

Please report nasty posts.

Check the "Local" tab for posts from other people on this instance, which should be just Atlantic Canada! 🐳
"""

if __name__ == '__main__':
    # Mastodon.create_app(
    #     CLIENT_ID,
    #     api_base_url = BASE_URL,
    #     to_file = SECRET_STORAGE,
    #     scopes=["write", "admin:read"]
    # )

    # mastodon = Mastodon(
    #     client_id = SECRET_STORAGE,
    #     api_base_url = BASE_URL
    # )

    # mastodon.log_in(
    #     'USERNAME',
    #     'PASSWORD',
    #     to_file = USER_STORAGE,
    #     scopes=["write", "admin:read"]
    # )

    connection = sqlite3.connect(SQLITE_LOCATION)
    cursor = connection.cursor()
    
    # are our tables defined?
    check_db_exists(cursor)
    
    mastodon = Mastodon(
        access_token = USER_STORAGE,
        api_base_url = BASE_URL
    )

    all_accounts = mastodon.admin_accounts(remote=False, status='active')
    for account in all_accounts:
        # despite status='active', we still get zombie users from the API
        if not (account.confirmed and account.approved) or account.disabled or account.suspended or account.silenced:
            continue
        if not check_user_exists(cursor, account.id):
            create_user(cursor, account.id, account.username)
            connection.commit()      
        
        if not check_user_welcomed(cursor, account.id):
            result = mastodon.status_post(status=f"@{account.username}, {WELCOME_MESSAGE}", visibility='unlisted')
            mastodon.status_post(status=WELCOME_MESSAGE_MORE, visibility='unlisted', in_reply_to_id=result.id, spoiler_text="This is what a content warning looks like")
            set_user_welcomed(cursor, account.id)
            connection.commit()