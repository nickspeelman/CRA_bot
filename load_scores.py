from sql_conn import sql_conn

conn, cursor = sql_conn('responses.db')

# define the weights and descriptions
weight_descriptions = [
    (1, 'Subject demonstrates no understanding of the prompt | Total Confusion'),
    (2, 'Subject demonstrates some understanding of the prompt but not entirely | Some Confusion'),
    (3, 'Subject demonstrates a good understanding of the prompt | No Confusion'),
    (4, 'Subject demonstrates a masterful understanding of the prompt | Insightful')
]

# iterate through the list and insert into the scores table
for weight, description in weight_descriptions:
    cursor.execute(
        'INSERT INTO scores (score_weight, score_description) VALUES (?, ?)',
        (weight, description)
    )

conn.commit()
conn.close()

print('Scores loaded.')


