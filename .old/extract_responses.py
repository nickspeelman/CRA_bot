import os
import re
import random
from pathlib import Path
from load_prompts import prompts
import subprocess
from sql_conn import sql_conn

# Disable foreign key constraints

conn, cursor = sql_conn('responses')

cursor.execute('PRAGMA foreign_keys = OFF;')

# Delete all entries from each table
tables = ['responses', 'questions', 'subjects', 'scores']

for table in tables:
    cursor.execute(f'DELETE FROM {table};')


# Load the prompts from my script into my questions table
for prompt in prompts:
    cursor.execute('INSERT INTO questions (question) VALUES (?)', (prompt,))

conn.commit()
conn.close()

subprocess.run(['python', 'extract_gpt.py'])
subprocess.run(['python', 'extract_zoom.py'])

# Clear any existing repsonses



