import os
from openai import OpenAI
from dotenv import load_dotenv
import re
import json
env_path = os.path.join(os.getcwd(), '.env')

load_dotenv(dotenv_path=env_path)
api_key = os.getenv('OPENAI_API_KEY')

if api_key:
    client = OpenAI(api_key=api_key)
else:
    raise ValueError("API Key not found. Ensure the .env file is loaded correctly.")

# The actual main process
def start():
    print("Welcome to the GPT Powered School Demo.")
    topic = input("Please enter a topic that you would like to learn about: ")
    topicSentiment = topicEvaluation(topic)
    topicSentiment = topicSentiment.split(',')

    while topicSentiment[0] == "Broad":
        topic = input(topicSentiment[1])
        topicSentiment = topicEvaluation(topic)
        topicSentiment = topicSentiment.split(',')

    level = input(f"Given {topic}, how would you say your standing is in this topic (EG: Beginner, Intermediate, Advanced, etc): ")

    print(f"Generating your {level} course on {topic}.")
    courses = course(level, topic)

    try:
        course_list = re.findall(r'"(.*?)"', courses)
        print("Courses Tailored for you: ")
        print(" ")
        x = 1
        for c in course_list:
            print(f"Course {x}: {c}")
            x=x+1
    except json.JSONDecodeError as e:
        print("Failed to decode JSON:", e)

#Evaluates the topic, to see if it needs to be narrowed down
def topicEvaluation(topic):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a system that dictates whether a topic is too broad or not to the prompt:"
                           "'Please enter a topic that you would like to learn about', and if so, generate"
                           "the followup question. Your response should be of few words, and seperated with a comma, leading"
                           "to a gentle question. "
                           "The sentiment should be based on this: Could this be taught in 10 to 12 lessons given they"
                           "already have the pre-requisites? Something like calculus,biology,civil war,grammar could be taught in 10 to 12 lessons,"
                           "but something like science,math,english,social studies is too broad to teach"
                           "Example:"
                           ""
                           "Topic = 'Math'"
                           "Response:'Broad,Is there anything specific about math you would like to learn?"
                           ""
                           "Example 2:"
                           "Topic = 'Neural Networks'"
                           "Response: Specific,Neural Networks"
                           ""
                           "Example 3:"
                           "Topic = 'Data Structures and Algorithms'"
                           "Response: Specific,Data Structures and Algorithms"
                           ""
                           "",
            },
            {"role": "user", "content": topic}
        ],
        model="gpt-4o-2024-08-06",
    )
    return (chat_completion.choices[0].message.content)

# Gets 10 to 12 courses on the topic
def course(level, topic):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a system that needs to generate names for a 10 to 12 course workflow for a student. "
                    "The courses need to be for a course at a level. The courses should be in chronological order in "
                    "which the student should learn them. EG: Entry level course first, Advanced course last. "
                    "Don't use any additional text outside of the JSON format."
                ),
            },
            {"role": "user", "content": f'Topic = {topic},Level = {level}'},
        ],
        model="gpt-4o-2024-08-06",
    )
    print (topic)
    return chat_completion.choices[0].message.content


start()

