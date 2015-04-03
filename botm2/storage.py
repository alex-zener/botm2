import sqlite3
import os.path
from .parser import Parser



conn = sqlite3.connect('words.db')
cur = conn.cursor()

# Create tables in database
cur.execute('CREATE TABLE IF NOT EXISTS texts'+
            '(id INTEGER PRIMARY KEY,'+
            'title TEXT UNIQUE,'+
            'text TEXT);')

conn.commit()


def add_source(filename):
    parser = Parser.get_parser(filename)
    text = parser.parse()
    save_text(os.path.split(filename)[-1], text)


def save_text(name, text):
    cur.execute('INSERT INTO texts(title, text)'+
                'VALUES (?, ?)', (name, text,))
    conn.commit()


def get_source_list():
    cur.execute('SELECT * FROM texts ORDER BY id')
    return [(row[0], row[1]) for row in cur.fetchall()]


def get_text(text_ids):
    if text_ids:
        query = 'SELECT text FROM texts '+\
                'WHERE id in ({}) ORDER BY id'.\
                format(','.join(['?']*len(text_ids)))
        cur.execute(query, tuple(text_ids))
    else:
        cur.execute('SELECT text FROM texts ORDER BY id')
    text = ''
    for i in cur:
        text += i[0]
    return text.split()


def edit_source(text_id, title):
    cur.execute('UPDATE texts SET title=? WHERE id=?', (title, text_id))
    conn.commit()


def delete_source(text_id):
    cur.execute('DELETE FROM texts WHERE id=?', (text_id,))
    conn.commit()
