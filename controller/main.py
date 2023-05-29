import logging
from pptx_parser_ import parser
from prompt_generator.generate_prompt import PromptGenerator
import asyncio
import openai
import os
import json
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(filename='game_logs.log', level=logging.INFO, format='[%(levelname)s] %(message)s')
# Load environment variables, including the API key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY_3")


async def send_prompt(prompt, slide_number):
    openai.api_key = api_key
    logging.info("Sending prompt...")

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=100,
        temperature=0.7
    )
    logging.info(f"response from gpt: {response.choices[0].text.strip()}")

    return f"Slide {slide_number}: {response.choices[0].text.strip()}"


async def gpt_explainer():

    parsed_data = parser.parse_presentation(
        "/Users/damiantissembaum/Documents/year_3/excellenteam/python/final-exercise/final-exercise-damianti/controller/pptx_parser_/asyncio-intro.pptx"
    )

    tasks = []
    for i, slide in enumerate(parsed_data):
        logging.info(f"Processing Slide {i + 1}")
        logging.info("Slide content:")
        logging.info(slide)

        generator = PromptGenerator()

        prompt = generator.generate_prompt(slide)

        if not prompt:
            logging.info(f"Slide number {i + 1} is empty.")

        logging.info("Prompt:")
        logging.info(prompt)

        task = asyncio.create_task(send_prompt(prompt, i + 1))
        tasks.append(task)
        await asyncio.sleep(1)  # Delay between API requests



    # Wait for all tasks to complete
    responses = await asyncio.gather(*tasks)

    # Save the explanations in a JSON file
    with open("explanations.json", "w") as file:
        json.dump(responses, file)


if __name__ == '__main__':
    logging.info("Starting GPT explainer...")
    asyncio.run(gpt_explainer())
    logging.info("GPT explainer finished.")
