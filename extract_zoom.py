import os
import re
import random
from pathlib import Path
from sql_conn import sql_conn
from log_location import logs_folder

# set to keep track of generated hexadecimal strings
generated_hex_strings = set()

# function to generate a unique 8-digit hexadecimal string
def generate_unique_hex_string():
    while True:
        hex_string = ''.join(random.choices('0123456789abcdef', k=8))
        if hex_string not in generated_hex_strings:
            generated_hex_strings.add(hex_string)
            return hex_string

# function to anonymize names in a line, maintaining consistency within a file
def anonymize_line(line, name_mapping):
    # regex patterns to identify names
    patterns = [
        r"(\d{1,2}:\d{2}:\d{2}) From (.+?) to Everyone:",
        r"(\d{1,2}:\d{2}:\d{2}) From (.+?) to (.+?)\(direct message\):"
    ]

    for pattern in patterns:
        match = re.match(pattern, line)
        if match:
            groups = match.groups()
            time_stamp = groups[0]
            sender = groups[1]
            recipient = groups[2] if len(groups) > 2 else None

            if sender not in name_mapping and sender != "Nick Speelman":
                name_mapping[sender] = f"Human_{generate_unique_hex_string()}"
            anonymized_sender = name_mapping.get(sender, sender)

            if recipient and recipient != "Nick Speelman":
                if recipient not in name_mapping:
                    name_mapping[recipient] = f"Human_{generate_unique_hex_string()}"
                anonymized_recipient = name_mapping[recipient]
            else:
                anonymized_recipient = recipient

            if recipient:
                line = f"{time_stamp} From {anonymized_sender} to {anonymized_recipient}(direct message):\n"
            else:
                line = f"{time_stamp} From {anonymized_sender} to Everyone:\n"

            return line, anonymized_sender

    return line, None

# function to insert a subject into the subjects table and return its subject_id
def insert_subject(subject):
    cursor.execute("INSERT INTO subjects (subject,subject_type) VALUES (?,'human')", (subject,))
    conn.commit()  # ensure the subject is committed to get its ID
    return cursor.lastrowid

# function to get the subject_id from the subjects table
def get_subject_id(subject):
    cursor.execute('SELECT subject_id FROM subjects WHERE subject = ?', (subject,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return insert_subject(subject)

# function to get the question_id from the questions table
def get_question_id(question):
    cursor.execute('SELECT question_id FROM questions WHERE question = ?', (question,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        return None

conn, cursor = sql_conn('responses.db')

# process each folder and its log file in the logs directory
for root, dirs, files in os.walk(logs_folder):
    for dir_name in dirs:
        folder_path = Path(root) / dir_name
        log_files = list(folder_path.glob('*.txt'))

        if log_files:
            # extract the subject from the folder name
            subject_match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}\.\d{2}\.\d{2} (.+) - Chat', dir_name)
            if subject_match:
                subject = subject_match.group(1).strip()
            else:
                continue

            subject_id = get_subject_id(subject)

            for log_file_path in log_files:
                # change the encoding
                with open(log_file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()

                anonymized_lines = []
                name_mapping = {}

                for line in lines:
                    try:
                        new_line, anonymized_name = anonymize_line(line, name_mapping)
                        anonymized_lines.append(new_line)
                    except Exception as e:
                        pass

                # extract and insert question-response pairs
                question = None
                response_lines = []
                for i, line in enumerate(anonymized_lines):
                    # check if the line matches the timestamp pattern
                    if re.match(r"\d{1,2}:\d{2}:\d{2} From .+ to .+:", line):
                        if i + 1 < len(anonymized_lines) and anonymized_lines[i + 1].strip():
                            if question is None:
                                question = anonymized_lines[i + 1].strip()
                            else:
                                response_lines.append(anonymized_lines[i + 1].strip())
                                # collect all subsequent lines as part of the response until another question is found
                                for j in range(i + 2, len(anonymized_lines)):
                                    next_line = anonymized_lines[j].strip()
                                    if re.match(r"\d{1,2}:\d{2}:\d{2} From .+ to .+:", next_line):
                                        break
                                    response_lines.append(next_line)
                                response = ' '.join(response_lines).strip()
                                response_lines = []
                                question_id = get_question_id(question)
                                # only insert if the question_id is found
                                if question_id:
                                    cursor.execute(
                                        'INSERT INTO responses (subject_id, question_id, response) VALUES (?, ?, ?)',
                                        (subject_id, question_id, response)
                                    )
                                    conn.commit()
                                question = None  # reset for the next question-response pair

                # write the anonymized lines back to the file
                # changed encoding to utf-8
                with open(log_file_path, 'w', encoding='utf-8') as f:
                    f.writelines(anonymized_lines)

                # Read back the file to confirm changes
                with open(log_file_path, 'r', encoding='utf-8') as f:  # Changed encoding to utf-8
                    confirmed_lines = f.readlines()

                # Anonymize folder name using the anonymized name found in the log file
                if name_mapping:
                    original_dir_path = folder_path
                    anonymized_name = list(name_mapping.values())[0]  # Use the first anonymized name
                    # Updated regex to correctly match folder names
                    new_dir_name = re.sub(r'(\d{4}-\d{2}-\d{2} \d{2}\.\d{2}\.\d{2}) .+ - Chat',
                                          r'\1 ' + anonymized_name + ' - Chat', dir_name)
                    new_dir_path = Path(root) / new_dir_name
                    os.rename(original_dir_path, new_dir_path)

conn.close()

print("Zoom Files Extracted")

# combine the files into a summary
def combine_text_files_in_subdirectories(root_dir, summary_log):
    # open the summary log directory and walk through it
    with open(summary_log, 'w', encoding='utf-8') as summary_file:
        for subdir, _, files in os.walk(root_dir):
            if subdir == root_dir:
                continue

            # only process the files in the subdirectory
            for file in files:
                if file.endswith('.txt'):
                    file_path = os.path.join(subdir, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            summary_file.write(f"Contents of {file_path}:\n")
                            summary_file.write(f.read())
                            summary_file.write("\n\n")
                    except UnicodeDecodeError:
                        print(f"Error decoding {file_path}. Skipping this file.")

# define the file name
summary_log_path = 'primary_zoom_log.txt'

# Call the function to combine text files
combine_text_files_in_subdirectories(logs_folder, summary_log_path)

print('Zoom Summary Log created.')
