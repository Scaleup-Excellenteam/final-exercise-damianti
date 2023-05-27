from pptx_parser_ import parser
from prompt_generator import generate_prompt
import asyncio
import aiohttp
import openai
import os
from dotenv import load_dotenv


async def send_prompt(prompt):
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY_2")
    response = await openai.Completion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return response.choices[0].message.content


async def gpt_explainer():


    parsed_data = parser.parse_presentation(
        "/Users/damiantissembaum/Documents/year_3/excellenteam/python/final-exercise/final-exercise-damianti/controller/pptx_parser_/asyncio-intro.pptx")
    tasks = []
    for i, slide in enumerate(parsed_data):
        print(f"Slide {i + 1}:")
        print(slide)
        # Join slide text strings with a dot separator
        slide_text = ".".join(slide)

        if slide_text:
            # Generate prompt for the slide text
            prompt = generate_prompt.generate_prompt(slide_text)
            print("Prompt:", prompt)

            task = asyncio.create_task(send_prompt(prompt))
            tasks.append(task)
            await asyncio.sleep(5)
        else:
            print("Empty slide. Skipping prompt generation.")

    # Wait for all tasks to complete
    responses = await asyncio.gather(*tasks)

    # Print the responses
    for i, response in enumerate(responses):
        print(f"Response for Slide {i + 1}:")
        print(response)
        print()


if __name__ == '__main__':

    asyncio.run(gpt_explainer())
