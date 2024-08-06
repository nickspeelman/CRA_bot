from sql_conn import sql_conn


# initialize a connection
conn, cursor = sql_conn('responses.db')

# disable foreign key constraints
cursor.execute('PRAGMA foreign_keys = OFF;')

# delete all entries from each table
tables = ['responses', 'questions', 'subjects', 'scores', 'question_types','response_scores','scorers']

for table in tables:
    cursor.execute(f'DELETE FROM {table};')

conn.commit()
conn.close()

print('Old database cleared.')