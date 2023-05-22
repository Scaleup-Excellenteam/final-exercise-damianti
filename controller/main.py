
from pptx_parser_ import parser


if __name__ == '__main__':

    parsed_data = parser.parse_presentation("/Users/damiantissembaum/Documents/year_3/excellenteam/python/final-exercise/final-exercise-damianti/controller/pptx_parser_/asyncio-intro.pptx")
    for i, slide in enumerate(parsed_data):
        print(f"Slide {i + 1}:")
        print(slide)
