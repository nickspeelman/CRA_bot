import os
from sql_conn import sql_conn
from log_location import logs_folder

#initialize a connection
conn, cursor = sql_conn('responses.db')



# extract the model and temperature from log
def extract_subject(file_path):
    try:
        with open(file_path, 'r', encoding='latin1') as file:
            lines = file.readlines()
            if len(lines) >= 2:
                model_line = lines[0].strip()
                temp_line = lines[1].strip()

                if model_line.startswith("Model:") and temp_line.startswith("Temperature:"):
                    model = model_line.split(': ')[1].strip()
                    temperature = temp_line.split(': ')[1].strip()
                    subject = f"{model} | {temperature}"
                    return subject
            return None
    except Exception:
        return None

# insert the subject into the subject table and return it's id
def insert_subject(subject):
    try:
        cursor.execute(r"INSERT INTO subjects (subject, subject_type) VALUES (?,'bot')", (subject,))
        conn.commit()
        return cursor.lastrowid
    except Exception:
        return None

# get the subject it
def get_subject_id(subject):
    cursor.execute('SELECT subject_id FROM subjects WHERE subject = ?', (subject,))
    result = cursor.fetchone()
    return result[0] if result else None

# get the questions from the question table
def get_question_id(question):
    cursor.execute('SELECT question_id FROM questions WHERE question = ?', (question,))
    result = cursor.fetchone()
    return result[0] if result else None

# process the log file
def process_log_file(file_path):
    try:
        with open(file_path, 'r', encoding='latin1') as file:
            lines = file.readlines()
            if len(lines) < 2:
                return

            # extract the subject
            subject = extract_subject(file_path)
            if not subject:
                return

            # get or insert the subjecid
            subject_id = get_subject_id(subject)
            if not subject_id:
                subject_id = insert_subject(subject)

            # process the file
            user_question = None
            response_lines = []
            for i in range(2, len(lines)):
                line = lines[i].strip()
                if line.startswith('user:'):
                    user_question = line[len('user:'):].strip()
                elif line.startswith('system:') and user_question:
                    response_lines.append(line[len('system:'):].strip())
                    # Collect all subsequent lines as part of the response until another question is found
                    for j in range(i + 1, len(lines)):
                        next_line = lines[j].strip()
                        if next_line.startswith('user:') or next_line.startswith('system:'):
                            break
                        response_lines.append(next_line)
                    response = ' '.join(response_lines).strip()
                    response_lines = []
                    question_id = get_question_id(user_question)
                    if question_id:
                        cursor.execute(
                            'INSERT INTO responses (subject_id, question_id, response) VALUES (?, ?, ?)',
                            (subject_id, question_id, response)
                        )
                        conn.commit()
                    user_question = None
    except Exception as e:
        print(f"Error processing file {file_path}: {e}")

# get the files in the logs directory - ignor the subfolders. those are the zoom logs
files = [f for f in os.listdir(logs_folder) if os.path.isfile(os.path.join(logs_folder, f)) and f.endswith('.txt')]

# do the dang thang
for file in files:
    file_path = os.path.join(logs_folder, file)
    process_log_file(file_path)

conn.close()

print("GPT files loaded")
