from pptx import Presentation


def parse_presentation(file_path = "asyncio-intro.pptx"):
    presentation = Presentation(file_path)
    slides = []
    for slide in presentation.slides:
        slide_text = []
        for shape in slide.shapes:
            if shape.has_text_frame:
                for paragraph in shape.text_frame.paragraphs:
                    for run in paragraph.runs:
                        slide_text.append(run.text)
        slides.append(slide_text)
    return slides
