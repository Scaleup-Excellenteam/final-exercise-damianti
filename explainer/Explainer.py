"""
Module to analyze and explain PowerPoint presentations using OpenAI's GPT-3.5.

This module provides a command-line interface (CLI) application to analyze and explain PowerPoint presentations using
 OpenAI's GPT-3.5 model. It takes a path to a PowerPoint presentation as input and generates explanations for each
 slide, saving them in a JSON file.
This module looks for pptx files in the uploads file that haven't been processed, it processes them and write the output
of the process in the output dir

Usage:
    python Explainer.py "path/to/presentation.pptx"

Functions:
    - ensure_env_file(): Ensures the existence of the environment file '.env' and its content.
    - send_prompt(prompt: str, slide_number: int) -> str: Sends a prompt to GPT-3 and returns the response.
    - gpt_explainer(presentation_path: str) -> None: Explains a PowerPoint presentation using GPT-3.5.
    - run(): Main loop to continuously process PowerPoint presentations.

Constants:
    - LOGS_DIRECTORY: The directory path for log files.
    - OUTPUTS_DIRECTORY: The directory path for output JSON files.
    - UPLOADS_DIRECTORY: The directory path for uploaded PowerPoint presentations.

Usage Example:
    python Explainer.py

    This command analyzes and explains the PowerPoint presentation located at "path/to/presentation.pptx" using GPT-3.5.

Note:
    - Before running the module, ensure that the environment file '.env' exists and contains the OpenAI API key.

Dependencies:
    - openai: The OpenAI Python library for API communication.
    - pptx_parser: Custom module for parsing PowerPoint presentations.
    - prompt_generator: Custom module for generating prompts for each slide.

"""

import time
import asyncio
import openai
import os
import json
import sys
import backoff
from dotenv import load_dotenv
from datetime import datetime
import logging.handlers

from pptx_parser.parser import parse_presentation
from prompt_generator.generate_prompt import PromptGenerator

LOGS_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), "../logs/explainer_logs"))
OUTPUTS_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), "../outputs"))
UPLOADS_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), "../uploads"))
REQUESTS_PER_MINUTE = 3

if not os.path.exists(LOGS_DIRECTORY):
    os.makedirs(LOGS_DIRECTORY)

if not os.path.exists(OUTPUTS_DIRECTORY):
    os.makedirs(OUTPUTS_DIRECTORY)

if not os.path.exists(UPLOADS_DIRECTORY):
    os.makedirs(UPLOADS_DIRECTORY)

# Configure the log file path
log_file_name = "explainer.log"
log_file_path = os.path.join(LOGS_DIRECTORY, log_file_name)

# Configure the logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

handler = logging.handlers.TimedRotatingFileHandler(log_file_path, when="D", interval=1, backupCount=5)
handler.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
logger.addHandler(handler)

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")


@backoff.on_exception(backoff.expo, openai.error.RateLimitError, max_tries=3, on_backoff=lambda _: asyncio.sleep(60))
async def send_prompt(prompt: str, slide_number: int) -> str:
    """
    Send a prompt to GPT-3 and return its response. The function is decorated with the backoff package to deal with
    exceptions: if an exception is raised, the prompt is sent again until there is no exception raised or 30 seconds
    have passed from the first try.

    Args:
        prompt (str): The prompt to send to GPT-3.
        slide_number (int): The number of the current slide.

    Returns:
        str: The response from GPT-3.
    """

    try:
        openai.api_key = api_key
        logger.info("Sending prompt...")

        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        logger.info(f"response from GPT to slide {slide_number}: {response.choices[0].message.content}")
        return f"Slide {slide_number}: {response.choices[0].message.content}"

    except Exception as e:
        logger.error(f"An error occurred while processing slide {slide_number}: {e}")
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

        if i > 0 and i % REQUESTS_PER_MINUTE == 0:
            await asyncio.sleep(60)

        logger.info(f"Processing Slide {i + 1}")
        logger.info("Slide content:")
        logger.info(slide)

        generator = PromptGenerator()

        prompt = generator.generate_prompt(slide)

        if not prompt:
            logger.info(f"Slide number {i + 1} is empty.")

        logger.info(f"prompt: {prompt}")

        task = asyncio.create_task(send_prompt(prompt, i + 1))
        tasks.append(task)
        await asyncio.sleep(2)

    # Wait for all tasks to complete
    responses = await asyncio.gather(*tasks)
    file_name = os.path.splitext(presentation_path.split('/')[-1])[0]

    # Save the explanations in a JSON file
    with open(f"{OUTPUTS_DIRECTORY}/{file_name}.json", "w") as file:
        json.dump(responses, file)


def run() -> None:
    while True:
        uploaded_files = set(os.path.splitext(file)[0] for file in os.listdir(UPLOADS_DIRECTORY))
        output_files = set(os.path.splitext(file)[0] for file in os.listdir(OUTPUTS_DIRECTORY))

        files_to_process = uploaded_files - output_files

        if files_to_process:
            file_to_process = files_to_process.pop()

            start_time = datetime.now()
            logger.info(f"\n\n\nStarting GPT explainer at {start_time}")

            try:
                file_full_path = os.path.join(UPLOADS_DIRECTORY, f'{file_to_process}.pptx')
                asyncio.run(gpt_explainer(file_full_path))
                end_time = datetime.now()
                total_time = end_time - start_time
                logger.info(f"\nGPT explainer finished at {end_time}. Total running time: {total_time}")

            except Exception as e:
                end_time = datetime.now()
                total_time = end_time - start_time
                logger.error(f"An error occurred during execution: {e}")
                logger.info(f"\nGPT explainer finished with errors at {end_time}. Total running time: {total_time}")
                sys.exit(1)

        time.sleep(10)


def main():
    run()


if __name__ == '__main__':
    main()
