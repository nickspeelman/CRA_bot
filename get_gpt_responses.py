from openai import OpenAI
import datetime
import os
from config import OPENAI_API_KEY
from load_prompts import prompts # loads the prompts from the script

# initialize an OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


# get the available models
def get_available_models():
    try:
        models = client.models.list() #initialize a list for my models
        #print(models)
        return [model.id for model in models.data]  # Extract Models
    except Exception as e:
        print(f"An error occurred while fetching models: {e}")
        return []

# prompt for the model and temperature
def get_model_and_temperature():
    available_models = get_available_models()

    if not available_models:
        print("No models available.")
        exit(1)

    # display the models
    print("Available models:")
    for i, model in enumerate(available_models, 1):
        print(f"{i}. {model}")

    # prompt for model selection
    model_choice = int(input("Enter the number of the model to use: ")) - 1
    model = available_models[model_choice]

    # prompt for temperature
    temperature = float(input("Enter the temperature (0 to 1): "))
    return model, temperature

# create the logs
def log_conversation(conversation, model, temperature):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = f"Logs/model_{model}_temp_{temperature}_{timestamp}.txt"
    os.makedirs(os.path.dirname(log_filename), exist_ok=True)
    with open(log_filename, 'w') as file:
        # add header details
        file.write(f"Model: {model}\n")
        file.write(f"Temperature: {temperature}\n\n")
        # log the conversation
        for message in conversation:
            file.write(f"{message['role']}: {message['content']}\n")

    # create primary log to hold all conversations
    with open("primary_gpt_log.txt", 'a') as primary_log:
        # add conversation header details
        primary_log.write(f"Conversation on {timestamp}\n")
        primary_log.write(f"Model: {model}\n")
        primary_log.write(f"Temperature: {temperature}\n\n")
        # log the conversation
        for message in conversation:
            primary_log.write(f"{message['role']}: {message['content']}\n")
        primary_log.write("\n\n")

# do the dang thang

def main():
    model, temperature = get_model_and_temperature()
    conversation = []

    print("CRA_bot is ready. Type 'exit' to end the conversation.")
    question_index = 0

    # iterate through the prompts
    while question_index < len(prompts):
        user_input = prompts[question_index]
        print(f"You: {user_input}")

        # append prompt to the conversation
        conversation.append({"role": "user", "content": user_input + "\n"})

        # get the response
        response = client.chat.completions.create(
            model=model,
            messages=conversation,
            temperature=temperature
        )

        # print and append the reply
        bot_reply = response.choices[0].message.content
        print(f"Bot: {bot_reply}")
        conversation.append({"role": "system", "content": bot_reply + "\n"})

        question_index += 1

    log_conversation(conversation, model, temperature)
    print(f"Conversation logged to file.")

if __name__ == "__main__":
    main()

