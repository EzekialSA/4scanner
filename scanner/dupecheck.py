#!/usr/bin/env python3

import hashlib
import os
import sqlite3
from scanner.config import DB_FILE


def hash_image(img_location):
    with open(img_location, 'rb') as img:
        m = hashlib.md5()
        while True:
            data = img.read(8192)
            if not data:
                break
            m.update(data)
        return m.hexdigest()


def add_to_db(img_hash, thread_nb):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("INSERT INTO Image_Hash (hash, Thread_Number) VALUES (?,?)", (img_hash, thread_nb))

    conn.commit()
    conn.close()


def is_duplicate(img_hash):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("SELECT Hash FROM Image_Hash WHERE Hash = ?", (img_hash,))
    result = c.fetchone()

    conn.close()

    if result:
        return True
    else:
        return False
