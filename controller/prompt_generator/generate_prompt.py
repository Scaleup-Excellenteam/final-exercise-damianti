# import random
#
#
# def generate_prompt(slide_text):
#     question_templates = [
#         "Can you explain the following slide text: {}?",
#         "What are the main points mentioned in the slide: {}?",
#         "Please provide a summary of the content in the slide: {}.",
#     ]
#     prompt_template = random.choice(question_templates)
#     prompt = prompt_template.format(slide_text)
#     return prompt


import random


class PromptGenerator:
    def __init__(self):
        self.question_templates = [
            "Can you explain the following slide text: {}?",
            "What are the main points mentioned in the slide: {}?",
            "Please provide a summary of the content in the slide: {}.",
        ]

    def generate_prompt(self, slide_text):
        slide_text = " ".join(slide_text).strip()
        if not slide_text:
            return ""

        prompt_template = random.choice(self.question_templates)
        prompt = prompt_template.format(slide_text)
        return prompt

if __name__ == '__main__':
    # Usage example
    generator = PromptGenerator()
    prompt = generator.generate_prompt("This is the slide text.")
    print(prompt)
