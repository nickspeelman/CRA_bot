import random
import textwrap
from sql_conn import sql_conn

# establish database connection
conn, cursor = sql_conn('responses.db')

# define the welcome message
welcome_message = "Welcome to the scoring program! You will be presented with a question and a response given to that question. Some responses were given by humans. Some by chatbots. Your role is only to rate the response on how well you think the responder 'understood' the prompt. Don't think too hard about it. There are no 'right' and 'wrong' answers. The goal is to get your subjective opinion."

# define the list of question types to include
question_types = ['Analogy', 'Ambiguous', 'Novel']

# get the username
def get_user_name():
    print('------------------------')
    print(welcome_message)
    user_name = input("\nPlease enter your name (or type 'exit' to quit): ")
    if user_name.lower() == 'exit':
        print("Exiting program.")
        conn.close()
        exit()
    return user_name

# insret the username
def insert_scorer(user_name):
    cursor.execute('INSERT INTO scorers (scorer_name) VALUES (?)', (user_name,))
    conn.commit()
    return cursor.lastrowid

# get the questions and the responses
def get_questions_and_responses():
    cursor.execute('''
        SELECT q.question_id, q.question, r.response_id, r.response, qt.question_type
        FROM questions q
        JOIN responses r ON q.question_id = r.question_id
        JOIN question_types qt on q.question_type_id = qt.question_type_id
        WHERE qt.question_type IN ({})
    '''.format(','.join('?' for _ in question_types)), question_types)
    return cursor.fetchall()

# get the score scale
def get_score_scale():
    cursor.execute('SELECT score_id, score_weight, score_description FROM scores')
    return cursor.fetchall()

# prompt for the score
def prompt_for_scores(scorer_id, questions_and_responses, score_scale):
    random.shuffle(questions_and_responses)
    total_responses = len(questions_and_responses)

    for index, (question_id, question, response_id, response, question_type) in enumerate(questions_and_responses, start=1):
        print('------------------------')
        print(f"Response {index} of {total_responses}")
        print(f"\nQuestion:\n{textwrap.fill(question, width=80)}\n")
        print(f"Response:\n{textwrap.fill(response, width=80)}\n")

        print("Score scale:")
        for score_id, score_weight, score_description in score_scale:
            print(f"{score_weight} | {score_description}")

        while True:
            score_input = input("\nPlease enter a score (numeric value) or type 'exit' to quit: ")
            if score_input.lower() == 'exit':
                print("Exiting program.")
                conn.close()
                exit()
            try:
                score_input = int(score_input)
                valid_scores = [score_weight for _, score_weight, _ in score_scale]
                if score_input in valid_scores:
                    score_id = next(score_id for score_id, score_weight, _ in score_scale if score_weight == score_input)
                    break
                else:
                    print(f"Invalid score. Please enter one of the following values: {valid_scores}")
            except ValueError:
                print("Invalid input. Please enter a numeric value.")

        cursor.execute('INSERT INTO response_scores (scorer_id, response_id, score_id) VALUES (?, ?, ?)',
                       (scorer_id, response_id, score_id))
        conn.commit()

# do the dang thang
def main():
    user_name = get_user_name()
    scorer_id = insert_scorer(user_name)

    questions_and_responses = get_questions_and_responses()
    score_scale = get_score_scale()

    prompt_for_scores(scorer_id, questions_and_responses, score_scale)

    print("Thank you for completing the scoring!")

# do the dang thant
if __name__ == "__main__":
    main()


conn.close()
