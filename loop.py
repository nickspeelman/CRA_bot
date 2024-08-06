import subprocess

# run the chat bot script
def run_script_with_inputs(model_input, temperature_input):
    process = subprocess.Popen(
        ['python', 'get_gpt_responses.py'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # pass the inputs to the script
    inputs = f"{model_input}\n{temperature_input}\n"
    stdout, stderr = process.communicate(input=inputs)
    print(stdout)
    if stderr:
        print(f"Error: {stderr}")

# define the models and temperatures lists
models = [15, 21, 24, 29]
temperatures = [0, 0.5, 1]

# initialize an empty list to store the input sets
inputs_sets = []

# iterate over each model and each temperature to create the pairs
for model in models:
    for temperature in temperatures:
        inputs_sets.append((model, temperature))

# loop through the inputs
print('Running loop for the input sets: ', inputs_sets)
for model_input, temperature_input in inputs_sets:
    print('Running get_gpt_responses for inputs :', model_input, ',', temperature_input)
    run_script_with_inputs(model_input, temperature_input)

print('All iterations complete.')