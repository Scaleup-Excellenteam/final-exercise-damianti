import random


def generate_prompt(slide_text):
    question_templates = [
        "Can you explain the following slide text: {}?",
        "What are the main points mentioned in the slide: {}?",
        "Please provide a summary of the content in the slide: {}.",
    ]
    prompt_template = random.choice(question_templates)
    prompt = prompt_template.format(slide_text)
    return prompt
