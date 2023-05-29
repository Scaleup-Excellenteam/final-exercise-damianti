import logging
from pptx_parser_ import parser
from prompt_generator.generate_prompt import PromptGenerator
import asyncio
import openai
import os
import json
from dotenv import load_dotenv
import sys
from datetime import datetime

# Configure logging
logging.basicConfig(filename='program_logs.log', level=logging.INFO, format='[%(levelname)s] %(message)s')
# Load environment variables, including the API key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY_3")


async def send_prompt(prompt, slide_number):
    openai.api_key = api_key
    logging.info("Sending prompt...")

    response = await openai.ChatCompletion.acreate(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}])
    logging.info(f"response from gpt: {response.choices[0].message.content}")

    return f"Slide {slide_number}: {response.choices[0].message.content}"


async def gpt_explainer(presentation_path):
    parsed_data = parser.parse_presentation(presentation_path)

    tasks = []
    for i, slide in enumerate(parsed_data):
        logging.info(f"Processing Slide {i + 1}")
        logging.info("Slide content:")
        logging.info(slide)

        generator = PromptGenerator()

        prompt = generator.generate_prompt(slide)

        if not prompt:
            logging.info(f"Slide number {i + 1} is empty.")

        logging.info(f"prompt:{prompt}")

        task = asyncio.create_task(send_prompt(prompt, i + 1))
        tasks.append(task)
        await asyncio.sleep(1)  # Delay between API requests



    # Wait for all tasks to complete
    responses = await asyncio.gather(*tasks)
    file_name = presentation_path.split('/')[-1].split('.')[0]

    # Save the explanations in a JSON file
    with open(f"{file_name}.json", "w") as file:
        json.dump(responses, file)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python main.py <presentation_path>")
        sys.exit(1)

    path = sys.argv[1]
    start_time = datetime.now()
    logging.info(f"Starting GPT explainer at {start_time}")
    asyncio.run(gpt_explainer(path))
    end_time = datetime.now()
    total_time = end_time - start_time
    logging.info(f"GPT explainer finished at {end_time}. Total running time: {total_time}")
