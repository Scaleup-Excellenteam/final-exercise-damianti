import random
from typing import List


class PromptGenerator:
    """
   A class used to generate prompts for GPT-3.

   Attributes:
       question_templates (list of str): A list of question templates for GPT-3 prompts.

   Methods:
       generate_prompt(slide_text: List[str]) -> str: Generates a prompt for GPT-3 based on the content of a slide.
   """
    def __init__(self):
        self.question_templates = [
            "Given the following text: {}, explain with details",
            "Write the main points and implications of this text: {}",
            "Summarize and explain the content in this text: {}",
        ]

    def generate_prompt(self, slide_text: List[str]) -> str:
        """
        Generate a prompt for GPT-3 based on the content of a slide.

        The function joins all elements in the slide_text list into a single string, then inserts this string into a
        randomly selected question template to generate the prompt.

        Args:
            slide_text (List[str]): The text contents of a PowerPoint slide.

        Returns:
            str: The generated prompt for GPT-3.
        """
        slide_text = [s for s in slide_text if s.strip()]
        slide_text = ". ".join(slide_text).strip()
        if not slide_text:
            return ""

        prompt_template = random.choice(self.question_templates)
        prompt = prompt_template.format(slide_text)

        # Replace tabs and newlines with spaces
        prompt = prompt.replace('\t', ' ').replace('\n', ' ')

        # Replace multiple spaces with a single space
        prompt = ' '.join(prompt.split())
        return prompt


if __name__ == '__main__':
    # Usage example
    generator = PromptGenerator()
    example_prompt = generator.generate_prompt(["The history of the sandwich."])
    print(example_prompt)
