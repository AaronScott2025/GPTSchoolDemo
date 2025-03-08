import os
from openai import OpenAI
from dotenv import load_dotenv
import csv
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
    print(courses)

    #To deal with the brackets []
    courses = courses.strip().replace('[', '').replace(']', '')

    course_list = courses.split(",")

    print("Courses Tailored for you: ")
    print(" ")
    for i, c in enumerate(course_list, start=1):
        print(f"Course {i}: {c}")

    with open('Generated Courses.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Course Number", "Course Name"])
        for i, z in enumerate(course_list):
            writer.writerow([i + 1, z])

    print(" ")
    print("Generating work for 1st course...")
    print(" ")
    headers = courseHeaders(course_list[0])
    print(f"Headers: {headers}")
    print(" ")
    headers = headers.split(",")
    content = []
    for header in headers:
        print(f"Generation Begin for {header}")
        contentgenerated = contentGen(topic,header)
        content.append(f"Header:[{header}] | Content:[{contentgenerated}]")
        print("Done")
    print(content)
    print(" ")
    print("Making it nice...")
    html = content2html(topic,content)
    with open('Generated Coursework.html', 'w', newline='') as file:
        file.write(html)
    print("Coursework Created Successfully")





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
    return chat_completion.choices[0].message.content

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
                    "Don't use any additional text outside of the Array."
                ),
            },
            {"role": "user", "content": f'Topic = {topic},Level = {level}'},
        ],
        model="gpt-4o-2024-08-06",
    )
    return chat_completion.choices[0].message.content

def courseHeaders(coursework):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a system that generates a detailed and informative coursework on the prompted course."
                    "You need to generate headers for everything that may be relevant to the prompted course. Return only"
                    "a comma separated list of course names, and no other words. These captions should be informative only, not"
                    "hands on"
                    "Example:"
                    "Input: 'Course: Introduction to punctuation'"
                    "Output:"
                    "Introduction, Periods, Commas, Semicolons, Colons, Question Marks, Exclamation Points, Quotation Marks, Apostrophes, Parentheses, Dashes, Hyphens, Ellipses, Punctuation Practice"
                )
            },
            {"role": "user", "content": f"Course: {coursework}"},  # Removed unnecessary {"text": ...}
        ],
        model="gpt-4o-2024-08-06",
    )
    return chat_completion.choices[0].message.content



def contentGen(topic,header):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a system that generates a detailed and informative coursework on the prompted course."
                    "You need to generate content for the prompted header, and the content should be 3 to 6 paragraphs long,"
                    "without generating new headers, and should vary in size depending on the requirements of the topic"
                    "Example:"
                    "Input: 'Topic: Punctuation, Header: Dashes"
                    "Output:"
                    "Dashes are versatile punctuation marks that can be used to create emphasis, add information, or connect ideas. They come in two main forms: the en dash (–) and the em dash (—). The en dash is shorter and is typically used to show ranges, such as 'pages 10–15' or 'June–August.' The em dash is longer and is often used to create a strong break in a sentence or to set off parenthetical information. Using em dashes can add a dramatic flair to your writing, making certain elements stand out. For example, 'She finally reached the summit—after hours of grueling climbing—and felt an overwhelming sense of accomplishment.' In this sentence, the em dashes emphasize the effort it took to reach the summit. Em dashes can also replace commas, parentheses, or colons, providing a more informal and dynamic feel to your writing. However, it's essential not to overuse dashes, as they can make your writing appear choppy or disjointed. Use them sparingly and purposefully to maintain clarity and coherence. When used correctly, dashes can enhance your writing by adding emphasis and variety, making your text more engaging and enjoyable to read."
                ),
            },
            {"role": "user", "content": f"Topic: {topic}, Header: {header}"},
        ],
        model="gpt-4o-2024-08-06",
    )
    return chat_completion.choices[0].message.content

def content2html(topic, content_list):
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>{topic}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 20px;
            }}
            h1 {{
                color: #333;
            }}
            h2 {{
                color: #555;
                margin-top: 30px;
            }}
            p {{
                margin: 10px 0;
            }}
        </style>
    </head>
    <body>
        <h1>{topic}</h1>
        {content_blocks}
    </body>
    </html>
    """

    content_blocks = ""
    for item in content_list:
        header_content = item.split(" | ")
        header = header_content[0].replace("Header:[", "").replace("]", "")
        content = header_content[1].replace("Content:[", "").replace("]", "")
        content_blocks += f"<h2>{header}</h2>\n<p>{content}</p>\n"

    return html_template.format(topic=topic, content_blocks=content_blocks)

start()

