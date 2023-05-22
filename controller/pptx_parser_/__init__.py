

# Test the parse_presentation function
if __name__ == '__main__':
    import parser

    parsed_data = parser.parse_presentation("asyncio-intro.pptx")
    for i, slide in enumerate(parsed_data):
        print(f"Slide {i + 1}:")
        print(slide)
