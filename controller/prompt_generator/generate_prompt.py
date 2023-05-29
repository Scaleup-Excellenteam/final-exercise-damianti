import random
from typing import List

class PromptGenerator:
    def __init__(self):
        self.question_templates = [
            "Can you explain the following text: {}?",
            "What are the main points mentioned in this text: {}?",
            "Please provide a summary of the content in this text: {}.",
        ]

    def generate_prompt(self, slide_text: List[str]) -> str:
        slide_text = " ".join(slide_text).strip()
        if not slide_text:
            return ""

        prompt_template = random.choice(self.question_templates)
        prompt = prompt_template.format(slide_text)
        return prompt

if __name__ == '__main__':
    # Usage example
    generator = PromptGenerator()
    prompt = generator.generate_prompt(["This is the slide text."])
    print(prompt)
