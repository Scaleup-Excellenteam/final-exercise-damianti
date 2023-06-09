"""
Module to analyze and explain PowerPoint presentations using OpenAI's GPT-3.5.

This module is designed as a command-line interface (CLI) application. It accepts a path to a PowerPoint
presentation and outputs a JSON file with explanations for each slide. It uses OpenAI's GPT-3.5 model to generate the
explanations.

Usage:
    python main.py "path/to/presentation.pptx" --log DEBUG --output my_output --dir "path/to/output/dir"
"""
import time
import logging
import asyncio
import openai
import os
import json
import sys
import backoff
from dotenv import load_dotenv
from datetime import datetime

from pptx_parser.parser import parse_presentation
from prompt_generator.generate_prompt import PromptGenerator

LOGS_DIRECTORY = "../logs"
OUTPUTS_DIRECTORY = "../outputs"
UPLOADS_DIRECTORY = "../uploads"

if not os.path.exists(LOGS_DIRECTORY):
    os.makedirs(LOGS_DIRECTORY)

if not os.path.exists(OUTPUTS_DIRECTORY):
    os.makedirs(OUTPUTS_DIRECTORY)

if not os.path.exists(UPLOADS_DIRECTORY):
    os.makedirs(UPLOADS_DIRECTORY)

def ensure_env_file():
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write('OPENAI_API_KEY_4=\n')


logging.basicConfig(filename=f'{LOGS_DIRECTORY}/logs.log', level=logging.INFO, format='[%(levelname)s] %(message)s')
# Load environment variables, including the API key
ensure_env_file()
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY_4")


@backoff.on_exception(backoff.expo, Exception, max_tries=3, on_backoff=lambda _: asyncio.sleep(60))
async def send_prompt(prompt: str, slide_number: int) -> str:
    """
       Send a prompt to GPT-3 and return its response. Function decorated with backoff package to deal with exceptions:
       if an exceptions is raised, the prompt is sent again until there is no exception raised or 30 seconds
       passed from the first try

       Args:
           prompt (str): The prompt to send to GPT-3.
           slide_number (int): The number of the current slide.

       Returns:
           str: The response from GPT-3.
       """

    try:
        openai.api_key = api_key
        logging.info("Sending prompt...")
        logging.info("y angora...")

        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}])
        logging.info(f"response from gpt to slide {slide_number}: {response.choices[0].message.content}")
        logging.debug("in debug")
        logging.info(f'{response.choices}')
        return f"Slide {slide_number}: {response.choices[0].message.content}"

    except Exception as e:
        logging.error(f"An error occurred while processing slide {slide_number}: {e}")
        return f"Slide {slide_number}: An error occurred"


async def gpt_explainer(presentation_path: str) -> None:
    """
    Explain a PowerPoint presentation using GPT-3.5.

    This function parses the presentation, sends the contents of each slide to GPT-3.5 as a prompt,
    and collects the responses. It then outputs a JSON file with the explanations.

    Args:
        presentation_path (str): The path to the PowerPoint presentation.
    """

    parsed_data = parse_presentation(presentation_path)

    tasks = []
    for i, slide in enumerate(parsed_data):
        if i > 4:
            break

        # if i % 3 == 0 and i != 0:

        print(f'we are going to explain the slide number {i} at {datetime.now()}...')
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
        await asyncio.sleep(2)

    # Wait for all tasks to complete
    responses = await asyncio.gather(*tasks)
    file_name = os.path.splitext(presentation_path.split('/')[-1])[0]
    print (f'file name is: {file_name}')
    print(f'presentation_path is: {presentation_path}')
    # Save the explanations in a JSON file
    with open(f"{OUTPUTS_DIRECTORY}/{file_name}.json", "w") as file:
        json.dump(responses, file)


def run():
    while True:

        uploaded_files = set(os.path.splitext(file)[0] for file in os.listdir(UPLOADS_DIRECTORY))
        output_files = set(os.path.splitext(file)[0] for file in os.listdir(OUTPUTS_DIRECTORY))

        files_to_process = uploaded_files - output_files

        if files_to_process:
            file_to_process = files_to_process.pop()

            start_time = datetime.now()
            logging.info(f"\n\n\nStarting GPT explainer at {start_time}")

            try:
                file_full_path = os.path.join(UPLOADS_DIRECTORY, f'{file_to_process}.pptx')
                asyncio.run(gpt_explainer(file_full_path))
                end_time = datetime.now()
                total_time = end_time - start_time
                logging.info(f"\nGPT explainer finished at {end_time}. Total running time: {total_time}")

            except Exception as e:
                end_time = datetime.now()
                total_time = end_time - start_time
                logging.error(f"An error occurred during execution: {e}")
                logging.info(f"\nGPT explainer finished with errors at {end_time}. Total running time: {total_time}")
                sys.exit(1)

        time.sleep(20)


def main():
    run()


if __name__ == '__main__':
    main()
