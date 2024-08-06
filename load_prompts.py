# Open my script
with open('script.txt', 'r') as file:
    content = file.read()

# split it into separate lines
lines = content.split('\n\n')

# clean it up
prompts = [line.strip() for line in lines]