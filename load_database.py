
import subprocess


# run the other scripts:
subprocess.run(['python', 'clear_db.py'])
subprocess.run(['python', 'load_scores.py'])
subprocess.run(['python', 'load_questions.py'])
subprocess.run(['python', 'extract_gpt.py'])
subprocess.run(['python', 'extract_zoom.py'])


