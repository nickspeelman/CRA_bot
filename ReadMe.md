### About

This is a program used to assess ChatGPT against John Searle's Chinese Room Argument (CRA). It was compelted for my DTSC 690 Course at Eatern University.

More details about the Chinse Room Argument can be found in the included PowerPoint.

### Usage

The loop.py file will iterate through GPT models and temperature you define, and pass those to the get_gpt_responses.py file.

The get_gpt_reponses.py will iterate through the prompts defined in the scripts.txt file and save those chats to the logs folder, as well as creating a single primary log in the root folder. The logs folder here also contains logs I obtained from Zoom chats with human beings.

The load_database.py file will extract those responses and insert them into responses.db. It will also anonymize the Zoom chat files and extract that information into the database as well.

The scoring.py file runs a program that asks for humans to rate the responses obtained and write them to the db, so human and GPT responses can be compared.

The anlalysis.ipynb file contains some analysis of the data obtained.