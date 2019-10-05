import os
from scanner import dupecheck
from scanner.config import DB_FILE
import sqlite3


def db_init():
    """
    Initialize the DB used to store image hash and downloaded threads
    """

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS Image_Hash
             (Hash TEXT, Thread_Number INTEGER, Date_Added INTEGER DEFAULT (strftime('%s','now')));''')
    # TRY THIS TO FIX THE DATE (datetime('now','localtime')
    c.execute('''CREATE TABLE IF NOT EXISTS Downloaded_Thread
             (Thread_Number INTEGER, Imageboard TEXT, Board TEXT, Date_Added INTEGER DEFAULT (strftime('%s','now')));''')

    conn.commit()
    conn.close()


def create_conf_dir():
    """
    Create home config directory
    """
    if not os.path.isdir(os.path.expanduser("~/.4scanner")):
        os.mkdir(os.path.expanduser("~/.4scanner"))

create_conf_dir()
db_init()
