import sqlite3
from load_prompts import prompts
from sql_conn import sql_conn

# initialize the connection
conn, cursor = sql_conn('responses.db')

# define the question types
question_types = ['Intro', 'Ambiguous', 'Novel', 'Nonsense', 'Analogy']

# create a dictionary to store question type IDs
question_type_ids = {}

# insert question types into the database and store their IDs
for question_type in question_types:
    cursor.execute('INSERT INTO question_types (question_type) VALUES (?)', (question_type,))
    question_type_id = cursor.lastrowid
    question_type_ids[question_type] = question_type_id

conn.commit()

# define the umber of prompts per question type and exclude the intro
prompts_per_type = (len(prompts) - 1) // (len(question_types) - 1)

# insert prompts into the questions table with the appropriate question_type_id
for i, prompt in enumerate(prompts):
    if i == 0:
        question_type = 'Intro'
    else:
        question_type_index = (i - 1) // prompts_per_type + 1
        question_type = question_types[question_type_index]

    question_type_id = question_type_ids[question_type]
    cursor.execute('INSERT INTO questions (question, question_type_id) VALUES (?, ?)', (prompt, question_type_id))

conn.commit()
conn.close()

print("Questions Loaded.")
