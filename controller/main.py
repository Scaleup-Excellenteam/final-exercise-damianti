"""
Module to analyze and explain PowerPoint presentations using OpenAI's GPT-3.5.

This module is designed as a command-line interface (CLI) application. It accepts a path to a PowerPoint
presentation and outputs a JSON file with explanations for each slide. It uses OpenAI's GPT-3.5 model to generate the
explanations.

Usage:
    python main.py "path/to/presentation.pptx" --log DEBUG --output my_output --dir "path/to/output/dir"
"""

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
import argparse
import backoff

# Configure logging
logging.basicConfig(filename='program_logs.log', level=logging.INFO, format='[%(levelname)s] %(message)s')
# Load environment variables, including the API key
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")


@backoff.on_exception(backoff.expo, (openai.error.RateLimitError, Exception), max_time=30)
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

        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}])
        logging.info(f"response from gpt to slide {slide_number}: {response.choices[0].message.content}")

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


def main(path_to_presentation):
    """
    The main function of the script.

    This function handles logging and error handling for the script.

    Args:
        path_to_presentation (str): The path to the PowerPoint presentation.
    """

    start_time = datetime.now()
    logging.info(f"\n\n\nStarting GPT explainer at {start_time}")
    try:
        asyncio.run(gpt_explainer(path_to_presentation))
        end_time = datetime.now()
        total_time = end_time - start_time
        logging.info(f"\nGPT explainer finished at {end_time}. Total running time: {total_time}")

    except Exception as e:
        end_time = datetime.now()
        total_time = end_time - start_time
        logging.error(f"An error occurred during execution: {e}")
        logging.info(f"\nGPT explainer finished with errors at {end_time}. Total running time: {total_time}")
        sys.exit(1)


if __name__ == '__main__':
    """
   The entry point of the script.

   This section parses command line arguments and calls the main function with the appropriate arguments.
   """

    arg_parser = argparse.ArgumentParser(description='GPT Explainer for PowerPoint Presentations. You input the path '
                                                     'to the presentation, and the program will '
                                                     'return in a json file the explanation that chatGPT gives to '
                                                     'every slide.')

    arg_parser.add_argument('presentation_path', type=str, help='The path to the presentation file.')

    arg_parser.add_argument('--log', type=str, choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                            default='INFO', help='Set the logging level.')
    arg_parser.add_argument('--output', type=str, default=None,
                            help='Specify the output filename.')
    arg_parser.add_argument('--dir', type=str, default='./',
                            help='Specify the output directory.')
    args = arg_parser.parse_args()

    main(args.presentation_path)


